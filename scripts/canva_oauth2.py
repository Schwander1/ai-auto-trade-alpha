#!/usr/bin/env python3
"""
Alpine Analytics - Canva OAuth 2.0 Integration
Complete OAuth 2.0 flow for Canva API
"""

import os
import json
import requests
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import secrets
import urllib.parse
import time
import hashlib
import base64

# Use Alpine's secrets manager
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "alpine-backend" / "backend"))
    from utils.secrets_manager import get_secret, get_secrets_manager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)

class CanvaOAuth2Client:
    """
    Canva OAuth 2.0 client with complete authorization flow
    """
    
    # Canva OAuth 2.0 endpoints
    AUTHORIZATION_URL = "https://www.canva.com/api/oauth/authorize"
    TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
    API_BASE = "https://api.canva.com/rest/v1"
    
    def __init__(self):
        """Initialize OAuth 2.0 client"""
        self.client_id = self._get_credential("canva-client-id")
        self.client_secret = self._get_credential("canva-client-secret")
        # For local development, use 127.0.0.1 (localhost not allowed by Canva)
        # For production, use your actual redirect URI
        self.redirect_uri = os.getenv(
            "CANVA_REDIRECT_URI",
            "http://127.0.0.1:3000/auth/canva/callback"  # Local development
        )
        
        # OAuth state for CSRF protection
        self.oauth_state: Optional[str] = None
        
        # PKCE for OAuth 2.0
        self.code_verifier: Optional[str] = None
        self.code_challenge: Optional[str] = None
        
        # Tokens
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.token_type: str = "Bearer"
        
        # Load stored tokens
        self._load_tokens()
    
    def _get_credential(self, key: str) -> Optional[str]:
        """Get credential from secrets manager or environment"""
        if SECRETS_MANAGER_AVAILABLE:
            try:
                # Try direct access with full secret name
                import boto3
                client = boto3.client('secretsmanager', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
                secret_name = f"alpine-analytics/{key}"
                try:
                    response = client.get_secret_value(SecretId=secret_name)
                    return response['SecretString']
                except client.exceptions.ResourceNotFoundException:
                    # Try with alpine-backend service path
                    secret_name = f"alpine-analytics/alpine-backend/{key}"
                    try:
                        response = client.get_secret_value(SecretId=secret_name)
                        return response['SecretString']
                    except client.exceptions.ResourceNotFoundException:
                        pass
            except Exception as e:
                logger.debug(f"Could not get {key} from secrets manager: {e}")
        
        env_key = key.upper().replace("-", "_")
        return os.getenv(env_key)
    
    def _load_tokens(self):
        """Load stored OAuth tokens"""
        token_file = Path.home() / ".alpine" / "canva_oauth_tokens.json"
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get("access_token")
                    self.refresh_token = tokens.get("refresh_token")
                    expires_in = tokens.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    self.token_type = tokens.get("token_type", "Bearer")
                    logger.info("Loaded stored OAuth tokens")
            except Exception as e:
                logger.warning(f"Could not load stored tokens: {e}")
    
    def _save_tokens(self):
        """Save OAuth tokens securely"""
        token_file = Path.home() / ".alpine" / "canva_oauth_tokens.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        
        tokens = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": int((self.token_expires_at - datetime.now()).total_seconds()) if self.token_expires_at else 3600,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(token_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        logger.debug("Saved OAuth tokens")
    
    def _save_pkce(self, state: str):
        """Save PKCE values for later use"""
        pkce_file = Path.home() / ".alpine" / "canva_pkce.json"
        pkce_file.parent.mkdir(parents=True, exist_ok=True)
        
        pkce_data = {
            "state": state,
            "code_verifier": self.code_verifier,
            "code_challenge": self.code_challenge,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(pkce_file, 'w') as f:
            json.dump(pkce_data, f, indent=2)
        logger.debug("Saved PKCE values")
    
    def _load_pkce(self, state: Optional[str] = None) -> bool:
        """Load PKCE values for a given state"""
        pkce_file = Path.home() / ".alpine" / "canva_pkce.json"
        if not pkce_file.exists():
            return False
        
        try:
            with open(pkce_file, 'r') as f:
                pkce_data = json.load(f)
            
            # If state is provided, check if it matches
            if state and pkce_data.get("state") == state:
                self.code_verifier = pkce_data.get("code_verifier")
                self.code_challenge = pkce_data.get("code_challenge")
                self.oauth_state = pkce_data.get("state")
                logger.info("Loaded PKCE values for state")
                return True
            # If no state provided, use the saved one
            elif not state:
                self.code_verifier = pkce_data.get("code_verifier")
                self.code_challenge = pkce_data.get("code_challenge")
                self.oauth_state = pkce_data.get("state")
                logger.info("Loaded PKCE values")
                return True
        except Exception as e:
            logger.warning(f"Could not load PKCE values: {e}")
        
        return False
    
    def _generate_pkce(self) -> tuple[str, str]:
        """
        Generate PKCE code verifier and challenge
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code_verifier (43-128 characters, URL-safe)
        code_verifier = secrets.token_urlsafe(32)
        
        # Generate code_challenge (SHA256 hash, base64url encoded)
        code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate OAuth 2.0 authorization URL with PKCE
        
        Args:
            state: Optional state parameter (auto-generated if not provided)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.client_id:
            raise ValueError("Canva Client ID not configured. Set CANVA_CLIENT_ID or store in AWS Secrets Manager.")
        
        # Generate state for CSRF protection
        if not state:
            self.oauth_state = secrets.token_urlsafe(32)
        else:
            self.oauth_state = state
        
        # Generate PKCE values
        self.code_verifier, self.code_challenge = self._generate_pkce()
        
        # OAuth 2.0 parameters with PKCE
        # Note: Scopes should match what's configured in Canva integration settings
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "design:content:read design:content:write design:meta:read",  # Scopes for design access
            "state": self.oauth_state,
            "code_challenge_method": "S256",
            "code_challenge": self.code_challenge,
        }
        
        # Build authorization URL
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.AUTHORIZATION_URL}?{query_string}"
        
        # Save PKCE values for later use
        self._save_pkce(self.oauth_state)
        
        return auth_url, self.oauth_state
    
    def exchange_authorization_code(
        self,
        authorization_code: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token (OAuth 2.0)
        
        Args:
            authorization_code: Authorization code from OAuth callback
            state: State parameter (for CSRF protection)
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        # Try to load PKCE values for the provided state
        if state and not self.code_verifier:
            if not self._load_pkce(state):
                raise ValueError(
                    "Code verifier not found. Make sure to call get_authorization_url() first, "
                    "or the state doesn't match a saved PKCE session."
                )
        
        # If state is provided but doesn't match stored state, warn but allow (for cases where script was restarted)
        if state and self.oauth_state and state != self.oauth_state:
            logger.warning("State parameter mismatch - proceeding anyway (script may have been restarted)")
        # If state is provided but we don't have a stored state, store it for validation
        elif state and not self.oauth_state:
            self.oauth_state = state
            logger.info("Storing provided state for validation")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Canva credentials not configured")
        
        # OAuth 2.0 token request with PKCE
        if not self.code_verifier:
            raise ValueError("Code verifier not found. Make sure to call get_authorization_url() first.")
        
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": self.code_verifier,  # PKCE requirement
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"Token exchange failed (Status {response.status_code}): {error_detail}")
            try:
                error_json = response.json()
                logger.error(f"Error details: {json.dumps(error_json, indent=2)}")
            except:
                pass
            response.raise_for_status()
        
        token_data = response.json()
        
        # Store tokens
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        self.token_type = token_data.get("token_type", "Bearer")
        
        self._save_tokens()
        logger.info("✅ Successfully authenticated with Canva OAuth 2.0")
        
        return token_data
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token (OAuth 2.0)"""
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        try:
            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            self.token_type = token_data.get("token_type", "Bearer")
            
            self._save_tokens()
            logger.info("✅ Refreshed OAuth access token")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token:
            raise ValueError(
                "Not authenticated. Run OAuth flow first:\n"
                "1. Get authorization URL: client.get_authorization_url()\n"
                "2. Visit URL and authorize\n"
                "3. Exchange code: client.exchange_authorization_code(code)"
            )
        
        # Check if token is expired or expiring soon (within 5 minutes)
        if self.token_expires_at and datetime.now() >= (self.token_expires_at - timedelta(minutes=5)):
            logger.info("Access token expired or expiring soon, refreshing...")
            if not self.refresh_access_token():
                raise ValueError(
                    "Access token expired and refresh failed. "
                    "Re-authenticate using OAuth flow."
                )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with OAuth 2.0 Bearer token"""
        self._ensure_authenticated()
        return {
            "Authorization": f"{self.token_type} {self.access_token}",
            "Content-Type": "application/json",
        }
    
    # API Methods
    def list_designs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List user's designs"""
        url = f"{self.API_BASE}/designs"
        params = {"limit": limit}
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"Failed to list designs (Status {response.status_code}): {error_detail}")
            try:
                error_json = response.json()
                logger.error(f"Error details: {json.dumps(error_json, indent=2)}")
            except:
                pass
        response.raise_for_status()
        return response.json().get("data", [])
    
    def get_design(self, design_id: str) -> Dict[str, Any]:
        """Get design details"""
        url = f"{self.API_BASE}/designs/{design_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_design_from_template(
        self,
        template_id: str,
        autofill_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create design from template with autofill"""
        url = f"{self.API_BASE}/designs"
        data = {"template_id": template_id}
        
        if autofill_data:
            data["autofill"] = autofill_data
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def export_design(
        self,
        design_id: str,
        format: str = "PNG",
        quality: str = "high"
    ) -> Dict[str, Any]:
        """Export design"""
        url = f"{self.API_BASE}/designs/{design_id}/exports"
        data = {"format": format.upper(), "quality": quality}
        
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
    
    def get_export_status(self, design_id: str, export_id: str) -> Dict[str, Any]:
        """Check export job status"""
        url = f"{self.API_BASE}/designs/{design_id}/exports/{export_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def wait_for_export(
        self,
        design_id: str,
        export_id: str,
        timeout: int = 300,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """Wait for export to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_export_status(design_id, export_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise Exception(f"Export failed: {status.get('error', 'Unknown error')}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Export timed out after {timeout} seconds")


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Alpine Analytics Canva OAuth 2.0 Integration")
    parser.add_argument("--auth", action="store_true", help="Get OAuth 2.0 authorization URL")
    parser.add_argument("--code", type=str, help="Exchange authorization code for token")
    parser.add_argument("--state", type=str, help="State parameter (from --auth)")
    parser.add_argument("--list-designs", action="store_true", help="List designs")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    client = CanvaOAuth2Client()
    
    if args.auth:
        auth_url, state = client.get_authorization_url()
        print("\n" + "="*70)
        print("🔗 OAuth 2.0 Authorization URL")
        print("="*70)
        print(f"\n{auth_url}\n")
        print("="*70)
        print(f"📋 State (save this): {state}")
        print("="*70)
        print("\n📝 Instructions:")
        print("1. Visit the URL above in your browser")
        print("2. Authorize the app")
        print("3. Copy the 'code' parameter from the redirect URL")
        print("4. Run: python3 scripts/canva_oauth2.py --code <CODE> --state <STATE>")
        print()
    
    elif args.code:
        if not args.state:
            print("❌ Error: --state parameter required for security")
            print("   Use the state value from --auth command")
            exit(1)
        
        try:
            token_data = client.exchange_authorization_code(args.code, args.state)
            print("\n✅ OAuth 2.0 Authentication Successful!")
            print(f"   Access token expires in: {token_data.get('expires_in', 3600)} seconds")
            print(f"   Token type: {token_data.get('token_type', 'Bearer')}")
            if token_data.get('refresh_token'):
                print("   ✅ Refresh token received")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")
            exit(1)
    
    elif args.list_designs:
        try:
            designs = client.list_designs()
            print(f"\n📋 Found {len(designs)} designs:")
            for design in designs[:10]:
                print(f"   • {design.get('title', 'Untitled')} ({design.get('id')})")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            exit(1)
    
    elif args.test:
        try:
            designs = client.list_designs(limit=1)
            print("\n✅ API connection successful!")
            print(f"   Authenticated and can access {len(designs)} design(s)")
        except Exception as e:
            print(f"\n❌ API test failed: {e}")
            exit(1)
    
    else:
        parser.print_help()

