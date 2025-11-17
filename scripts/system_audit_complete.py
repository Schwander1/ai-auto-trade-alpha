#!/usr/bin/env python3
"""
Complete System Audit
Generates comprehensive system audit report
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemAuditor:
    """Complete system auditor"""
    
    def __init__(self):
        self.audit_results: Dict = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "dependencies": {},
            "configuration": {},
            "security": {},
            "performance": {},
            "recommendations": []
        }
        
    def audit_components(self) -> Dict:
        """Audit system components"""
        components = {
            "argo": {
                "exists": Path("argo").exists(),
                "main_py": Path("argo/main.py").exists(),
                "config_json": Path("argo/config.json").exists(),
                "requirements_txt": Path("argo/requirements.txt").exists(),
            },
            "alpine_backend": {
                "exists": Path("alpine-backend").exists(),
                "main_py": Path("alpine-backend/backend/main.py").exists(),
            },
            "alpine_frontend": {
                "exists": Path("alpine-frontend").exists(),
                "package_json": Path("alpine-frontend/package.json").exists(),
            },
            "scripts": {
                "deploy_argo": Path("scripts/deploy-argo.sh").exists(),
                "deploy_alpine": Path("scripts/deploy-alpine.sh").exists(),
                "health_check": Path("scripts/health-check.sh").exists(),
            }
        }
        
        return components
    
    def audit_dependencies(self) -> Dict:
        """Audit dependencies"""
        dependencies = {}
        
        # Check Python dependencies
        if Path("argo/requirements.txt").exists():
            try:
                with open("argo/requirements.txt") as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                dependencies["argo_python"] = {
                    "count": len(deps),
                    "packages": deps[:10]  # First 10
                }
            except:
                pass
        
        # Check Node dependencies
        if Path("alpine-frontend/package.json").exists():
            try:
                with open("alpine-frontend/package.json") as f:
                    pkg = json.load(f)
                    deps = list(pkg.get("dependencies", {}).keys())
                dependencies["alpine_frontend"] = {
                    "count": len(deps),
                    "packages": deps[:10]
                }
            except:
                pass
        
        return dependencies
    
    def audit_configuration(self) -> Dict:
        """Audit configuration"""
        config = {}
        
        # Check config.json
        if Path("argo/config.json").exists():
            try:
                with open("argo/config.json") as f:
                    cfg = json.load(f)
                config["argo"] = {
                    "has_trading": "trading" in cfg,
                    "has_strategy": "strategy" in cfg,
                    "has_alpaca": "alpaca" in cfg,
                    "has_backtest": "backtest" in cfg,
                }
            except:
                pass
        
        # Check environment detection
        try:
            sys.path.insert(0, str(Path("argo")))
            from argo.core.environment import detect_environment
            env = detect_environment()
            config["environment"] = env
        except:
            config["environment"] = "unknown"
        
        return config
    
    def audit_security(self) -> Dict:
        """Audit security status"""
        security = {}
        
        # Check for .deployignore
        security["deployignore_exists"] = Path(".deployignore").exists()
        
        # Check for deployment manifest
        security["deployment_manifest_exists"] = Path("scripts/deployment-manifest.json").exists()
        
        # Check for security scripts
        security["security_audit_script"] = Path("scripts/security_audit_complete.py").exists()
        security["local_security_audit"] = Path("scripts/local_security_audit.sh").exists()
        
        return security
    
    def audit_performance(self) -> Dict:
        """Audit performance-related files"""
        performance = {}
        
        # Check for backtesting framework
        performance["backtesting_framework"] = Path("argo/argo/backtest").exists()
        
        # Check for health checks
        performance["health_check_unified"] = Path("argo/scripts/health_check_unified.py").exists()
        performance["local_health_check"] = Path("scripts/local_health_check.sh").exists()
        
        # Check for monitoring
        performance["monitoring_scripts"] = len(list(Path("argo/scripts").glob("*monitor*.py"))) > 0
        
        return performance
    
    def generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Check components
        components = self.audit_components()
        if not components["argo"]["exists"]:
            recommendations.append("Argo directory not found")
        
        # Check security
        security = self.audit_security()
        if not security.get("deployignore_exists"):
            recommendations.append("Create .deployignore file for deployment exclusions")
        
        # Check backtesting
        performance = self.audit_performance()
        if not performance.get("backtesting_framework"):
            recommendations.append("Backtesting framework not found")
        
        return recommendations
    
    def run_audit(self) -> Dict:
        """Run complete system audit"""
        print('\n📊 COMPLETE SYSTEM AUDIT')
        print('='*70)
        
        print('\n1️⃣  Component Audit...')
        self.audit_results["components"] = self.audit_components()
        print(f'   Components found: {sum(1 for c in self.audit_results["components"].values() if isinstance(c, dict) and c.get("exists"))}')
        
        print('\n2️⃣  Dependency Audit...')
        self.audit_results["dependencies"] = self.audit_dependencies()
        total_deps = sum(d.get("count", 0) for d in self.audit_results["dependencies"].values())
        print(f'   Total dependencies: {total_deps}')
        
        print('\n3️⃣  Configuration Audit...')
        self.audit_results["configuration"] = self.audit_configuration()
        print(f'   Environment: {self.audit_results["configuration"].get("environment", "unknown")}')
        
        print('\n4️⃣  Security Audit...')
        self.audit_results["security"] = self.audit_security()
        security_items = sum(1 for v in self.audit_results["security"].values() if v)
        print(f'   Security items: {security_items}/{len(self.audit_results["security"])}')
        
        print('\n5️⃣  Performance Audit...')
        self.audit_results["performance"] = self.audit_performance()
        perf_items = sum(1 for v in self.audit_results["performance"].values() if v)
        print(f'   Performance items: {perf_items}/{len(self.audit_results["performance"])}')
        
        print('\n6️⃣  Recommendations...')
        self.audit_results["recommendations"] = self.generate_recommendations()
        print(f'   Recommendations: {len(self.audit_results["recommendations"])}')
        for rec in self.audit_results["recommendations"]:
            print(f'   - {rec}')
        
        # Summary
        print('\n' + '='*70)
        print('📊 AUDIT SUMMARY')
        print('='*70)
        print(f'Components: {len(self.audit_results["components"])}')
        print(f'Dependencies: {len(self.audit_results["dependencies"])}')
        print(f'Configuration: {len(self.audit_results["configuration"])}')
        print(f'Security: {len(self.audit_results["security"])}')
        print(f'Performance: {len(self.audit_results["performance"])}')
        print(f'Recommendations: {len(self.audit_results["recommendations"])}')
        
        return self.audit_results

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete System Audit')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    auditor = SystemAuditor()
    results = auditor.run_audit()
    
    if args.json or args.output:
        output = json.dumps(results, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f'\n✅ Audit report saved to: {args.output}')
        else:
            print(output)
    
    sys.exit(0)

if __name__ == '__main__':
    main()

