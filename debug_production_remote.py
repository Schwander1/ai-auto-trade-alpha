#!/usr/bin/env python3
"""
Remote Production Debugging Script
Performs comprehensive debugging checks on remote production servers
"""
import sys
import json
import subprocess
import requests
import time
from datetime import datetime
from typing import Tuple, Optional

# Production server configuration
ARGO_SERVER = "178.156.194.174"
ALPINE_SERVER = "91.98.153.49"
ARGO_USER = "root"
ALPINE_USER = "root"

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'
    BOLD = '\033[1m'

class RemoteProductionDebugger:
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
    
    def run_ssh_command(self, server: str, user: str, cmd: str, timeout: int = 30) -> Tuple[bool, str]:
        """Run a command on remote server via SSH"""
        try:
            # Escape single quotes in the command
            escaped_cmd = cmd.replace("'", "'\"'\"'")
            ssh_cmd = f"ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no {user}@{server} '{escaped_cmd}'"
            result = subprocess.run(
                ssh_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout.strip() if result.stdout else ""
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "SSH command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_argo_service(self):
        """Check Argo production service"""
        self.print_section("1. ARGO PRODUCTION SERVICE")
        
        # Check service status
        success, output = self.run_ssh_command(
            ARGO_SERVER, ARGO_USER,
            "systemctl is-active argo-trading.service 2>/dev/null || echo 'inactive'"
        )
        if success and "active" in output:
            self.success(f"Argo service is running on {ARGO_SERVER}")
        else:
            self.error(f"Argo service is not running on {ARGO_SERVER}")
        
        # Check health endpoint
        try:
            response = requests.get(f"http://{ARGO_SERVER}:8000/health", timeout=10)
            if response.status_code == 200:
                self.success(f"Argo health endpoint: HTTP {response.status_code}")
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
                self.error(f"Argo health endpoint: HTTP {response.status_code}")
        except Exception as e:
            self.error(f"Argo health endpoint: {str(e)[:50]}")
        
        # Check which environment is active
        success, env = self.run_ssh_command(
            ARGO_SERVER, ARGO_USER,
            "if [ -f /root/argo-production-green/.current ]; then echo 'green'; elif [ -f /root/argo-production-blue/.current ]; then echo 'blue'; else echo 'unknown'; fi"
        )
        if success:
            self.info_msg(f"Active environment: {env}")
        
        # Check recent logs for errors
        success, errors = self.run_ssh_command(
            ARGO_SERVER, ARGO_USER,
            "tail -n 100 /tmp/argo-blue.log 2>/dev/null | grep -iE 'ERROR|Exception|Traceback' | tail -5 || echo 'no errors'"
        )
        if success and errors and "no errors" not in errors.lower():
            self.warning("Recent errors in Argo logs:")
            for line in errors.split('\n')[:3]:
                if line.strip():
                    self.info_msg(f"  {line.strip()[:100]}")
    
    def check_alpine_containers(self):
        """Check Alpine production containers"""
        self.print_section("2. ALPINE PRODUCTION CONTAINERS")
        
        # Get all running containers (check multiple naming patterns)
        success, containers = self.run_ssh_command(
            ALPINE_SERVER, ALPINE_USER,
            "docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'alpine-backend|alpine-frontend|alpine-postgres|alpine-redis' | grep -v exporter"
        )
        
        container_list = {}
        if success and containers and containers.strip():
            for line in containers.split('\n'):
                line = line.strip()
                if line:
                    # Handle tab-separated values, but be flexible with whitespace
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        status = '\t'.join(parts[1:]).strip()  # Join remaining parts
                        if name:
                            container_list[name] = status
                    elif ' ' in line:
                        # Fallback: split on first space if no tabs
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            status = parts[1].strip()
                            if name:
                                container_list[name] = status
        
        # Debug: Show what containers were found
        if not container_list:
            self.warning(f"No containers parsed from output. Raw output length: {len(containers) if containers else 0}")
        
        # Check specific containers with flexible matching
        expected_patterns = {
            "backend-1": ["alpine-backend-1", "backend-1"],
            "backend-2": ["alpine-backend-2", "backend-2"],
            "backend-3": ["alpine-backend-3", "backend-3"],
            "frontend-1": ["alpine-frontend-1", "frontend-1"],
            "frontend-2": ["alpine-frontend-2", "frontend-2"],
            "postgres": ["alpine-postgres"],
            "redis": ["alpine-redis"],
        }
        
        found_containers = {}
        for key, patterns in expected_patterns.items():
            for pattern in patterns:
                # Check exact match first
                if pattern in container_list:
                    found_containers[key] = {"name": pattern, "status": container_list[pattern]}
                    break
            # If not found with exact pattern, try matching any container name
            if key not in found_containers:
                for container_name, status in container_list.items():
                    # Check if container name matches any of the patterns
                    for pattern in patterns:
                        if container_name == pattern or pattern in container_name:
                            found_containers[key] = {"name": container_name, "status": status}
                            break
                    if key in found_containers:
                        break
        
        if found_containers:
            self.success(f"Found {len(found_containers)} Alpine containers:")
            for key, info in found_containers.items():
                if "Up" in info["status"]:
                    self.success(f"  {info['name']}: {info['status']}")
                else:
                    self.warning(f"  {info['name']}: {info['status']}")
            self.metrics["alpine_containers_running"] = len([c for c in found_containers.values() if "Up" in c["status"]])
        else:
            self.warning("Could not find expected Alpine containers")
            if container_list:
                self.info_msg("Available containers:")
                for name, status in container_list.items():
                    self.info_msg(f"  {name}: {status}")
            self.metrics["alpine_containers_running"] = 0
        
        # Store container names for later use
        self.alpine_containers = found_containers
    
    def check_alpine_health_endpoints(self):
        """Check Alpine health endpoints"""
        self.print_section("3. ALPINE HEALTH ENDPOINTS")
        
        endpoints = [
            ("Backend-1", f"http://{ALPINE_SERVER}:8001/health"),
            ("Backend-2", f"http://{ALPINE_SERVER}:8002/health"),
            ("Backend-3", f"http://{ALPINE_SERVER}:8003/health"),
            ("Frontend-1", f"http://{ALPINE_SERVER}:3000"),
        ]
        
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.success(f"{name}: HTTP {response.status_code}")
                    if "health" in url:
                        try:
                            data = response.json()
                            self.info_msg(f"  Status: {data.get('status', 'unknown')}")
                        except:
                            pass
                else:
                    self.warning(f"{name}: HTTP {response.status_code}")
            except Exception as e:
                self.error(f"{name}: {str(e)[:50]}")
    
    def check_alpine_database(self):
        """Check Alpine database"""
        self.print_section("4. ALPINE DATABASE")
        
        # Find postgres container name
        postgres_container = None
        if hasattr(self, 'alpine_containers') and 'postgres' in self.alpine_containers:
            postgres_container = self.alpine_containers['postgres']['name']
        else:
            # Try to find it (exclude exporters)
            success, containers = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                "docker ps --format '{{.Names}}' | grep -i postgres | grep -v exporter | head -1"
            )
            if success and containers.strip():
                postgres_container = containers.strip()
        
        if postgres_container:
            self.success(f"PostgreSQL container found: {postgres_container}")
            
            # Check database connection
            success, output = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c 'SELECT version();' 2>&1 | head -3"
            )
            if success and "PostgreSQL" in output:
                self.success("Database connection successful")
                version_line = [l for l in output.split('\n') if 'PostgreSQL' in l]
                if version_line:
                    self.info_msg(f"  {version_line[0].strip()[:80]}")
            
            # Check database size
            success, size = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                f"docker exec {postgres_container} psql -U alpine_user -d alpine_prod -c \"SELECT pg_size_pretty(pg_database_size('alpine_prod'));\" -t 2>&1"
            )
            if success and size.strip():
                self.info_msg(f"Database size: {size.strip()}")
        else:
            self.error("PostgreSQL container not found")
    
    def check_alpine_redis(self):
        """Check Alpine Redis"""
        self.print_section("5. ALPINE REDIS")
        
        # Find redis container name
        redis_container = None
        if hasattr(self, 'alpine_containers') and 'redis' in self.alpine_containers:
            redis_container = self.alpine_containers['redis']['name']
        else:
            # Try to find it (exclude exporters)
            success, containers = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                "docker ps --format '{{.Names}}' | grep -i redis | grep -v exporter | head -1"
            )
            if success and containers.strip():
                redis_container = containers.strip()
        
        if redis_container:
            self.success(f"Redis container found: {redis_container}")
            
            # Check Redis connection
            success, output = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                f"docker exec {redis_container} redis-cli -a AlpineRedis2025! PING 2>&1"
            )
            if success and "PONG" in output:
                self.success("Redis connection successful")
            
            # Check Redis info
            success, keys = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                f"docker exec {redis_container} redis-cli -a AlpineRedis2025! DBSIZE 2>&1"
            )
            if success and keys.strip().isdigit():
                self.info_msg(f"Redis keys: {keys.strip()}")
        else:
            self.error("Redis container not found")
    
    def check_alpine_api_endpoints(self):
        """Check Alpine API endpoints"""
        self.print_section("6. ALPINE API ENDPOINTS")
        
        endpoints = [
            ("Backend-1 Health", f"http://{ALPINE_SERVER}:8001/api/v1/health"),
            ("Backend-1 Metrics", f"http://{ALPINE_SERVER}:8001/metrics"),
            ("Backend-1 Docs", f"http://{ALPINE_SERVER}:8001/docs"),
        ]
        
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.success(f"{name}: HTTP {response.status_code}")
                else:
                    self.warning(f"{name}: HTTP {response.status_code}")
            except Exception as e:
                self.warning(f"{name}: {str(e)[:50]}")
    
    def check_alpine_logs(self):
        """Check Alpine container logs for errors"""
        self.print_section("7. ALPINE LOGS")
        
        # Get backend container names
        backend_containers = []
        if hasattr(self, 'alpine_containers'):
            for key in ['backend-1', 'backend-2', 'backend-3']:
                if key in self.alpine_containers:
                    backend_containers.append(self.alpine_containers[key]['name'])
        
        if not backend_containers:
            # Fallback: try to find backend containers
            success, containers = self.run_ssh_command(
                ALPINE_SERVER, ALPINE_USER,
                "docker ps --format '{{.Names}}' | grep -i backend | head -3"
            )
            if success and containers.strip():
                backend_containers = [c.strip() for c in containers.split('\n') if c.strip()]
        
        if backend_containers:
            for container in backend_containers[:3]:  # Limit to 3
                success, errors = self.run_ssh_command(
                    ALPINE_SERVER, ALPINE_USER,
                    f"docker logs {container} --tail 50 2>&1 | grep -iE 'ERROR|Exception|Traceback|FATAL' | tail -3 || echo 'no errors'"
                )
                if success and errors and "no errors" not in errors.lower():
                    self.warning(f"{container} has recent errors:")
                    for line in errors.split('\n')[:2]:
                        if line.strip():
                            self.info_msg(f"  {line.strip()[:100]}")
        else:
            self.warning("No backend containers found to check logs")
    
    def check_signal_generation(self):
        """Check signal generation status"""
        self.print_section("10. SIGNAL GENERATION STATUS")
        
        # Check Argo signal generation
        try:
            response = requests.get(f"http://{ARGO_SERVER}:8000/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                signal_gen = data.get('signal_generation', {})
                if signal_gen:
                    status = signal_gen.get('status', 'unknown')
                    bg_task = signal_gen.get('background_task_running', False)
                    error = signal_gen.get('background_task_error')
                    
                    if status in ['active', 'running'] and bg_task:
                        self.success("Signal generation: Active and running")
                    elif status in ['active', 'running']:
                        self.warning("Signal generation: Active but background task not running")
                    else:
                        self.warning(f"Signal generation: {status}")
                    
                    if error:
                        self.error(f"Signal generation error: {error[:100]}")
        except requests.exceptions.ConnectionError:
            # Try with explicit port
            try:
                response = requests.get(f"http://{ARGO_SERVER}:8000/health", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    signal_gen = data.get('signal_generation', {})
                    if signal_gen:
                        status = signal_gen.get('status', 'unknown')
                        if status in ['active', 'running']:
                            self.success(f"Signal generation: {status}")
            except:
                self.warning("Could not check signal generation (connection error)")
        except Exception as e:
            self.warning(f"Could not check signal generation: {str(e)[:50]}")
        
        # Check recent signals
        try:
            response = requests.get(f"http://{ARGO_SERVER}:8000/api/signals/latest?limit=5", timeout=10)
            if response.status_code == 200:
                signals = response.json()
                if isinstance(signals, list) and len(signals) > 0:
                    self.success(f"Recent signals: {len(signals)} found")
                    executed = sum(1 for s in signals if s.get('order_id'))
                    self.info_msg(f"  Executed: {executed}/{len(signals)}")
                else:
                    self.warning("No recent signals found")
        except requests.exceptions.ConnectionError:
            # Try alternative endpoint
            try:
                response = requests.get(f"http://{ARGO_SERVER}:8000/signals/latest?limit=5", timeout=10)
                if response.status_code == 200:
                    signals = response.json()
                    if isinstance(signals, list) and len(signals) > 0:
                        self.success(f"Recent signals: {len(signals)} found (via alternative endpoint)")
                        executed = sum(1 for s in signals if s.get('order_id'))
                        self.info_msg(f"  Executed: {executed}/{len(signals)}")
            except:
                self.warning("Could not check recent signals (endpoint not accessible)")
        except Exception as e:
            self.warning(f"Could not check recent signals: {str(e)[:50]}")
    
    def check_trading_status(self):
        """Check trading system status"""
        self.print_section("11. TRADING SYSTEM STATUS")
        
        # Check Argo trading status
        try:
            response = requests.get(f"http://{ARGO_SERVER}:8000/api/v1/trading/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.success("Trading status endpoint: Accessible")
                self.info_msg(f"  Environment: {data.get('environment', 'unknown')}")
                self.info_msg(f"  Trading Mode: {data.get('trading_mode', 'unknown')}")
                self.info_msg(f"  Alpaca Connected: {data.get('alpaca_connected', False)}")
                self.info_msg(f"  Trading Blocked: {data.get('trading_blocked', False)}")
                if data.get('portfolio_value'):
                    self.info_msg(f"  Portfolio Value: ${data.get('portfolio_value', 0):,.2f}")
        except Exception as e:
            self.warning(f"Could not check trading status: {str(e)[:50]}")
    
    def check_alpine_resources(self):
        """Check Alpine server resources"""
        self.print_section("8. ALPINE SERVER RESOURCES")
        
        # Check disk usage
        success, disk = self.run_ssh_command(
            ALPINE_SERVER, ALPINE_USER,
            "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
        )
        if success and disk.strip().isdigit():
            disk_percent = float(disk.strip())
            if disk_percent > 90:
                self.error(f"High disk usage: {disk_percent:.1f}%")
            elif disk_percent > 80:
                self.warning(f"Moderate disk usage: {disk_percent:.1f}%")
            else:
                self.success(f"Disk usage: {disk_percent:.1f}%")
            self.metrics["alpine_disk_percent"] = disk_percent
        
        # Check container resource usage
        success, stats = self.run_ssh_command(
            ALPINE_SERVER, ALPINE_USER,
            "docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep alpine | head -5"
        )
        if success and stats.strip():
            self.info_msg("Container resource usage:")
            for line in stats.split('\n'):
                if line.strip():
                    self.info_msg(f"  {line.strip()}")
    
    def check_network_connectivity(self):
        """Check network connectivity to production servers"""
        self.print_section("9. NETWORK CONNECTIVITY")
        
        # Check Argo server
        success, _ = self.run_ssh_command(ARGO_SERVER, ARGO_USER, "echo 'connected'", timeout=5)
        if success:
            self.success(f"SSH connection to Argo server ({ARGO_SERVER}): OK")
        else:
            self.error(f"SSH connection to Argo server ({ARGO_SERVER}): Failed")
        
        # Check Alpine server
        success, _ = self.run_ssh_command(ALPINE_SERVER, ALPINE_USER, "echo 'connected'", timeout=5)
        if success:
            self.success(f"SSH connection to Alpine server ({ALPINE_SERVER}): OK")
        else:
            self.error(f"SSH connection to Alpine server ({ALPINE_SERVER}): Failed")
        
        # Check HTTP endpoints (external)
        for server, port, name in [
            (ARGO_SERVER, 8000, "Argo API"),
            (ALPINE_SERVER, 8001, "Alpine Backend-1"),
            (ALPINE_SERVER, 3000, "Alpine Frontend"),
        ]:
            try:
                response = requests.get(f"http://{server}:{port}", timeout=5)
                self.success(f"{name} ({server}:{port}): Accessible externally")
            except:
                self.warning(f"{name} ({server}:{port}): Not accessible externally (may be firewall-protected)")
        
        # Check internal connectivity from Alpine server
        self.print_section("9.1 INTERNAL NETWORK CONNECTIVITY")
        internal_checks = [
            ("Backend-1 (localhost:8001)", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health 2>/dev/null || wget -q -O /dev/null -S http://localhost:8001/health 2>&1 | grep -oP 'HTTP/\\d\\.\\d \\K\\d{3}' || echo '000'"),
            ("Backend-2 (localhost:8002)", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/health 2>/dev/null || wget -q -O /dev/null -S http://localhost:8002/health 2>&1 | grep -oP 'HTTP/\\d\\.\\d \\K\\d{3}' || echo '000'"),
            ("Backend-3 (localhost:8003)", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8003/health 2>/dev/null || wget -q -O /dev/null -S http://localhost:8003/health 2>&1 | grep -oP 'HTTP/\\d\\.\\d \\K\\d{3}' || echo '000'"),
            ("Frontend-1 (localhost:3000)", "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || wget -q -O /dev/null -S http://localhost:3000 2>&1 | grep -oP 'HTTP/\\d\\.\\d \\K\\d{3}' || echo '000'"),
            ("Frontend-2 (localhost:3002)", "curl -s -o /dev/null -w '%{http_code}' http://localhost:3002 2>/dev/null || wget -q -O /dev/null -S http://localhost:3002 2>&1 | grep -oP 'HTTP/\\d\\.\\d \\K\\d{3}' || echo '000'"),
        ]
        
        for name, cmd in internal_checks:
            success, code = self.run_ssh_command(ALPINE_SERVER, ALPINE_USER, cmd, timeout=5)
            if success and code.strip() == "200":
                self.success(f"{name}: HTTP 200 (internal)")
            elif success and code.strip() != "000":
                self.warning(f"{name}: HTTP {code.strip()} (internal)")
            else:
                self.warning(f"{name}: Not accessible (internal)")
    
    def generate_report(self):
        """Generate comprehensive debug report"""
        self.print_header("REMOTE PRODUCTION DEBUG REPORT")
        
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
            print(f"{Colors.GREEN}✅ All production systems operational!{Colors.NC}")
            return 0
        elif len(self.issues) == 0:
            print(f"{Colors.YELLOW}⚠️  Production systems operational with warnings{Colors.NC}")
            return 0
        else:
            print(f"{Colors.RED}❌ Production systems have critical issues{Colors.NC}")
            return 1
    
    def run_all_checks(self):
        """Run all debugging checks"""
        self.print_header("COMPREHENSIVE REMOTE PRODUCTION DEBUGGING")
        print(f"{Colors.CYAN}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}\n")
        print(f"{Colors.CYAN}Argo Server: {ARGO_SERVER}{Colors.NC}")
        print(f"{Colors.CYAN}Alpine Server: {ALPINE_SERVER}{Colors.NC}\n")
        
        try:
            self.alpine_containers = {}  # Initialize container tracking
            self.check_argo_service()
            self.check_alpine_containers()
            self.check_alpine_health_endpoints()
            self.check_alpine_database()
            self.check_alpine_redis()
            self.check_alpine_api_endpoints()
            self.check_alpine_logs()
            self.check_alpine_resources()
            self.check_network_connectivity()
            self.check_signal_generation()
            self.check_trading_status()
        except Exception as e:
            self.error(f"Error during checks: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return self.generate_report()

def main():
    """Main entry point"""
    debugger = RemoteProductionDebugger()
    exit_code = debugger.run_all_checks()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

