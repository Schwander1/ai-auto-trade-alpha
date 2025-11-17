#!/usr/bin/env python3
"""Environment detection for dev vs production"""
import os
import socket
from pathlib import Path

def detect_environment():
    """
    Detect if running in development or production environment
    
    Returns:
        str: 'development' or 'production'
    """
    # Check explicit environment variable (highest priority)
    env = os.getenv('ARGO_ENVIRONMENT', '').lower()
    if env in ['prod', 'production']:
        return 'production'
    if env in ['dev', 'development']:
        return 'development'
    
    # Check for production path (most reliable)
    if os.path.exists('/root/argo-production/config.json'):
        return 'production'
    
    # Check hostname (production server)
    hostname = socket.gethostname()
    if 'production' in hostname.lower() or 'prod' in hostname.lower():
        return 'production'
    
    # Check if running from production directory
    cwd = Path.cwd()
    if '/root/argo-production' in str(cwd):
        return 'production'
    
    # Default to development
    return 'development'

def get_environment_info():
    """Get detailed environment information"""
    env = detect_environment()
    return {
        'environment': env,
        'hostname': socket.gethostname(),
        'cwd': str(Path.cwd()),
        'config_path_exists': os.path.exists('/root/argo-production/config.json'),
        'env_var': os.getenv('ARGO_ENVIRONMENT', 'not set')
    }

