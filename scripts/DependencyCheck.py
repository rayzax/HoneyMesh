#!/usr/bin/env python3
"""
HoneyMesh Dependency Checker
Verifies all required dependencies are installed and properly configured
"""

import sys
import subprocess
import importlib
import socket
import os
import shutil
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DependencyChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
        
    def print_status(self, message: str, status: str = "info"):
        """Print status messages with colored indicators"""
        if status == "success":
            print(f"{Colors.GREEN}[+]{Colors.END} {message}")
            self.success_count += 1
        elif status == "warning":
            print(f"{Colors.YELLOW}[-]{Colors.END} {message}")
            self.warnings.append(message)
        elif status == "error":
            print(f"{Colors.RED}[x]{Colors.END} {message}")
            self.errors.append(message)
        else:
            print(f"{Colors.BLUE}[i]{Colors.END} {message}")
            
    def check_python_version(self):
        """Check Python version compatibility"""
        self.total_checks += 1
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 7:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} detected", "success")
        else:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} - requires Python 3.7+", "error")
            
    def check_system_commands(self):
        """Check required system commands"""
        commands = {
            'docker': 'Docker container runtime',
            'docker-compose': 'Docker Compose orchestration',
            'curl': 'HTTP client for health checks'
        }
        
        for cmd, description in commands.items():
            self.total_checks += 1
            if shutil.which(cmd):
                try:
                    result = subprocess.run([cmd, '--version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version_info = result.stdout.split('\n')[0]
                        self.print_status(f"{description}: {version_info}", "success")
                    else:
                        self.print_status(f"{description}: Command found but version check failed", "warning")
                except subprocess.TimeoutExpired:
                    self.print_status(f"{description}: Version check timed out", "warning")
                except Exception as e:
                    self.print_status(f"{description}: Error checking version - {str(e)}", "warning")
            else:
                self.print_status(f"{description}: Command not found", "error")
                
    def check_python_packages(self):
        """Check required Python packages"""
        packages = {
            'docker': 'Docker Python SDK',
            'yaml': 'YAML configuration parser',
            'requests': 'HTTP requests library'
        }
        
        for package, description in packages.items():
            self.total_checks += 1
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                self.print_status(f"{description}: v{version}", "success")
            except ImportError:
                self.print_status(f"{description}: Not installed", "error")
                
    def check_docker_permissions(self):
        """Check if user can access Docker without sudo"""
        self.total_checks += 1
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self.print_status("Docker daemon accessible without sudo", "success")
        except Exception as e:
            error_msg = str(e).lower()
            if 'permission denied' in error_msg:
                self.print_status("Docker permission denied - user not in docker group", "error")
            elif 'connection refused' in error_msg:
                self.print_status("Docker daemon not running", "error")
            else:
                self.print_status(f"Docker access error: {str(e)}", "error")
                
    def check_port_availability(self):
        """Check if required ports are available"""
        ports = {
            2222: 'SSH Honeypot (default)',
            2223: 'Telnet Honeypot (optional)',
            5601: 'Kibana Dashboard (default)', 
            9200: 'Elasticsearch API',
            9600: 'Logstash API'
        }
        
        for port, description in ports.items():
            self.total_checks += 1
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    self.print_status(f"Port {port} ({description}): Available", "success")
            except socket.error:
                if port in [2223]:  # Optional ports
                    self.print_status(f"Port {port} ({description}): In use (optional)", "warning")
                else:
                    self.print_status(f"Port {port} ({description}): In use", "error")
                    
    def check_disk_space(self):
        """Check available disk space"""
        self.total_checks += 1
        try:
            disk_usage = shutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            
            if free_gb >= 10:
                self.print_status(f"Disk space: {free_gb:.1f}GB available", "success")
            elif free_gb >= 5:
                self.print_status(f"Disk space: {free_gb:.1f}GB available (minimum met)", "warning")
            else:
                self.print_status(f"Disk space: {free_gb:.1f}GB available (need 5GB minimum)", "error")
                
        except Exception as e:
            self.print_status(f"Could not check disk space: {str(e)}", "warning")
            
    def check_memory(self):
        """Check available system memory"""
        self.total_checks += 1
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                
            for line in meminfo.split('\n'):
                if line.startswith('MemAvailable:'):
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / (1024**2)
                    
                    if mem_gb >= 4:
                        self.print_status(f"Available memory: {mem_gb:.1f}GB", "success")
                    elif mem_gb >= 2:
                        self.print_status(f"Available memory: {mem_gb:.1f}GB (minimum met)", "warning")
                    else:
                        self.print_status(f"Available memory: {mem_gb:.1f}GB (need 2GB minimum)", "error")
                    break
            else:
                self.print_status("Could not determine available memory", "warning")
                
        except Exception as e:
            self.print_status(f"Memory check failed: {str(e)}", "warning")
            
    def run_all_checks(self):
        """Run all dependency checks"""
        print(f"{Colors.BOLD}HoneyMesh Dependency Check{Colors.END}\n")
        
        print(f"{Colors.BLUE}Checking Python environment...{Colors.END}")
        self.check_python_version()
        self.check_python_packages()
        
        print(f"\n{Colors.BLUE}Checking system commands...{Colors.END}")
        self.check_system_commands()
        
        print(f"\n{Colors.BLUE}Checking Docker configuration...{Colors.END}")
        self.check_docker_permissions()
        
        print(f"\n{Colors.BLUE}Checking system resources...{Colors.END}")
        self.check_port_availability()
        self.check_disk_space()
        self.check_memory()
        
        # Summary
        print(f"\n{Colors.BOLD}Dependency Check Summary:{Colors.END}")
        print(f"{Colors.GREEN}Passed: {self.success_count}/{self.total_checks}{Colors.END}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.END}")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if self.errors:
            print(f"{Colors.RED}Errors: {len(self.errors)}{Colors.END}")
            for error in self.errors:
                print(f"  - {error}")
                
        return len(self.errors) == 0
        
    def print_installation_help(self):
        """Print installation instructions for missing dependencies"""
        if not self.errors:
            return
            
        print(f"\n{Colors.BOLD}Installation Instructions:{Colors.END}")
        
        # Check what's missing and provide specific instructions
        missing_packages = [error for error in self.errors if "Not installed" in error]
        docker_issues = [error for error in self.errors if "docker" in error.lower()]
        port_issues = [error for error in self.errors if "Port" in error and "In use" in error]
        
        if missing_packages:
            print(f"\n{Colors.YELLOW}Install missing Python packages:{Colors.END}")
            print("pip3 install docker pyyaml requests")
            
        if docker_issues:
            print(f"\n{Colors.YELLOW}Fix Docker issues:{Colors.END}")
            if any("not in docker group" in error for error in docker_issues):
                print("sudo usermod -aG docker $USER")
                print("# Then logout and login again")
            if any("daemon not running" in error for error in docker_issues):
                print("sudo systemctl start docker")
                print("sudo systemctl enable docker")
                
        if port_issues:
            print(f"\n{Colors.YELLOW}Port conflicts detected:{Colors.END}")
            print("Use different ports in configuration or stop conflicting services")
            
        print(f"\n{Colors.BLUE}Quick install command:{Colors.END}")
        print("sudo apt update && sudo apt install -y docker-compose python3-pip curl && pip3 install docker pyyaml requests")

def main():
    """Run dependency checker as standalone script"""
    # Check if running as root/sudo - this should NOT be the case
    if os.geteuid() == 0:
        print(f"{Colors.RED}{Colors.BOLD}WARNING: Running as root/sudo detected!{Colors.END}\n")
        print(f"{Colors.YELLOW}HoneyMesh should NOT be run as root for security reasons:{Colors.END}")
        print("• Docker containers will run with elevated privileges")
        print("• Log files will be owned by root") 
        print("• Security risks if honeypot is compromised")
        print("• Docker group membership allows non-root Docker access")
        
        print(f"\n{Colors.GREEN}Recommended approach:{Colors.END}")
        print("1. Add your user to docker group: sudo usermod -aG docker $USER")
        print("2. Logout and login again")
        print("3. Run as normal user: python3 check_deps.py")
        
        choice = input(f"\n{Colors.RED}Continue checking anyway? [y/N]: {Colors.END}").strip().lower()
        if choice not in ['y', 'yes']:
            print(f"{Colors.CYAN}Exiting. Please run as normal user for security.{Colors.END}")
            return 1
        else:
            print(f"{Colors.YELLOW}Continuing as root (not recommended)...\n{Colors.END}")
    
    checker = DependencyChecker()
    
    try:
        success = checker.run_all_checks()
        
        if success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All dependencies satisfied! HoneyMesh is ready to run.{Colors.END}")
            return 0
        else:
            checker.print_installation_help()
            print(f"\n{Colors.RED}{Colors.BOLD}Please fix the above issues before running HoneyMesh.{Colors.END}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Dependency check cancelled.{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during dependency check: {str(e)}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
