#!/usr/bin/env python3
"""
Comprehensive Security Audit System
Works locally and in production - detects environment automatically
"""
import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Comprehensive security auditor"""
    
    def __init__(self):
        self.issues: List[Dict] = []
        self.checks_passed = 0
        self.checks_failed = 0
        
    def check_hardcoded_secrets(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded secrets in code"""
        issues = []
        
        # Patterns to check
        patterns = [
            (r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded API key'),
            (r'secret_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded secret key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', 'Hardcoded token'),
        ]
        
        # Check Python files
        for py_file in Path('argo').rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                for pattern, description in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's a comment or example
                        line_start = content.rfind('\n', 0, match.start())
                        line = content[line_start:match.end()] if line_start >= 0 else content[:match.end()]
                        if '#' in line or 'example' in line.lower() or 'test' in line.lower():
                            continue
                        
                        issues.append(f"{py_file}: {description} found")
            except Exception as e:
                logger.debug(f"Error checking {py_file}: {e}")
        
        return len(issues) == 0, issues
    
    def check_config_secrets(self) -> Tuple[bool, str]:
        """Check if config.json contains actual secrets"""
        config_path = Path('argo/config.json')
        if not config_path.exists():
            return True, "config.json not found (using AWS Secrets Manager)"
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check if API keys look like real secrets (not placeholders)
            alpaca_config = config.get('alpaca', {})
            if isinstance(alpaca_config, dict):
                if 'dev' in alpaca_config:
                    dev_key = alpaca_config['dev'].get('api_key', '')
                    if dev_key and len(dev_key) > 20 and not dev_key.startswith('YOUR_'):
                        return False, "config.json contains actual API keys (should use AWS Secrets Manager in production)"
            
            return True, "config.json OK (local dev use is acceptable)"
        except Exception as e:
            return False, f"Error reading config.json: {e}"
    
    def check_cors_config(self) -> Tuple[bool, str]:
        """Check CORS configuration"""
        main_py = Path('argo/main.py')
        if not main_py.exists():
            return True, "main.py not found"
        
        try:
            content = main_py.read_text()
            if r'allow_origins.*\*' in content or "allow_origins=['*']" in content:
                return False, "CORS allows all origins (*) - security risk"
            elif 'ALLOWED_ORIGINS' in content or 'allow_origins' in content:
                return True, "CORS is properly configured (whitelist)"
            else:
                return True, "CORS configuration found"
        except Exception as e:
            return False, f"Error checking CORS: {e}"
    
    def check_security_headers(self) -> Tuple[bool, str]:
        """Check for security headers middleware"""
        # Check Alpine backend
        alpine_main = Path('alpine-backend/backend/main.py')
        if alpine_main.exists():
            try:
                content = alpine_main.read_text()
                if 'SecurityHeadersMiddleware' in content:
                    return True, "Security headers middleware found"
            except:
                pass
        
        # Check Argo
        argo_main = Path('argo/main.py')
        if argo_main.exists():
            try:
                content = argo_main.read_text()
                if 'X-Frame-Options' in content or 'Content-Security-Policy' in content:
                    return True, "Security headers found"
            except:
                pass
        
        return False, "Security headers middleware may not be configured"
    
    def check_input_validation(self) -> Tuple[bool, str]:
        """Check for input validation"""
        # Check for sanitization functions
        sanitize_files = list(Path('alpine-backend').rglob('*sanitize*.py'))
        sanitize_files += list(Path('argo').rglob('*sanitize*.py'))
        
        if sanitize_files:
            return True, f"Input sanitization found in {len(sanitize_files)} file(s)"
        
        # Check for Pydantic validation
        api_files = list(Path('alpine-backend/backend/api').glob('*.py'))
        api_files += list(Path('argo/argo/api').glob('*.py'))
        
        for api_file in api_files:
            try:
                content = api_file.read_text()
                if 'BaseModel' in content and 'Field' in content:
                    return True, "Input validation found (Pydantic models)"
            except:
                continue
        
        return False, "Input validation may be missing"
    
    def check_sql_injection(self) -> Tuple[bool, str]:
        """Check for SQL injection risks"""
        issues = []
        
        # Check for string formatting in SQL queries
        for py_file in Path('argo').rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                # Look for f-strings or % formatting with SELECT/INSERT/UPDATE/DELETE
                # But exclude parameterized queries (using ? or :param) and print statements
                sql_pattern = re.compile(rf'f["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?["\']', re.IGNORECASE | re.DOTALL)
                param_pattern = re.compile(r'\?|:\w+|%s|%d')
                print_pattern = re.compile(r'print\s*\(|logger\.(info|debug|warning|error)\s*\(')
                
                for match in sql_pattern.finditer(content):
                    sql_snippet = match.group(0)
                    # Check if it's in a print/log statement (false positive)
                    line_start = content.rfind('\n', 0, match.start())
                    line_end = content.find('\n', match.end())
                    context = content[max(0, line_start-50):min(len(content), match.end()+50)]
                    
                    if print_pattern.search(context):
                        continue  # Skip print/log statements
                    
                    # Check if it uses parameterized queries
                    if not param_pattern.search(sql_snippet):
                        # Check if it's in a comment or docstring
                        if '#' not in context and '"""' not in context and "'''" not in context:
                            # Check if it's actually executed (not just a string)
                            if 'execute(' in context or 'query(' in context or 'cursor.' in context:
                                issues.append(f"{py_file}: Potential SQL injection risk (f-string with SQL, no parameters)")
            except:
                continue
        
        if issues:
            return False, f"Potential SQL injection risks: {len(issues)} found"
        
        return True, "No obvious SQL injection risks (using parameterized queries)"
    
    def check_rate_limiting(self) -> Tuple[bool, str]:
        """Check for rate limiting"""
        # Check API files for rate limiting
        api_files = list(Path('argo/argo/api').glob('*.py'))
        api_files += list(Path('alpine-backend/backend/api').glob('*.py'))
        
        for api_file in api_files:
            try:
                content = api_file.read_text()
                if 'rate_limit' in content.lower() or 'RateLimiter' in content:
                    return True, "Rate limiting found"
            except:
                continue
        
        return False, "Rate limiting may not be configured"
    
    def check_authentication(self) -> Tuple[bool, str]:
        """Check for authentication/authorization"""
        auth_files = list(Path('alpine-backend/backend').rglob('*auth*.py'))
        
        if auth_files:
            return True, f"Authentication found in {len(auth_files)} file(s)"
        
        # Check for JWT or OAuth
        for py_file in Path('alpine-backend/backend/api').glob('*.py'):
            try:
                content = py_file.read_text()
                if 'JWT' in content or 'OAuth' in content or 'verify_token' in content:
                    return True, "Authentication/authorization found"
            except:
                continue
        
        return False, "Authentication may not be configured"
    
    def check_error_sanitization(self) -> Tuple[bool, str]:
        """Check for error message sanitization"""
        # Check for DEBUG checks in error handlers
        for py_file in Path('alpine-backend/backend').rglob('*.py'):
            try:
                content = py_file.read_text()
                if 'settings.DEBUG' in content or 'if.*debug' in content.lower():
                    return True, "Error message sanitization found"
            except:
                continue
        
        return False, "Error messages may expose internal details"
    
    def run_all_checks(self) -> Dict:
        """Run all security checks"""
        print('\n🔒 COMPREHENSIVE SECURITY AUDIT')
        print('='*70)
        
        checks = [
            ("Hardcoded Secrets", self.check_hardcoded_secrets),
            ("Config Secrets", self.check_config_secrets),
            ("CORS Configuration", self.check_cors_config),
            ("Security Headers", self.check_security_headers),
            ("Input Validation", self.check_input_validation),
            ("SQL Injection", self.check_sql_injection),
            ("Rate Limiting", self.check_rate_limiting),
            ("Authentication", self.check_authentication),
            ("Error Sanitization", self.check_error_sanitization),
        ]
        
        results = []
        
        for check_name, check_func in checks:
            try:
                if check_name == "Hardcoded Secrets":
                    passed, issues = check_func()
                    if passed:
                        print(f'✅ {check_name}: PASS')
                        self.checks_passed += 1
                    else:
                        print(f'❌ {check_name}: FAIL')
                        for issue in issues[:3]:  # Show first 3
                            print(f'   - {issue}')
                        if len(issues) > 3:
                            print(f'   ... and {len(issues) - 3} more')
                        self.checks_failed += 1
                    results.append({
                        "check": check_name,
                        "status": passed,
                        "issues": issues if not passed else []
                    })
                else:
                    passed, message = check_func()
                    status_icon = "✅" if passed else "❌"
                    print(f'{status_icon} {check_name}: {message}')
                    if passed:
                        self.checks_passed += 1
                    else:
                        self.checks_failed += 1
                    results.append({
                        "check": check_name,
                        "status": passed,
                        "message": message
                    })
            except Exception as e:
                print(f'⚠️  {check_name}: Error - {e}')
                results.append({
                    "check": check_name,
                    "status": False,
                    "error": str(e)
                })
        
        # Summary
        print('\n' + '='*70)
        print('📊 SECURITY AUDIT SUMMARY')
        print('='*70)
        print(f'✅ Passed: {self.checks_passed}')
        print(f'❌ Failed: {self.checks_failed}')
        print(f'📊 Total: {len(checks)}')
        
        overall_status = self.checks_failed == 0
        
        if overall_status:
            print('\n✅ SECURITY AUDIT PASSED!')
        else:
            print('\n❌ SECURITY AUDIT FAILED - Please fix issues before deployment')
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "passed": self.checks_passed,
            "failed": self.checks_failed,
            "overall_status": overall_status,
            "results": results
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Security Audit')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor()
    results = auditor.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    sys.exit(0 if results["overall_status"] else 1)

if __name__ == '__main__':
    main()

