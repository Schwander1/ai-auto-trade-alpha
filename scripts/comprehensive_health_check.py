#!/usr/bin/env python3
"""
Comprehensive Health Check System
Performs thorough health checks across all components of the Argo-Alpine platform
"""
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import traceback

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: str  # 'pass', 'fail', 'warning', 'skip'
    message: str = ""
    details: Dict = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class ComprehensiveHealthChecker:
    """Comprehensive health checker for the entire platform"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.results: List[HealthCheckResult] = []
        self.start_time = datetime.utcnow()

    def check_python_imports(self) -> HealthCheckResult:
        """Check if critical Python modules can be imported"""
        failed_imports = []
        successful_imports = []

        critical_modules = [
            ("argo.core.signal_generation_service", "SignalGenerationService"),
            ("argo.core.paper_trading_engine", "PaperTradingEngine"),
            ("argo.core.database", "get_db_connection"),
            ("backend.core.database", "get_db"),
            ("backend.core.cache", "redis_client"),
        ]

        for module_path, item_name in critical_modules:
            try:
                # Try to import
                spec = importlib.util.find_spec(module_path)
                if spec is None:
                    failed_imports.append(f"{module_path} (module not found)")
                    continue

                module = importlib.import_module(module_path)
                if hasattr(module, item_name):
                    successful_imports.append(f"{module_path}.{item_name}")
                else:
                    failed_imports.append(f"{module_path}.{item_name} (not found in module)")
            except Exception as e:
                failed_imports.append(f"{module_path}.{item_name} ({str(e)})")

        if failed_imports:
            return HealthCheckResult(
                "Python Imports",
                "fail" if len(failed_imports) > len(successful_imports) else "warning",
                f"{len(successful_imports)}/{len(critical_modules)} imports successful",
                {"successful": successful_imports, "failed": failed_imports}
            )
        else:
            return HealthCheckResult(
                "Python Imports",
                "pass",
                f"All {len(successful_imports)} critical imports successful",
                {"successful": successful_imports}
            )

    def check_file_structure(self) -> HealthCheckResult:
        """Check critical files and directories exist"""
        critical_paths = [
            "argo/argo/api/health.py",
            "argo/argo/core/signal_generation_service.py",
            "alpine-backend/backend/main.py",
            "alpine-backend/backend/api/signals.py",
            "alpine-frontend/app/api/health/route.ts",
            "package.json",
            "pnpm-workspace.yaml",
        ]

        missing = []
        present = []

        for path_str in critical_paths:
            path = self.workspace_root / path_str
            if path.exists():
                present.append(path_str)
            else:
                missing.append(path_str)

        if missing:
            return HealthCheckResult(
                "File Structure",
                "warning" if len(missing) < len(critical_paths) / 2 else "fail",
                f"{len(present)}/{len(critical_paths)} critical files present",
                {"present": present, "missing": missing}
            )
        else:
            return HealthCheckResult(
                "File Structure",
                "pass",
                f"All {len(present)} critical files present",
                {"present": present}
            )

    def check_configuration_files(self) -> HealthCheckResult:
        """Check configuration files are valid JSON"""
        config_files = [
            "package.json",
            "pnpm-workspace.yaml",
        ]

        # Also check for argo config if it exists
        argo_configs = [
            "argo/config.json",
            "config.json",
        ]

        valid = []
        invalid = []
        missing = []

        for config_file in config_files:
            path = self.workspace_root / config_file
            if not path.exists():
                missing.append(config_file)
                continue

            try:
                if config_file.endswith('.json'):
                    with open(path) as f:
                        json.load(f)
                valid.append(config_file)
            except json.JSONDecodeError as e:
                invalid.append(f"{config_file}: {str(e)}")

        # Check argo configs (optional)
        for config_file in argo_configs:
            path = self.workspace_root / config_file
            if path.exists():
                try:
                    with open(path) as f:
                        json.load(f)
                    valid.append(config_file)
                except json.JSONDecodeError as e:
                    invalid.append(f"{config_file}: {str(e)}")

        if invalid:
            return HealthCheckResult(
                "Configuration Files",
                "fail",
                f"{len(valid)} valid, {len(invalid)} invalid",
                {"valid": valid, "invalid": invalid, "missing": missing}
            )
        elif missing:
            return HealthCheckResult(
                "Configuration Files",
                "warning",
                f"{len(valid)} valid, {len(missing)} missing (optional)",
                {"valid": valid, "missing": missing}
            )
        else:
            return HealthCheckResult(
                "Configuration Files",
                "pass",
                f"All {len(valid)} configuration files valid",
                {"valid": valid}
            )

    def check_database_connectivity(self) -> HealthCheckResult:
        """Check database connectivity"""
        results = {}

        # Check Argo SQLite database
        try:
            db_path = self.workspace_root / "argo" / "data" / "signals.db"
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM signals")
                count = cursor.fetchone()[0]
                conn.close()
                results["argo_sqlite"] = {
                    "status": "healthy",
                    "signal_count": count,
                    "path": str(db_path)
                }
            else:
                results["argo_sqlite"] = {
                    "status": "warning",
                    "message": "Database file not found (will be created on first use)"
                }
        except Exception as e:
            results["argo_sqlite"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check Alpine Backend database (PostgreSQL - may not be accessible locally)
        try:
            # Try to import and check connection
            sys.path.insert(0, str(self.workspace_root / "alpine-backend"))
            from backend.core.database import get_engine
            engine = get_engine()
            if engine:
                results["alpine_postgres"] = {
                    "status": "checkable",
                    "message": "Database engine available (connection not tested)"
                }
            else:
                results["alpine_postgres"] = {
                    "status": "warning",
                    "message": "Database engine not configured"
                }
        except Exception as e:
            results["alpine_postgres"] = {
                "status": "skip",
                "message": f"Cannot check (likely not configured locally): {str(e)}"
            }

        # Determine overall status
        statuses = [r.get("status") for r in results.values()]
        if "unhealthy" in statuses:
            overall = "fail"
        elif "warning" in statuses and "healthy" not in statuses:
            overall = "warning"
        elif "healthy" in statuses:
            overall = "pass"
        else:
            overall = "skip"

        return HealthCheckResult(
            "Database Connectivity",
            overall,
            f"Checked {len(results)} databases",
            results
        )

    def check_health_endpoints(self) -> HealthCheckResult:
        """Check health endpoint implementations"""
        endpoints = {}

        # Check Argo health endpoint
        argo_health = self.workspace_root / "argo" / "argo" / "api" / "health.py"
        if argo_health.exists():
            content = argo_health.read_text()
            has_timeout = "timeout" in content.lower() or "wait_for" in content
            has_error_handling = "try:" in content and "except" in content
            has_database_check = "database" in content.lower() or "sqlite" in content.lower()

            endpoints["argo"] = {
                "exists": True,
                "has_timeout": has_timeout,
                "has_error_handling": has_error_handling,
                "has_database_check": has_database_check,
                "issues": []
            }

            if not has_timeout:
                endpoints["argo"]["issues"].append("No timeout handling")
            if not has_error_handling:
                endpoints["argo"]["issues"].append("No error handling")
            if not has_database_check:
                endpoints["argo"]["issues"].append("No database check")
        else:
            endpoints["argo"] = {"exists": False}

        # Check Alpine Backend health endpoint
        alpine_health = self.workspace_root / "alpine-backend" / "backend" / "main.py"
        if alpine_health.exists():
            content = alpine_health.read_text()
            has_health = "/health" in content
            has_timeout = "timeout" in content.lower() or "wait_for" in content
            has_error_handling = "try:" in content and "except" in content

            endpoints["alpine_backend"] = {
                "exists": has_health,
                "has_timeout": has_timeout,
                "has_error_handling": has_error_handling,
                "issues": []
            }

            if has_health:
                if not has_timeout:
                    endpoints["alpine_backend"]["issues"].append("No timeout handling")
                if not has_error_handling:
                    endpoints["alpine_backend"]["issues"].append("No error handling")
        else:
            endpoints["alpine_backend"] = {"exists": False}

        # Check Alpine Frontend health endpoint
        frontend_health = self.workspace_root / "alpine-frontend" / "app" / "api" / "health" / "route.ts"
        if frontend_health.exists():
            endpoints["alpine_frontend"] = {"exists": True}
        else:
            endpoints["alpine_frontend"] = {"exists": False, "issues": ["Health endpoint missing"]}

        # Determine overall status
        all_exist = all(e.get("exists", False) for e in endpoints.values())
        all_issues = [issue for e in endpoints.values() for issue in e.get("issues", [])]

        if not all_exist:
            overall = "warning"
        elif all_issues:
            overall = "warning"
        else:
            overall = "pass"

        return HealthCheckResult(
            "Health Endpoints",
            overall,
            f"{sum(1 for e in endpoints.values() if e.get('exists'))}/{len(endpoints)} endpoints exist",
            {"endpoints": endpoints, "total_issues": len(all_issues)}
        )

    def check_dependencies(self) -> HealthCheckResult:
        """Check if dependencies are installed"""
        # Check Python dependencies
        python_deps = ["fastapi", "sqlalchemy", "pydantic", "redis"]
        python_status = {}

        for dep in python_deps:
            try:
                __import__(dep)
                python_status[dep] = "installed"
            except ImportError:
                python_status[dep] = "missing"

        # Check Node.js dependencies (if package.json exists)
        node_status = {}
        package_json = self.workspace_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                node_status["package.json"] = "exists"

                # Check if node_modules exists
                node_modules = self.workspace_root / "node_modules"
                if node_modules.exists():
                    node_status["node_modules"] = "exists"
                else:
                    node_status["node_modules"] = "missing"
            except Exception as e:
                node_status["error"] = str(e)
        else:
            node_status["package.json"] = "missing"

        python_missing = sum(1 for v in python_status.values() if v == "missing")
        node_issues = "missing" in node_status.values()

        if python_missing > 0:
            overall = "fail" if python_missing > len(python_deps) / 2 else "warning"
        elif node_issues:
            overall = "warning"
        else:
            overall = "pass"

        return HealthCheckResult(
            "Dependencies",
            overall,
            f"Python: {len(python_deps) - python_missing}/{len(python_deps)} installed",
            {"python": python_status, "node": node_status}
        )

    def check_linting(self) -> HealthCheckResult:
        """Check for linting errors"""
        # Try to run linting on key files
        lint_results = {}

        # Check Python files with flake8 if available
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                # Run flake8 on a sample of files
                test_files = [
                    "argo/argo/api/health.py",
                    "alpine-backend/backend/main.py",
                ]

                for test_file in test_files:
                    path = self.workspace_root / test_file
                    if path.exists():
                        result = subprocess.run(
                            ["python", "-m", "flake8", str(path), "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"],
                            capture_output=True,
                            timeout=10
                        )
                        lint_results[test_file] = {
                            "status": "pass" if result.returncode == 0 else "warning",
                            "errors": result.stdout.decode() if result.returncode != 0 else None
                        }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            lint_results["flake8"] = {"status": "skip", "message": "flake8 not available"}

        # Check TypeScript/JavaScript files with ESLint if available
        try:
            result = subprocess.run(
                ["npx", "eslint", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                lint_results["eslint"] = {"status": "available", "message": "ESLint available"}
            else:
                lint_results["eslint"] = {"status": "skip", "message": "ESLint not available"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            lint_results["eslint"] = {"status": "skip", "message": "ESLint not available"}

        # Determine overall status
        if any(r.get("status") == "warning" for r in lint_results.values()):
            overall = "warning"
        elif all(r.get("status") in ["pass", "skip"] for r in lint_results.values()):
            overall = "pass"
        else:
            overall = "skip"

        return HealthCheckResult(
            "Linting",
            overall,
            f"Checked {len(lint_results)} linting tools",
            lint_results
        )

    def check_git_status(self) -> HealthCheckResult:
        """Check git repository status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                changes = result.stdout.decode().strip().split('\n')
                changes = [c for c in changes if c]

                modified = [c for c in changes if c.startswith(' M')]
                untracked = [c for c in changes if c.startswith('??')]

                return HealthCheckResult(
                    "Git Status",
                    "warning" if changes else "pass",
                    f"{len(modified)} modified, {len(untracked)} untracked files",
                    {
                        "modified_count": len(modified),
                        "untracked_count": len(untracked),
                        "total_changes": len(changes)
                    }
                )
            else:
                return HealthCheckResult(
                    "Git Status",
                    "skip",
                    "Not a git repository or git not available"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return HealthCheckResult(
                "Git Status",
                "skip",
                "Git not available"
            )

    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            status = "pass"
            issues = []

            if cpu_percent > 90:
                status = "warning"
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")

            if memory.percent > 90:
                status = "warning"
                issues.append(f"High memory usage: {memory.percent:.1f}%")

            if disk.percent > 90:
                status = "warning"
                issues.append(f"High disk usage: {disk.percent:.1f}%")

            return HealthCheckResult(
                "System Resources",
                status,
                f"CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%, Disk: {disk.percent:.1f}%",
                {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "issues": issues
                }
            )
        except ImportError:
            return HealthCheckResult(
                "System Resources",
                "skip",
                "psutil not available",
                {"message": "Install psutil to check system resources"}
            )

    def check_service_endpoints(self) -> HealthCheckResult:
        """Check if service endpoints are accessible (if services are running)"""
        endpoints_to_check = [
            ("Argo API", "http://localhost:8000/api/v1/health"),
            ("Alpine Backend", "http://localhost:9001/health"),
        ]

        results = {}

        try:
            import requests
        except ImportError:
            return HealthCheckResult(
                "Service Endpoints",
                "skip",
                "requests library not available",
                {"message": "Install requests to check service endpoints"}
            )

        for name, url in endpoints_to_check:
            try:
                response = requests.get(url, timeout=2)
                results[name] = {
                    "status": "reachable",
                    "http_status": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            except requests.exceptions.RequestException as e:
                results[name] = {
                    "status": "unreachable",
                    "error": str(e),
                    "note": "Service may not be running (this is OK for local checks)"
                }

        reachable = sum(1 for r in results.values() if r.get("status") == "reachable")

        return HealthCheckResult(
            "Service Endpoints",
            "skip" if reachable == 0 else ("pass" if reachable == len(endpoints_to_check) else "warning"),
            f"{reachable}/{len(endpoints_to_check)} services reachable",
            results
        )

    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print("=" * 80)
        print("COMPREHENSIVE HEALTH CHECK")
        print("=" * 80)
        print(f"Workspace: {self.workspace_root}")
        print(f"Started: {self.start_time.isoformat()}")
        print("=" * 80)
        print()

        # Run all checks
        checks = [
            ("File Structure", self.check_file_structure),
            ("Configuration Files", self.check_configuration_files),
            ("Python Imports", self.check_python_imports),
            ("Dependencies", self.check_dependencies),
            ("Database Connectivity", self.check_database_connectivity),
            ("Health Endpoints", self.check_health_endpoints),
            ("Linting", self.check_linting),
            ("Git Status", self.check_git_status),
            ("System Resources", self.check_system_resources),
            ("Service Endpoints", self.check_service_endpoints),
        ]

        for name, check_func in checks:
            try:
                print(f"Checking {name}...", end=" ", flush=True)
                result = check_func()
                self.results.append(result)

                status_icon = {
                    "pass": "✅",
                    "fail": "❌",
                    "warning": "⚠️",
                    "skip": "⏭️"
                }.get(result.status, "❓")

                print(f"{status_icon} {result.status.upper()}")
                if result.message:
                    print(f"   {result.message}")
            except Exception as e:
                error_result = HealthCheckResult(
                    name,
                    "fail",
                    f"Check failed with exception: {str(e)}",
                    error=traceback.format_exc()
                )
                self.results.append(error_result)
                print(f"❌ FAIL (Exception: {str(e)})")

        # Generate summary
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()

        summary = self._generate_summary()

        # Print summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Checks: {len(self.results)}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"Duration: {duration:.2f}s")
        print("=" * 80)

        # Print failed checks
        failed = [r for r in self.results if r.status == "fail"]
        if failed:
            print()
            print("FAILED CHECKS:")
            print("-" * 80)
            for result in failed:
                print(f"❌ {result.name}: {result.message}")
                if result.error:
                    print(f"   Error: {result.error[:200]}...")

        # Print warnings
        warnings = [r for r in self.results if r.status == "warning"]
        if warnings:
            print()
            print("WARNINGS:")
            print("-" * 80)
            for result in warnings:
                print(f"⚠️  {result.name}: {result.message}")

        return {
            "workspace": str(self.workspace_root),
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": summary,
            "results": [asdict(r) for r in self.results]
        }

    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        return {
            "passed": sum(1 for r in self.results if r.status == "pass"),
            "failed": sum(1 for r in self.results if r.status == "fail"),
            "warnings": sum(1 for r in self.results if r.status == "warning"),
            "skipped": sum(1 for r in self.results if r.status == "skip"),
            "total": len(self.results)
        }

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive Health Check System')
    parser.add_argument('--workspace', type=str, default=None,
                       help='Workspace root directory (default: script parent directory)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--output', type=str, default=None,
                       help='Save results to file')

    args = parser.parse_args()

    if args.workspace:
        workspace_root = Path(args.workspace)
    else:
        workspace_root = Path(__file__).parent.parent

    if not workspace_root.exists():
        print(f"Error: Workspace directory does not exist: {workspace_root}")
        return 1

    checker = ComprehensiveHealthChecker(workspace_root)
    results = checker.run_all_checks()

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {output_path}")

    # Output JSON if requested
    if args.json:
        print()
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    summary = results["summary"]
    if summary["failed"] > 0:
        return 1
    elif summary["warnings"] > 0:
        return 0  # Warnings are OK
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())
