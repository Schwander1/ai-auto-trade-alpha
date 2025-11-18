#!/usr/bin/env python3
"""
Comprehensive Production Debugging Script
Performs extensive debugging checks on all production services
"""
import sys
import json
import subprocess
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import traceback

# Try to import psutil, but handle gracefully if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'

class ProductionDebugger:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
        self.metrics = {}
        self.start_time = time.time()
        
    def print_header(self, text: str):
        print(f"\n{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.NC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.NC}\n")
    
    def print_section(self, text: str):
        print(f"\n{Colors.BLUE}{'-'*80}{Colors.NC}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.NC}")
        print(f"{Colors.BLUE}{'-'*80}{Colors.NC}\n")
    
    def success(self, msg: str):
        print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")
        self.info.append(("SUCCESS", msg))
    
    def error(self, msg: str):
        print(f"{Colors.RED}❌ {msg}{Colors.NC}")
        self.issues.append(msg)
    
    def warning(self, msg: str):
        print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")
        self.warnings.append(msg)
    
    def info_msg(self, msg: str):
        print(f"{Colors.CYAN}ℹ️  {msg}{Colors.NC}")
        self.info.append(("INFO", msg))
    
    def run_command(self, cmd: str, capture_output: bool = True) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip() if capture_output else ""
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_docker_containers(self):
        """Check all Docker containers status"""
        self.print_section("1. DOCKER CONTAINERS STATUS")
        
        # Check if Docker is running
        docker_running, _ = self.run_command("docker ps > /dev/null 2>&1")
        if not docker_running:
            self.error("Docker daemon is not running")
            return
        
        self.success("Docker daemon is running")
        
        # Get all containers
        success, output = self.run_command("docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'")
        if not success:
            self.error(f"Failed to list containers: {output}")
            return
        
        containers = {}
        for line in output.split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[0]
                    status = parts[1]
                    ports = parts[2] if len(parts) > 2 else ""
                    containers[name] = {"status": status, "ports": ports}
        
        # Check production containers (with flexible matching)
        production_containers = [
            "alpine-backend-1", "alpine-backend-2", "alpine-backend-3",
            "alpine-frontend-1", "alpine-frontend-2",
            "alpine-postgres", "alpine-redis",
            "alpine-prometheus", "alpine-grafana",
            "alpine-node-exporter", "alpine-postgres-exporter", "alpine-redis-exporter"
        ]
        
        # Also check for local variants
        local_containers = [
            "alpine-postgres-local", "alpine-redis-local",
            "argo-postgres", "argo-redis", "argo-grafana", "argo-clickhouse"
        ]
        
        all_containers_to_check = production_containers + local_containers
        
        running_count = 0
        stopped_count = 0
        
        for container_name in all_containers_to_check:
            if container_name in containers:
                container = containers[container_name]
                status = container["status"]
                if "Up" in status:
                    self.success(f"{container_name}: {status}")
                    running_count += 1
                else:
                    self.error(f"{container_name}: {status}")
                    stopped_count += 1
            else:
                self.warning(f"{container_name}: Not found")
        
        self.metrics["containers_running"] = running_count
        self.metrics["containers_stopped"] = stopped_count
        
        # Check container health
        self.print_section("1.1 Container Health Checks")
        for container_name in all_containers_to_check:
            if container_name in containers and "Up" in containers[container_name]["status"]:
                success, health = self.run_command(f"docker inspect {container_name} --format '{{{{.State.Health.Status}}}}' 2>/dev/null")
                if success and health:
                    if health == "healthy":
                        self.success(f"{container_name} health: {health}")
                    elif health == "unhealthy":
                        self.error(f"{container_name} health: {health}")
                    elif health == "starting":
                        self.warning(f"{container_name} health: {health}")
    
    def check_service_health_endpoints(self):
        """Check all service health endpoints"""
        self.print_section("2. SERVICE HEALTH ENDPOINTS")
        
        endpoints = [
            ("Backend-1", "http://localhost:8001/health", "alpine-backend-1"),
            ("Backend-2", "http://localhost:8002/health", "alpine-backend-2"),
            ("Backend-3", "http://localhost:8003/health", "alpine-backend-3"),
            ("Frontend-1", "http://localhost:3000", "alpine-frontend-1"),
            ("Frontend-2", "http://localhost:3002", "alpine-frontend-2"),
        ]
        
        for name, url, container in endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.success(f"{name}: HTTP {response.status_code}")
                    if "health" in url:
                        try:
                            data = response.json()
                            self.info_msg(f"  Status: {data.get('status', 'unknown')}")
                            if 'version' in data:
                                self.info_msg(f"  Version: {data.get('version')}")
                            if 'uptime' in data:
                                self.info_msg(f"  Uptime: {data.get('uptime')}")
                        except:
                            pass
                else:
                    self.error(f"{name}: HTTP {response.status_code}")
            except requests.exceptions.ConnectionError:
                self.error(f"{name}: Connection refused")
            except requests.exceptions.Timeout:
                self.error(f"{name}: Request timeout")
            except Exception as e:
                self.error(f"{name}: {str(e)}")
    
    def check_database_connectivity(self):
        """Check database connectivity and status"""
        self.print_section("3. DATABASE CONNECTIVITY")
        
        # Find postgres container (try multiple names)
        postgres_container = None
        for name in ["alpine-postgres", "alpine-postgres-local", "argo-postgres"]:
            success, _ = self.run_command(f"docker ps | grep {name} | grep Up")
            if success:
                postgres_container = name
                break
        
        if not postgres_container:
            self.warning("PostgreSQL container is not running")
            return
        
        self.success(f"PostgreSQL container is running: {postgres_container}")
        
        # Check database connection
        success, output = self.run_command(
            f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c 'SELECT version();' 2>&1"
        )
        if success:
            self.success("Database connection successful")
            # Extract version
            if "PostgreSQL" in output:
                version_line = [l for l in output.split('\n') if 'PostgreSQL' in l]
                if version_line:
                    self.info_msg(f"  {version_line[0].strip()}")
        else:
            self.error(f"Database connection failed: {output[:100]}")
        
        # Check database size
        success, size = self.run_command(
            f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c \"SELECT pg_size_pretty(pg_database_size('alpine_prod'));\" -t 2>&1"
        )
        if success and size.strip():
            self.info_msg(f"Database size: {size.strip()}")
        
        # Check table counts
        tables = ["users", "signals", "roles", "notifications"]
        for table in tables:
            success, count = self.run_command(
                f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c \"SELECT COUNT(*) FROM {table};\" -t 2>&1"
            )
            if success and count.strip().isdigit():
                self.info_msg(f"  {table}: {count.strip()} rows")
        
        # Check for locks
        success, locks = self.run_command(
            f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c \"SELECT COUNT(*) FROM pg_locks WHERE NOT granted;\" -t 2>&1"
        )
        if success and locks.strip().isdigit():
            lock_count = int(locks.strip())
            if lock_count > 0:
                self.warning(f"Database has {lock_count} ungranted locks")
            else:
                self.success("No database locks detected")
    
    def check_redis_connectivity(self):
        """Check Redis connectivity and status"""
        self.print_section("4. REDIS CONNECTIVITY")
        
        # Find redis container (try multiple names)
        redis_container = None
        for name in ["alpine-redis", "alpine-redis-local", "argo-redis"]:
            success, _ = self.run_command(f"docker ps | grep {name} | grep Up")
            if success:
                redis_container = name
                break
        
        if not redis_container:
            self.warning("Redis container is not running")
            return
        
        self.success(f"Redis container is running: {redis_container}")
        
        # Check Redis connection
        success, output = self.run_command(
            f"docker exec {redis_container} redis-cli -a AlpineRedis2025! PING 2>&1"
        )
        if success and "PONG" in output:
            self.success("Redis connection successful")
        else:
            self.error(f"Redis connection failed: {output[:100]}")
        
        # Check Redis info
        success, info = self.run_command(
            f"docker exec {redis_container} redis-cli -a AlpineRedis2025! INFO stats 2>&1 | grep -E 'total_commands_processed|keyspace_hits|keyspace_misses'"
        )
        if success:
            self.info_msg("Redis statistics:")
            for line in info.split('\n'):
                if line.strip():
                    self.info_msg(f"  {line.strip()}")
        
        # Check memory usage
        success, memory = self.run_command(
            f"docker exec {redis_container} redis-cli -a AlpineRedis2025! INFO memory 2>&1 | grep used_memory_human"
        )
        if success and memory.strip():
            self.info_msg(f"Redis memory: {memory.strip().split(':')[1].strip()}")
        
        # Check key count
        success, keys = self.run_command(
            f"docker exec {redis_container} redis-cli -a AlpineRedis2025! DBSIZE 2>&1"
        )
        if success and keys.strip().isdigit():
            self.info_msg(f"Redis keys: {keys.strip()}")
    
    def check_api_endpoints(self):
        """Check API endpoints functionality"""
        self.print_section("5. API ENDPOINTS")
        
        endpoints = [
            ("Backend-1 Health", "http://localhost:8001/api/v1/health"),
            ("Backend-2 Health", "http://localhost:8002/api/v1/health"),
            ("Backend-3 Health", "http://localhost:8003/api/v1/health"),
            ("Backend-1 Metrics", "http://localhost:8001/metrics"),
            ("Backend-1 API Docs", "http://localhost:8001/docs"),
        ]
        
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.success(f"{name}: HTTP {response.status_code}")
                else:
                    self.warning(f"{name}: HTTP {response.status_code}")
            except Exception as e:
                self.error(f"{name}: {str(e)[:50]}")
    
    def check_logs_for_errors(self):
        """Check logs for errors and warnings"""
        self.print_section("6. LOG ANALYSIS")
        
        # Check Docker container logs
        containers = ["alpine-backend-1", "alpine-backend-2", "alpine-backend-3", 
                     "alpine-frontend-1", "alpine-frontend-2", "alpine-postgres", "alpine-redis"]
        
        error_patterns = ["ERROR", "Exception", "Traceback", "FATAL", "CRITICAL"]
        warning_patterns = ["WARNING", "WARN"]
        
        for container in containers:
            success, _ = self.run_command(f"docker ps | grep {container} | grep Up")
            if not success:
                continue
            
            # Check for errors in last 100 lines
            success, errors = self.run_command(
                f"docker logs {container} --tail 100 2>&1 | grep -iE 'ERROR|Exception|Traceback|FATAL|CRITICAL' | tail -5"
            )
            if success and errors.strip():
                self.warning(f"{container} has recent errors:")
                for line in errors.split('\n')[:3]:
                    if line.strip():
                        self.info_msg(f"  {line.strip()[:100]}")
            
            # Check for warnings
            success, warnings = self.run_command(
                f"docker logs {container} --tail 100 2>&1 | grep -iE 'WARNING|WARN' | tail -3"
            )
            if success and warnings.strip():
                warning_count = len([l for l in warnings.split('\n') if l.strip()])
                if warning_count > 0:
                    self.info_msg(f"{container}: {warning_count} recent warnings")
    
    def check_resource_usage(self):
        """Check system resource usage"""
        self.print_section("7. RESOURCE USAGE")
        
        if not PSUTIL_AVAILABLE:
            self.warning("psutil not available, using alternative methods")
            # Fallback to system commands
            success, cpu_output = self.run_command("top -l 1 | grep 'CPU usage' | awk '{print $3}' | sed 's/%//'")
            if success:
                try:
                    cpu_percent = float(cpu_output)
                    self.info_msg(f"CPU usage: {cpu_percent:.1f}% (from top)")
                    self.metrics["cpu_percent"] = cpu_percent
                except:
                    pass
            
            success, mem_output = self.run_command("vm_stat | perl -ne '/page size of (\\d+)/ and $size=$1; /Pages\\s+([^:]+)[^\\d]+(\\d+)/ and printf(\"%-16s % 16.2f Mi\\n\", \"$1:\", $2 * $size / 1048576);'")
            if success:
                self.info_msg("Memory stats (from vm_stat):")
                for line in mem_output.split('\n')[:5]:
                    if line.strip():
                        self.info_msg(f"  {line.strip()}")
            
            # Disk usage fallback
            success, disk_output = self.run_command("df -h / | tail -1 | awk '{print $5}' | sed 's/%//'")
            if success:
                try:
                    disk_percent = float(disk_output)
                    if disk_percent > 90:
                        self.error(f"High disk usage: {disk_percent:.1f}%")
                    elif disk_percent > 80:
                        self.warning(f"Moderate disk usage: {disk_percent:.1f}%")
                    else:
                        self.success(f"Disk usage: {disk_percent:.1f}%")
                    self.metrics["disk_percent"] = disk_percent
                except:
                    pass
        else:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                self.error(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 60:
                self.warning(f"Moderate CPU usage: {cpu_percent:.1f}%")
            else:
                self.success(f"CPU usage: {cpu_percent:.1f}%")
            self.metrics["cpu_percent"] = cpu_percent
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent > 90:
                self.error(f"High memory usage: {memory_percent:.1f}% ({memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB)")
            elif memory_percent > 75:
                self.warning(f"Moderate memory usage: {memory_percent:.1f}% ({memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB)")
            else:
                self.success(f"Memory usage: {memory_percent:.1f}% ({memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB)")
            self.metrics["memory_percent"] = memory_percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                self.error(f"High disk usage: {disk_percent:.1f}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")
            elif disk_percent > 80:
                self.warning(f"Moderate disk usage: {disk_percent:.1f}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")
            else:
                self.success(f"Disk usage: {disk_percent:.1f}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)")
            self.metrics["disk_percent"] = disk_percent
        
        # Check Docker container resource usage
        self.print_section("7.1 Container Resource Usage")
        success, stats = self.run_command(
            "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' | grep alpine"
        )
        if success and stats.strip():
            self.info_msg("Container resource usage:")
            for line in stats.split('\n')[1:]:  # Skip header
                if line.strip():
                    self.info_msg(f"  {line.strip()}")
    
    def check_network_connectivity(self):
        """Check network connectivity"""
        self.print_section("8. NETWORK CONNECTIVITY")
        
        # Check if ports are listening
        ports = [8001, 8002, 8003, 3000, 3002, 5433, 6380, 9090, 3100]
        
        for port in ports:
            success, _ = self.run_command(f"lsof -i :{port} > /dev/null 2>&1 || netstat -an | grep :{port} | grep LISTEN > /dev/null 2>&1")
            if success:
                self.success(f"Port {port}: Listening")
            else:
                self.warning(f"Port {port}: Not listening")
        
        # Check external connectivity
        external_checks = [
            ("Google DNS", "8.8.8.8"),
            ("Cloudflare DNS", "1.1.1.1"),
        ]
        
        for name, host in external_checks:
            success, _ = self.run_command(f"ping -c 1 -W 2 {host} > /dev/null 2>&1")
            if success:
                self.success(f"{name} ({host}): Reachable")
            else:
                self.warning(f"{name} ({host}): Not reachable")
    
    def check_monitoring_services(self):
        """Check monitoring services (Prometheus, Grafana)"""
        self.print_section("9. MONITORING SERVICES")
        
        # Check Prometheus
        try:
            response = requests.get("http://localhost:9090/-/healthy", timeout=5)
            if response.status_code == 200:
                self.success("Prometheus: Healthy")
            else:
                self.warning(f"Prometheus: HTTP {response.status_code}")
        except Exception as e:
            self.warning(f"Prometheus: {str(e)[:50]}")
        
        # Check Grafana
        try:
            response = requests.get("http://localhost:3100/api/health", timeout=5)
            if response.status_code == 200:
                self.success("Grafana: Healthy")
            else:
                self.warning(f"Grafana: HTTP {response.status_code}")
        except Exception as e:
            self.warning(f"Grafana: {str(e)[:50]}")
        
        # Check exporters
        exporters = [
            ("Node Exporter", "http://localhost:9100/metrics"),
            ("Postgres Exporter", "http://localhost:9187/metrics"),
            ("Redis Exporter", "http://localhost:9121/metrics"),
        ]
        
        for name, url in exporters:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.success(f"{name}: Accessible")
                else:
                    self.warning(f"{name}: HTTP {response.status_code}")
            except Exception as e:
                self.warning(f"{name}: {str(e)[:50]}")
    
    def check_trading_system_status(self):
        """Check trading system specific status"""
        self.print_section("10. TRADING SYSTEM STATUS")
        
        # Check backend trading endpoints
        backends = [
            ("Backend-1", "http://localhost:8001"),
            ("Backend-2", "http://localhost:8002"),
            ("Backend-3", "http://localhost:8003"),
        ]
        
        for name, base_url in backends:
            try:
                # Check trading status
                response = requests.get(f"{base_url}/api/v1/trading/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.success(f"{name} trading status: Accessible")
                    self.info_msg(f"  Environment: {data.get('environment', 'unknown')}")
                    self.info_msg(f"  Trading Mode: {data.get('trading_mode', 'unknown')}")
                    self.info_msg(f"  Alpaca Connected: {data.get('alpaca_connected', False)}")
                else:
                    self.warning(f"{name} trading status: HTTP {response.status_code}")
            except Exception as e:
                self.warning(f"{name} trading status: {str(e)[:50]}")
    
    def generate_report(self):
        """Generate comprehensive debug report"""
        self.print_header("DEBUG REPORT SUMMARY")
        
        elapsed_time = time.time() - self.start_time
        
        print(f"\n{Colors.BOLD}Execution Time: {elapsed_time:.2f} seconds{Colors.NC}\n")
        
        print(f"{Colors.BOLD}Issues Found: {len(self.issues)}{Colors.NC}")
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        print(f"\n{Colors.BOLD}Warnings: {len(self.warnings)}{Colors.NC}")
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print(f"\n{Colors.BOLD}Metrics:{Colors.NC}")
        for key, value in self.metrics.items():
            print(f"  {key}: {value}")
        
        # Overall status
        print(f"\n{Colors.BOLD}Overall Status:{Colors.NC}")
        if len(self.issues) == 0 and len(self.warnings) == 0:
            print(f"{Colors.GREEN}✅ All systems operational!{Colors.NC}")
            return 0
        elif len(self.issues) == 0:
            print(f"{Colors.YELLOW}⚠️  System operational with warnings{Colors.NC}")
            return 0
        else:
            print(f"{Colors.RED}❌ System has critical issues{Colors.NC}")
            return 1
    
    def run_all_checks(self):
        """Run all debugging checks"""
        self.print_header("COMPREHENSIVE PRODUCTION DEBUGGING")
        print(f"{Colors.CYAN}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}\n")
        
        try:
            self.check_docker_containers()
            self.check_service_health_endpoints()
            self.check_database_connectivity()
            self.check_redis_connectivity()
            self.check_api_endpoints()
            self.check_logs_for_errors()
            self.check_resource_usage()
            self.check_network_connectivity()
            self.check_monitoring_services()
            self.check_trading_system_status()
        except Exception as e:
            self.error(f"Error during checks: {str(e)}")
            traceback.print_exc()
        
        return self.generate_report()

def main():
    """Main entry point"""
    debugger = ProductionDebugger()
    exit_code = debugger.run_all_checks()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

