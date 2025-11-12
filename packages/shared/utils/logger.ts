/**
 * Structured logging utilities for TypeScript/JavaScript
 * Provides consistent logging across frontend and backend
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

export interface LogContext {
  [key: string]: unknown
}

class Logger {
  private level: LogLevel = LogLevel.INFO

  setLevel(level: LogLevel): void {
    this.level = level
  }

  private log(level: LogLevel, message: string, context?: LogContext): void {
    if (level < this.level) {
      return
    }

    const timestamp = new Date().toISOString()
    const levelName = LogLevel[level]
    const logEntry = {
      timestamp,
      level: levelName,
      message,
      ...context,
    }

    // Use appropriate console method
    switch (level) {
      case LogLevel.DEBUG:
        console.debug(JSON.stringify(logEntry))
        break
      case LogLevel.INFO:
        console.info(JSON.stringify(logEntry))
        break
      case LogLevel.WARN:
        console.warn(JSON.stringify(logEntry))
        break
      case LogLevel.ERROR:
        console.error(JSON.stringify(logEntry))
        break
    }
  }

  debug(message: string, context?: LogContext): void {
    this.log(LogLevel.DEBUG, message, context)
  }

  info(message: string, context?: LogContext): void {
    this.log(LogLevel.INFO, message, context)
  }

  warn(message: string, context?: LogContext): void {
    this.log(LogLevel.WARN, message, context)
  }

  error(message: string, context?: LogContext): void {
    this.log(LogLevel.ERROR, message, context)
  }
}

// Export singleton instance
export const logger = new Logger()

// Export convenience functions
export const log = {
  debug: (message: string, context?: LogContext) => logger.debug(message, context),
  info: (message: string, context?: LogContext) => logger.info(message, context),
  warn: (message: string, context?: LogContext) => logger.warn(message, context),
  error: (message: string, context?: LogContext) => logger.error(message, context),
}

