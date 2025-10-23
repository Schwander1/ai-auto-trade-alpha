import boto3
import json

def get_secret(secret_name, region='us-west-2'):
    """
    Retrieve secret from AWS Secrets Manager

    Args:
        secret_name: Name of the secret (e.g., 'alpaca-paper-trading')
        region: AWS region

    Returns:
        dict: Parsed secret JSON
    """
    client = boto3.client('secretsmanager', region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except client.exceptions.ResourceNotFoundException:
        raise RuntimeError(f"Secret '{secret_name}' not found in AWS Secrets Manager")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")
