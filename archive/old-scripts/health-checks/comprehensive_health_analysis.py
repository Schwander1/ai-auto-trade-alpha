#!/usr/bin/env python3
"""
Comprehensive Health Check Analysis
Analyzes all health endpoints, identifies gaps, and finds optimization opportunities
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class HealthEndpoint:
    """Represents a health check endpoint"""
    path: str
    method: str
    service: str
    file_path: str
    line_number: int
    checks: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

@dataclass
class ServiceAnalysis:
    """Analysis of a service's health checks"""
    service_name: str
    endpoints: List[HealthEndpoint] = field(default_factory=list)
    missing_checks: List[str] = field(default_factory=list)
    missing_metrics: List[str] = field(default_factory=list)
    router_registration: bool = False
    issues: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)

class HealthCheckAnalyzer:
    """Comprehensive health check analyzer"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.services: Dict[str, ServiceAnalysis] = {}
        self.all_endpoints: List[HealthEndpoint] = []
        
    def analyze(self) -> Dict:
        """Run comprehensive analysis"""
        print("🔍 Starting comprehensive health check analysis...")
        
        # Analyze Argo service
        self._analyze_argo()
        
        # Analyze Alpine Backend service
        self._analyze_alpine_backend()
        
        # Analyze Alpine Frontend
        self._analyze_alpine_frontend()
        
        # Find gaps
        gaps = self._find_gaps()
        
        # Find opportunities
        opportunities = self._find_opportunities()
        
        # Generate report
        return {
            "services": {name: self._service_to_dict(svc) for name, svc in self.services.items()},
            "gaps": gaps,
            "opportunities": opportunities,
            "summary": self._generate_summary()
        }
    
    def _analyze_argo(self):
        """Analyze Argo service health checks"""
        print("  📊 Analyzing Argo service...")
        service = ServiceAnalysis(service_name="Argo")
        
        # Check main.py
        main_py = self.workspace_root / "argo" / "main.py"
        if main_py.exists():
            self._analyze_file(main_py, service, "Argo")
        
        # Check health.py router
        health_py = self.workspace_root / "argo" / "argo" / "api" / "health.py"
        if health_py.exists():
            self._analyze_health_router(health_py, service, "Argo")
        
        # Check server.py (legacy)
        server_py = self.workspace_root / "argo" / "argo" / "api" / "server.py"
        if server_py.exists():
            self._analyze_file(server_py, service, "Argo")
        
        # Check router registration
        if main_py.exists():
            content = main_py.read_text()
            service.router_registration = "health.router" in content or "include_router(health" in content
        
        self.services["Argo"] = service
    
    def _analyze_alpine_backend(self):
        """Analyze Alpine Backend service health checks"""
        print("  📊 Analyzing Alpine Backend service...")
        service = ServiceAnalysis(service_name="Alpine Backend")
        
        # Check main.py
        main_py = self.workspace_root / "alpine-backend" / "backend" / "main.py"
        if main_py.exists():
            self._analyze_file(main_py, service, "Alpine Backend")
        
        # Check for health router (might not exist)
        health_router = self.workspace_root / "alpine-backend" / "backend" / "api" / "health.py"
        if health_router.exists():
            self._analyze_health_router(health_router, service, "Alpine Backend")
        
        self.services["Alpine Backend"] = service
    
    def _analyze_alpine_frontend(self):
        """Analyze Alpine Frontend health checks"""
        print("  📊 Analyzing Alpine Frontend...")
        service = ServiceAnalysis(service_name="Alpine Frontend")
        
        # Check API client
        api_ts = self.workspace_root / "alpine-frontend" / "lib" / "api.ts"
        if api_ts.exists():
            content = api_ts.read_text()
            if "checkApiHealth" in content:
                endpoint = HealthEndpoint(
                    path="/health",
                    method="GET",
                    service="Alpine Frontend",
                    file_path=str(api_ts.relative_to(self.workspace_root)),
                    line_number=self._find_line_number(content, "checkApiHealth")
                )
                endpoint.checks = ["API connectivity"]
                service.endpoints.append(endpoint)
                self.all_endpoints.append(endpoint)
        
        self.services["Alpine Frontend"] = service
    
    def _analyze_file(self, file_path: Path, service: ServiceAnalysis, service_name: str):
        """Analyze a Python file for health endpoints"""
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Find @app.get("/health") or similar
        for i, line in enumerate(lines, 1):
            if re.search(r'@app\.(get|post)\(["\']/health', line):
                # Find the function definition
                func_line = i
                for j in range(i, min(i + 20, len(lines))):
                    if 'async def' in lines[j] or 'def ' in lines[j]:
                        func_line = j + 1
                        break
                
                endpoint = HealthEndpoint(
                    path="/health",
                    method="GET",
                    service=service_name,
                    file_path=str(file_path.relative_to(self.workspace_root)),
                    line_number=func_line
                )
                
                # Extract checks from function body
                func_body = '\n'.join(lines[func_line-1:min(func_line+100, len(lines))])
                endpoint.checks = self._extract_checks(func_body)
                endpoint.dependencies = self._extract_dependencies(func_body)
                endpoint.metrics = self._extract_metrics(func_body)
                endpoint.issues = self._analyze_endpoint_issues(endpoint, func_body)
                
                service.endpoints.append(endpoint)
                self.all_endpoints.append(endpoint)
            
            # Check for /metrics endpoint
            if re.search(r'@app\.(get|post)\(["\']/metrics', line):
                func_line = i
                for j in range(i, min(i + 20, len(lines))):
                    if 'async def' in lines[j] or 'def ' in lines[j]:
                        func_line = j + 1
                        break
                
                endpoint = HealthEndpoint(
                    path="/metrics",
                    method="GET",
                    service=service_name,
                    file_path=str(file_path.relative_to(self.workspace_root)),
                    line_number=func_line
                )
                
                func_body = '\n'.join(lines[func_line-1:min(func_line+50, len(lines))])
                endpoint.metrics = self._extract_metrics(func_body)
                
                service.endpoints.append(endpoint)
                self.all_endpoints.append(endpoint)
    
    def _analyze_health_router(self, file_path: Path, service: ServiceAnalysis, service_name: str):
        """Analyze a health router file"""
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Find router prefix
        prefix = "/api/v1/health"
        for line in lines:
            if 'prefix=' in line and 'health' in line.lower():
                match = re.search(r'prefix=["\']([^"\']+)["\']', line)
                if match:
                    prefix = match.group(1)
        
        # Find all router endpoints
        for i, line in enumerate(lines, 1):
            if re.search(r'@router\.(get|post)\(', line):
                # Extract path
                path_match = re.search(r'@router\.(get|post)\(["\']([^"\']*)["\']', line)
                if path_match:
                    method = path_match.group(1).upper()
                    path_suffix = path_match.group(2)
                    full_path = f"{prefix}{path_suffix}" if path_suffix else prefix
                    
                    # Find function
                    func_line = i
                    for j in range(i, min(i + 20, len(lines))):
                        if 'async def' in lines[j] or 'def ' in lines[j]:
                            func_line = j + 1
                            break
                    
                    endpoint = HealthEndpoint(
                        path=full_path,
                        method=method,
                        service=service_name,
                        file_path=str(file_path.relative_to(self.workspace_root)),
                        line_number=func_line
                    )
                    
                    func_body = '\n'.join(lines[func_line-1:min(func_line+150, len(lines))])
                    endpoint.checks = self._extract_checks(func_body)
                    endpoint.dependencies = self._extract_dependencies(func_body)
                    endpoint.metrics = self._extract_metrics(func_body)
                    endpoint.issues = self._analyze_endpoint_issues(endpoint, func_body)
                    
                    service.endpoints.append(endpoint)
                    self.all_endpoints.append(endpoint)
    
    def _extract_checks(self, func_body: str) -> List[str]:
        """Extract health checks from function body"""
        checks = []
        
        # Database checks
        if re.search(r'db\.(execute|query)', func_body, re.IGNORECASE):
            checks.append("Database connectivity")
        if 'SELECT 1' in func_body or 'SELECT 1' in func_body:
            checks.append("Database query")
        
        # Redis checks
        if 'redis' in func_body.lower() and ('ping' in func_body.lower() or 'get' in func_body.lower()):
            checks.append("Redis connectivity")
        
        # Secrets manager checks
        if 'secrets' in func_body.lower() and ('manager' in func_body.lower() or 'get_secret' in func_body):
            checks.append("Secrets manager")
        
        # Data source checks
        if 'data_source' in func_body.lower() or 'data_sources' in func_body.lower():
            checks.append("Data sources")
        
        # Performance metrics
        if 'performance' in func_body.lower() and 'metrics' in func_body.lower():
            checks.append("Performance metrics")
        
        # System metrics
        if 'psutil' in func_body or 'cpu_percent' in func_body or 'memory_percent' in func_body:
            checks.append("System metrics (CPU, Memory, Disk)")
        
        return checks
    
    def _extract_dependencies(self, func_body: str) -> List[str]:
        """Extract dependencies from function body"""
        dependencies = []
        
        if 'database' in func_body.lower() or 'db' in func_body.lower() or 'sqlalchemy' in func_body.lower():
            dependencies.append("Database")
        if 'redis' in func_body.lower():
            dependencies.append("Redis")
        if 'secrets' in func_body.lower():
            dependencies.append("Secrets Manager")
        if 'data_source' in func_body.lower():
            dependencies.append("Data Sources")
        
        return list(set(dependencies))
    
    def _extract_metrics(self, func_body: str) -> List[str]:
        """Extract metrics from function body"""
        metrics = []
        
        if 'prometheus' in func_body.lower():
            metrics.append("Prometheus metrics")
        if 'uptime' in func_body.lower():
            metrics.append("Uptime")
        if 'cpu' in func_body.lower() or 'memory' in func_body.lower():
            metrics.append("System resources")
        if 'win_rate' in func_body.lower() or 'signals_generated' in func_body.lower():
            metrics.append("Trading metrics")
        
        return metrics
    
    def _analyze_endpoint_issues(self, endpoint: HealthEndpoint, func_body: str) -> List[str]:
        """Analyze endpoint for issues"""
        issues = []
        
        # Check for error handling
        if 'try:' not in func_body and 'except' not in func_body:
            issues.append("No error handling - may crash on failures")
        
        # Check for timeout
        if 'timeout' not in func_body.lower():
            issues.append("No timeout specified - may hang indefinitely")
        
        # Check for response structure
        if endpoint.path == "/health" and 'status' not in func_body.lower():
            issues.append("Health endpoint may not return standard status field")
        
        # Check for logging
        if 'logger' not in func_body and 'logging' not in func_body:
            issues.append("No logging - failures may go unnoticed")
        
        return issues
    
    def _find_gaps(self) -> Dict[str, List[str]]:
        """Find gaps in health check coverage"""
        gaps = defaultdict(list)
        
        # Standard checks that should be present
        standard_checks = [
            "Database connectivity",
            "Redis connectivity",
            "System metrics (CPU, Memory, Disk)",
            "Uptime tracking",
            "Error rate monitoring"
        ]
        
        for service_name, service in self.services.items():
            all_checks = set()
            for endpoint in service.endpoints:
                all_checks.update(endpoint.checks)
            
            for check in standard_checks:
                if check not in all_checks:
                    gaps[service_name].append(f"Missing: {check}")
        
        # Check for router registration
        for service_name, service in self.services.items():
            if not service.router_registration and any(e.path.startswith("/api/") for e in service.endpoints):
                gaps[service_name].append("Health router may not be registered in main app")
        
        # Check for frontend health checks
        if "Alpine Frontend" in self.services:
            frontend = self.services["Alpine Frontend"]
            if not frontend.endpoints:
                gaps["Alpine Frontend"].append("No frontend health check endpoint")
        
        return dict(gaps)
    
    def _find_opportunities(self) -> Dict[str, List[str]]:
        """Find optimization opportunities"""
        opportunities = defaultdict(list)
        
        for service_name, service in self.services.items():
            # Check for duplicate endpoints
            paths = [e.path for e in service.endpoints]
            duplicates = [p for p in set(paths) if paths.count(p) > 1]
            if duplicates:
                opportunities[service_name].append(f"Duplicate endpoints: {', '.join(duplicates)} - consider consolidating")
            
            # Check for comprehensive health endpoint
            has_comprehensive = any(
                len(e.checks) >= 3 and len(e.dependencies) >= 2 
                for e in service.endpoints 
                if e.path == "/health" or "/health" in e.path
            )
            if not has_comprehensive and service.endpoints:
                opportunities[service_name].append("Health endpoint could be more comprehensive - add more dependency checks")
            
            # Check for metrics endpoint
            has_metrics = any("/metrics" in e.path for e in service.endpoints)
            if not has_metrics:
                opportunities[service_name].append("Missing /metrics endpoint for Prometheus monitoring")
            
            # Check for readiness vs liveness
            has_readiness = any("readiness" in e.path.lower() for e in service.endpoints)
            has_liveness = any("liveness" in e.path.lower() for e in service.endpoints)
            if not has_readiness or not has_liveness:
                opportunities[service_name].append("Consider separate /health/readiness and /health/liveness endpoints for Kubernetes")
            
            # Check for structured response
            for endpoint in service.endpoints:
                if endpoint.path == "/health" and endpoint.issues:
                    opportunities[service_name].extend([f"{endpoint.path}: {issue}" for issue in endpoint.issues])
        
        return dict(opportunities)
    
    def _find_line_number(self, content: str, search_term: str) -> int:
        """Find line number of search term"""
        for i, line in enumerate(content.split('\n'), 1):
            if search_term in line:
                return i
        return 0
    
    def _service_to_dict(self, service: ServiceAnalysis) -> Dict:
        """Convert service analysis to dict"""
        return {
            "service_name": service.service_name,
            "endpoints": [
                {
                    "path": e.path,
                    "method": e.method,
                    "file": e.file_path,
                    "line": e.line_number,
                    "checks": e.checks,
                    "dependencies": e.dependencies,
                    "metrics": e.metrics,
                    "issues": e.issues
                }
                for e in service.endpoints
            ],
            "router_registered": service.router_registration,
            "total_endpoints": len(service.endpoints)
        }
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_endpoints = sum(len(s.endpoints) for s in self.services.values())
        total_checks = sum(len(e.checks) for s in self.services.values() for e in s.endpoints)
        total_issues = sum(len(e.issues) for s in self.services.values() for e in s.endpoints)
        
        return {
            "total_services": len(self.services),
            "total_endpoints": total_endpoints,
            "total_health_checks": total_checks,
            "total_issues_found": total_issues,
            "services_analyzed": list(self.services.keys())
        }

def main():
    """Main entry point"""
    workspace_root = Path(__file__).parent.parent
    analyzer = HealthCheckAnalyzer(workspace_root)
    
    print("=" * 60)
    print("COMPREHENSIVE HEALTH CHECK ANALYSIS")
    print("=" * 60)
    print()
    
    results = analyzer.analyze()
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = results["summary"]
    print(f"Services Analyzed: {summary['total_services']}")
    print(f"Total Endpoints: {summary['total_endpoints']}")
    print(f"Total Health Checks: {summary['total_health_checks']}")
    print(f"Issues Found: {summary['total_issues_found']}")
    
    # Print gaps
    print("\n" + "=" * 60)
    print("GAPS IDENTIFIED")
    print("=" * 60)
    if results["gaps"]:
        for service, gaps in results["gaps"].items():
            print(f"\n{service}:")
            for gap in gaps:
                print(f"  ⚠️  {gap}")
    else:
        print("✅ No major gaps identified")
    
    # Print opportunities
    print("\n" + "=" * 60)
    print("OPTIMIZATION OPPORTUNITIES")
    print("=" * 60)
    if results["opportunities"]:
        for service, opps in results["opportunities"].items():
            print(f"\n{service}:")
            for opp in opps:
                print(f"  💡 {opp}")
    else:
        print("✅ No optimization opportunities identified")
    
    # Save detailed report
    report_file = workspace_root / "HEALTH_CHECK_ANALYSIS_REPORT.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

