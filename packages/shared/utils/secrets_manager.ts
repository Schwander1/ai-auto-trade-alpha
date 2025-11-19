/**
 * AWS Secrets Manager utility for TypeScript/Node.js
 * Provides caching, fallback to environment variables, and error handling
 */

import { SecretsManagerClient, GetSecretValueCommand, PutSecretValueCommand, CreateSecretCommand } from '@aws-sdk/client-secrets-manager';

interface CacheEntry {
  value: unknown;
  timestamp: number;
}

interface SecretsManagerOptions {
  region?: string;
  cacheTtl?: number; // in milliseconds
  fallbackToEnv?: boolean;
  secretPrefix?: string;
}

/**
 * AWS Secrets Manager client with caching and fallback support
 */
export class SecretsManager {
  private client: SecretsManagerClient | null = null;
  private cache: Map<string, CacheEntry> = new Map();
  private cacheTtl: number;
  private fallbackToEnv: boolean;
  private secretPrefix: string;
  private region: string;

  constructor(options: SecretsManagerOptions = {}) {
    this.region = options.region || process.env.AWS_DEFAULT_REGION || 'us-east-1';
    this.cacheTtl = (options.cacheTtl || 300) * 1000; // Convert to milliseconds
    this.fallbackToEnv = options.fallbackToEnv !== false;
    this.secretPrefix = options.secretPrefix || 'argo-alpine';

    // Initialize AWS client if credentials are available
    // Note: AWS SDK v3 uses credential provider chain automatically
    // It will try: environment variables, shared credentials file, IAM roles, etc.
    try {
      this.client = new SecretsManagerClient({
        region: this.region,
        // Let AWS SDK handle credentials automatically via default provider chain
      });
      // Only log if we successfully created the client
      // Actual credential validation happens on first API call
      console.log(`AWS Secrets Manager client created (region: ${this.region})`);
    } catch (error) {
      console.warn('Failed to create AWS Secrets Manager client:', error);
      if (!this.fallbackToEnv) {
        throw error;
      }
    }
  }

  private getSecretName(key: string, service?: string): string {
    if (service) {
      return `${this.secretPrefix}/${service}/${key}`;
    }
    return `${this.secretPrefix}/${key}`;
  }

  private isCacheValid(secretName: string): boolean {
    const entry = this.cache.get(secretName);
    if (!entry) {
      return false;
    }
    return Date.now() - entry.timestamp < this.cacheTtl;
  }

  private getFromCache(secretName: string): unknown | null {
    if (this.isCacheValid(secretName)) {
      const entry = this.cache.get(secretName);
      console.debug(`Cache hit for secret: ${secretName}`);
      return entry?.value;
    }
    return null;
  }

  private setCache(secretName: string, value: unknown): void {
    this.cache.set(secretName, {
      value,
      timestamp: Date.now(),
    });
  }

  private async getFromAws(secretName: string): Promise<string | null> {
    if (!this.client) {
      return null;
    }

    try {
      const command = new GetSecretValueCommand({ SecretId: secretName });
      const response = await this.client.send(command);

      if (response.SecretString) {
        return response.SecretString;
      }

      if (response.SecretBinary) {
        const buff = Buffer.from(response.SecretBinary);
        return buff.toString('utf-8');
      }

      return null;
    } catch (error: unknown) {
      // Handle AWS SDK errors
      if (error && typeof error === 'object' && 'name' in error) {
        const errorName = error.name as string;
        if (errorName === 'ResourceNotFoundException') {
          console.debug(`Secret not found: ${secretName}`);
        } else if (errorName === 'InvalidRequestException') {
          console.error(`Invalid request for secret ${secretName}:`, error);
        } else if (errorName === 'InvalidParameterException') {
          console.error(`Invalid parameter for secret ${secretName}:`, error);
        } else if (errorName === 'DecryptionFailureException') {
          console.error(`Failed to decrypt secret ${secretName}:`, error);
        } else if (errorName === 'InternalServiceErrorException') {
          console.error(`AWS internal error for secret ${secretName}:`, error);
        } else if (errorName === 'AccessDeniedException') {
          console.error(`Access denied for secret ${secretName}:`, error);
        } else {
          console.error(`Error retrieving secret ${secretName}:`, error);
        }
      } else {
        console.error(`Unexpected error retrieving secret ${secretName}:`, error);
      }
      return null;
    }
  }

  private getFromEnv(key: string): string | undefined {
    const envKey = key.toUpperCase().replace(/-/g, '_');
    const value = process.env[envKey];
    if (value) {
      console.debug(`Retrieved ${key} from environment variable`);
    }
    return value;
  }

  /**
   * Get secret value with caching and fallback
   */
  async getSecret(
    key: string,
    options: {
      service?: string;
      default?: string;
      required?: boolean;
      parseJson?: boolean;
    } = {}
  ): Promise<unknown> {
    const { service, default: defaultValue, required = false, parseJson = false } = options;
    const secretName = this.getSecretName(key, service);

    // Try cache first
    const cachedValue = this.getFromCache(secretName);
    if (cachedValue !== null) {
      return cachedValue;
    }

    // Try AWS Secrets Manager with current prefix
    let awsValue = await this.getFromAws(secretName);

    // Backward compatibility: Try old "argo-alpine" prefix if current prefix fails
    if (!awsValue && this.secretPrefix !== 'argo-alpine' && service) {
      const oldSecretName = `argo-alpine/${service}/${key}`;
      console.debug(`Trying backward-compatible secret name: ${oldSecretName}`);
      awsValue = await this.getFromAws(oldSecretName);
      if (awsValue) {
        console.info(`Found secret with old prefix (argo-alpine), consider migrating to new prefix (${this.secretPrefix})`);
      }
    }

    if (awsValue) {
      try {
        const value = parseJson ? JSON.parse(awsValue) : awsValue;
        this.setCache(secretName, value);
        console.debug(`Retrieved ${secretName} from AWS Secrets Manager`);
        return value;
      } catch (error) {
        console.error(`Failed to parse JSON secret: ${secretName}`, error);
        if (required) {
          throw new Error(`Invalid JSON in secret: ${secretName}`);
        }
      }
    }

    // Fallback to environment variable
    if (this.fallbackToEnv) {
      const envValue = this.getFromEnv(key);
      if (envValue) {
        try {
          const value = parseJson ? JSON.parse(envValue) : envValue;
          this.setCache(secretName, value);
          return value;
        } catch (error) {
          console.warn(`Failed to parse JSON from env var ${key}`);
        }
      }
    }

    // Use default or throw error
    if (defaultValue !== undefined) {
      console.debug(`Using default value for ${secretName}`);
      return defaultValue;
    }

    if (required) {
      throw new Error(
        `Required secret not found: ${secretName} ` +
        `(checked AWS Secrets Manager and environment variables)`
      );
    }

    return null;
  }

  /**
   * Get multiple secrets as an object
   */
  async getSecretsDict(
    keys: string[],
    service?: string,
    parseJson: boolean = false
  ): Promise<Record<string, unknown>> {
    const result: Record<string, unknown> = {};
    for (const key of keys) {
      result[key] = await this.getSecret(key, { service, parseJson });
    }
    return result;
  }

  /**
   * Set secret in AWS Secrets Manager
   */
  async setSecret(
    key: string,
    value: unknown,
    service?: string,
    description?: string
  ): Promise<boolean> {
    if (!this.client) {
      console.error('AWS client not available - cannot set secret');
      return false;
    }

    const secretName = this.getSecretName(key, service);
    const secretString = typeof value === 'string' ? value : JSON.stringify(value);

    try {
      // Try to get existing secret
      try {
        await this.client.send(new GetSecretValueCommand({ SecretId: secretName }));
        // Secret exists - update it
        await this.client.send(
          new PutSecretValueCommand({
            SecretId: secretName,
            SecretString: secretString,
          })
        );
        console.log(`Updated secret: ${secretName}`);
      } catch (error: unknown) {
        // Handle AWS SDK errors
        if (error && typeof error === 'object' && 'name' in error) {
          const errorName = error.name as string;
          if (errorName === 'ResourceNotFoundException') {
            // Secret doesn't exist - create it
            const params: {
              Name: string;
              SecretString: string;
              Description?: string;
            } = {
              Name: secretName,
              SecretString: secretString,
            };
            if (description) {
              params.Description = description;
            }
            try {
              await this.client.send(new CreateSecretCommand(params));
              console.log(`Created secret: ${secretName}`);
            } catch (createError: unknown) {
              // Handle case where secret was created between check and create
              if (createError && typeof createError === 'object' && 'name' in createError) {
                const createErrorName = createError.name as string;
                if (createErrorName === 'ResourceExistsException') {
                  // Secret exists - update it
                  await this.client.send(
                    new PutSecretValueCommand({
                      SecretId: secretName,
                      SecretString: secretString,
                    })
                  );
                  console.log(`Updated secret: ${secretName}`);
                } else {
                  throw createError;
                }
              } else {
                throw createError;
              }
            }
          } else if (errorName === 'AccessDeniedException') {
            // Don't have permission to check - try to create directly
            try {
              const params: {
                Name: string;
                SecretString: string;
                Description?: string;
              } = {
                Name: secretName,
                SecretString: secretString,
              };
              if (description) {
                params.Description = description;
              }
              await this.client.send(new CreateSecretCommand(params));
              console.log(`Created secret: ${secretName}`);
            } catch (createError: unknown) {
              if (createError && typeof createError === 'object' && 'name' in createError) {
                const createErrorName = createError.name as string;
                if (createErrorName === 'ResourceExistsException') {
                  // Secret exists - update it
                  await this.client.send(
                    new PutSecretValueCommand({
                      SecretId: secretName,
                      SecretString: secretString,
                    })
                  );
                  console.log(`Updated secret: ${secretName}`);
                } else {
                  throw createError;
                }
              } else {
                throw createError;
              }
            }
          } else {
            throw error;
          }
        } else {
          throw error;
        }
      }

      // Invalidate cache
      this.cache.delete(secretName);
      return true;
    } catch (error) {
      console.error(`Failed to set secret ${secretName}:`, error);
      return false;
    }
  }

  /**
   * Clear the in-memory cache
   */
  clearCache(): void {
    this.cache.clear();
    console.debug('Secrets cache cleared');
  }
}

// Global instance
let globalSecretsManager: SecretsManager | null = null;

/**
 * Get or create global SecretsManager instance
 */
export function getSecretsManager(options?: SecretsManagerOptions): SecretsManager {
  if (!globalSecretsManager) {
    globalSecretsManager = new SecretsManager(options);
  }
  return globalSecretsManager;
}

/**
 * Convenience function to get a secret
 */
export async function getSecret(
  key: string,
  options: {
    service?: string;
    default?: string;
    required?: boolean;
    parseJson?: boolean;
  } = {}
): Promise<unknown> {
  return getSecretsManager().getSecret(key, options);
}
