#!/usr/bin/env python3
"""
HoneyMesh - Self-hosted honeypot deployment platform
A simplified honeypot creation and management tool for security professionals
"""

import os
import sys
import time
import json
import subprocess
import socket
import shutil
import yaml
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import docker
from docker.errors import DockerException, APIError, ImageNotFound
import threading

try:
    from medium.medium_deployment import MediumDeploymentManager
    MEDIUM_AVAILABLE = True
except ImportError:
    MEDIUM_AVAILABLE = False

# Embedded dependency checker
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

    def check_critical_dependencies(self) -> bool:
        """Quick check of critical dependencies only"""
        self.total_checks = 0
        self.errors = []
        self.warnings = []
        self.success_count = 0

        # Check Python packages
        critical_packages = ['docker', 'yaml', 'requests']
        for package in critical_packages:
            self.total_checks += 1
            try:
                importlib.import_module(package)
                self.success_count += 1
            except ImportError:
                self.errors.append(f"Python package '{package}' not installed")

        # Check Docker command
        self.total_checks += 1
        if shutil.which('docker'):
            self.success_count += 1
        else:
            self.errors.append("Docker command not found")

        # Check docker-compose command
        self.total_checks += 1
        if shutil.which('docker-compose'):
            self.success_count += 1
        else:
            self.errors.append("docker-compose command not found")

        # Check Docker permissions
        self.total_checks += 1
        try:
            import docker as docker_module
            client = docker_module.from_env()
            client.ping()
            self.success_count += 1
        except Exception:
            self.errors.append("Cannot access Docker daemon (check permissions)")

        return len(self.errors) == 0

    def print_quick_fix(self):
        """Print quick installation command"""
        print(f"\n{Colors.YELLOW}Quick fix command:{Colors.END}")
        print("sudo apt update && sudo apt install -y docker-compose python3-pip && pip3 install docker pyyaml requests && sudo usermod -aG docker $USER")
        print(f"{Colors.RED}After running the above, logout and login again!{Colors.END}")

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class HoneyMeshApp:
    def __init__(self):
        self.data_dir = Path("./honeypot-data")
        self.config_file = self.data_dir / "config.json"
        self.docker_compose_file = self.data_dir / "docker-compose.yml"
        self.docker_client = None
        self.config = {}
        self.containers = {}

        # Setup logging
        self.log_dir = Path("./honeymesh-logs")
        self.log_dir.mkdir(exist_ok=True)
        self.setup_logging()

        # Service definitions
        self.services = {
            'elasticsearch': 'honeymesh-elasticsearch',
            'logstash': 'honeymesh-logstash',
            'filebeat': 'honeymesh-filebeat',
            'cowrie': 'honeymesh-cowrie',
            'kibana': 'honeymesh-kibana'
        }

        self.medium_manager = None

    def setup_logging(self):
        """Setup comprehensive logging to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"honeymesh_{timestamp}.log"

        # Setup logger
        self.logger = logging.getLogger('HoneyMesh')
        self.logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        self.logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

        self.logger.info("HoneyMesh logging initialized")
        self.logger.info(f"Log file: {log_file}")

        # Store log file path for user reference
        self.current_log_file = log_file

    def print_banner(self):
        """Display the application banner with ASCII art"""
        banner = f"""{Colors.CYAN}
██╗  ██╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗███╗   ███╗███████╗███████╗██╗  ██╗
██║  ██║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝████╗ ████║██╔════╝██╔════╝██║  ██║
███████║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ ██╔████╔██║█████╗  ███████╗███████║
██╔══██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  ██║╚██╔╝██║██╔══╝  ╚════██║██╔══██║
██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ██║ ╚═╝ ██║███████╗███████║██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
{Colors.END}
{Colors.BOLD}                    Self-Hosted Honeypot Deployment Platform{Colors.END}
{Colors.WHITE}                         Version 1.0 - Security Research Tool{Colors.END}

{Colors.YELLOW}WARNING:{Colors.END} This tool deploys honeypots that expose services to potential attackers.
{Colors.YELLOW}DISCLAIMER:{Colors.END} Use only on networks you own or have explicit permission to test.
The authors are not responsible for misuse or any damages caused by this software.

{Colors.GREEN}Legal Notice:{Colors.END} Ensure compliance with local laws and regulations before deployment.
"""
        print(banner)

    def print_status(self, message: str, status: str = "info"):
        """Print status messages with colored indicators and log to file"""
        # Log to file
        if hasattr(self, 'logger'):
            if status == "success":
                self.logger.info(f"SUCCESS: {message}")
            elif status == "warning":
                self.logger.warning(f"WARNING: {message}")
            elif status == "error":
                self.logger.error(f"ERROR: {message}")
            else:
                self.logger.info(f"INFO: {message}")

        # Print to console
        if status == "success":
            print(f"{Colors.GREEN}[+]{Colors.END} {message}")
        elif status == "warning":
            print(f"{Colors.YELLOW}[-]{Colors.END} {message}")
        elif status == "error":
            print(f"{Colors.RED}[x]{Colors.END} {message}")
        else:
            print(f"{Colors.BLUE}[i]{Colors.END} {message}")

    def log_exception(self, operation: str, exception: Exception):
        """Log detailed exception information"""
        if hasattr(self, 'logger'):
            self.logger.error(f"EXCEPTION in {operation}")
            self.logger.error(f"Exception type: {type(exception).__name__}")
            self.logger.error(f"Exception message: {str(exception)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def log_docker_info(self):
        """Log Docker environment information"""
        try:
            if not self.docker_client:
                self.docker_client = docker.from_env()

            # Log Docker version
            version_info = self.docker_client.version()
            self.logger.info(f"Docker version: {version_info.get('Version', 'unknown')}")

            # Log system info
            system_info = self.docker_client.info()
            self.logger.info(f"Docker containers running: {system_info.get('ContainersRunning', 0)}")
            self.logger.info(f"Docker images: {system_info.get('Images', 0)}")

        except Exception as e:
            self.log_exception("log_docker_info", e)

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def wait_for_input(self, prompt: str = "Press Enter to continue..."):
        """Wait for user input"""
        input(f"{Colors.CYAN}{prompt}{Colors.END}")

    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """Get user choice with validation"""
        while True:
            try:
                choice = input(f"{Colors.WHITE}{prompt}{Colors.END}").strip().lower()
                if choice in [c.lower() for c in valid_choices]:
                    return choice
                print(f"{Colors.RED}Invalid choice. Please select from: {', '.join(valid_choices)}{Colors.END}")
            except KeyboardInterrupt:
                raise
            except Exception:
                print(f"{Colors.RED}Invalid input, please try again{Colors.END}")

    def detect_existing_deployment(self) -> bool:
        """Check if there's an existing HoneyMesh deployment"""
        # Check for data directory
        if not self.data_dir.exists():
            return False

        # Check for config file
        if not self.config_file.exists():
            return False

        # Check for running containers
        try:
            if not self.docker_client:
                self.docker_client = docker.from_env()
            containers = self.docker_client.containers.list(all=True)
            honeymesh_containers = [c for c in containers if any(service_name in c.name for service_name in self.services.values())]
            return len(honeymesh_containers) > 0
        except DockerException:
            return False

    def get_all_honeymesh_deployments(self) -> Dict[str, List]:
        """
        Detect all HoneyMesh deployments (default + medium interaction)

        Returns:
            Dict with deployment names as keys and list of containers as values
        """
        deployments = {}

        try:
            if not self.docker_client:
                self.docker_client = docker.from_env()

            containers = self.docker_client.containers.list(all=True)

            # Find all honeymesh containers
            for container in containers:
                if 'honeymesh' in container.name.lower():
                    # Parse deployment name from container name
                    # Pattern: honeymesh-<service>-<deployment> or honeymesh-<service>
                    parts = container.name.split('-', 2)

                    if len(parts) >= 3:
                        # Medium interaction: honeymesh-elasticsearch-epic-prod-01
                        deployment_name = parts[2]
                    elif len(parts) == 2:
                        # Default deployment: honeymesh-cowrie
                        deployment_name = 'default'
                    else:
                        continue

                    if deployment_name not in deployments:
                        deployments[deployment_name] = []

                    deployments[deployment_name].append(container)

        except DockerException as e:
            self.logger.error(f"Error detecting deployments: {e}")

        return deployments

    def get_container_status(self, deployment_name: str = 'default') -> Dict[str, Dict]:
        """
        Get status of HoneyMesh containers for a specific deployment

        Args:
            deployment_name: Name of deployment ('default' for default deployment)

        Returns:
            Dict with service names as keys and status info as values
        """
        status = {}
        try:
            if not self.docker_client:
                self.docker_client = docker.from_env()

            # Get all containers for this deployment
            all_deployments = self.get_all_honeymesh_deployments()

            if deployment_name not in all_deployments:
                return status

            deployment_containers = all_deployments[deployment_name]

            # Map containers to services
            for container in deployment_containers:
                # Determine service type from container name
                service_type = self._extract_service_type(container.name, deployment_name)

                if service_type:
                    status[service_type] = {
                        'name': container.name,
                        'status': container.status,
                        'health': self.check_container_health(container),
                        'ports': self.get_container_ports(container)
                    }

        except DockerException as e:
            self.print_status(f"Error accessing Docker: {str(e)}", "error")

        return status

    def _extract_service_type(self, container_name: str, deployment_name: str) -> Optional[str]:
        """
        Extract service type from container name

        Args:
            container_name: Full container name
            deployment_name: Deployment name

        Returns:
            Service type string or None
        """
        # Remove 'honeymesh-' prefix and deployment suffix
        name_lower = container_name.lower()

        if deployment_name == 'default':
            # Pattern: honeymesh-<service>
            if 'elasticsearch' in name_lower:
                return 'elasticsearch'
            elif 'kibana' in name_lower:
                return 'kibana'
            elif 'logstash' in name_lower:
                return 'logstash'
            elif 'filebeat' in name_lower:
                return 'filebeat'
            elif 'cowrie' in name_lower:
                return 'cowrie'
        else:
            # Pattern: honeymesh-<service>-<deployment> or honeymesh-<deployment>
            # For medium interaction, the cowrie container is: honeymesh-<deployment>
            if f'honeymesh-{deployment_name}' == name_lower and 'elasticsearch' not in name_lower and 'kibana' not in name_lower:
                return 'cowrie'
            elif 'elasticsearch' in name_lower:
                return 'elasticsearch'
            elif 'kibana' in name_lower:
                return 'kibana'
            elif 'logstash' in name_lower:
                return 'logstash'
            elif 'filebeat' in name_lower:
                return 'filebeat'

        return None

    def check_container_health(self, container) -> str:
        """Check if a container is healthy"""
        try:
            if container.status != 'running':
                return 'unhealthy'

            # For containers without health checks, we'll do basic connectivity tests
            if 'elasticsearch' in container.name:
                return self.check_elasticsearch_health()
            elif 'kibana' in container.name:
                return self.check_kibana_health()
            elif 'cowrie' in container.name:
                return self.check_cowrie_health()
            elif 'logstash' in container.name:
                return self.check_logstash_health()
            elif 'filebeat' in container.name:
                return self.check_filebeat_health()
            else:
                return 'healthy' if container.status == 'running' else 'unhealthy'
        except:
            return 'unknown'

    def get_container_ports(self, container) -> Dict:
        """Get port mappings for a container"""
        try:
            ports = {}
            if container.ports:
                for internal_port, external_port in container.ports.items():
                    if external_port:
                        ports[internal_port] = external_port[0]['HostPort']
            return ports
        except:
            return {}

    def check_elasticsearch_health(self) -> str:
        """Check Elasticsearch health via HTTP"""
        try:
            import requests
            response = requests.get('http://localhost:9200/_cluster/health', timeout=5)
            return 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            return 'unhealthy'

    def check_kibana_health(self) -> str:
        """Check Kibana health"""
        try:
            import requests
            kibana_port = self.config.get('kibana_port', 5601)
            response = requests.get(f'http://localhost:{kibana_port}/api/status', timeout=5)
            return 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            return 'unhealthy'

    def check_cowrie_health(self) -> str:
        """Check Cowrie health by testing SSH port"""
        try:
            ssh_port = self.config.get('ssh_port', 2222)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex(('localhost', ssh_port))
                return 'healthy' if result == 0 else 'unhealthy'
        except:
            return 'unhealthy'

    def check_logstash_health(self) -> str:
        """Check Logstash health"""
        try:
            import requests
            response = requests.get('http://localhost:9600/_node/stats', timeout=5)
            return 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            return 'unhealthy'

    def check_filebeat_health(self) -> str:
        """Check Filebeat health - filebeat doesn't have a status endpoint"""
        # For filebeat, we just check if container is running since it doesn't have an HTTP endpoint
        return 'healthy'

    def show_main_menu(self):
        """Display the main menu based on deployment detection"""
        while True:  # ← ADD THIS LINE
            self.clear_screen()
            self.print_banner()

            # Check for ANY HoneyMesh deployments (default or medium interaction)
            all_deployments = self.get_all_honeymesh_deployments()
            existing_deployment = len(all_deployments) > 0

            if existing_deployment:
                print(f"{Colors.BOLD}Existing HoneyMesh deployment detected in {self.data_dir}{Colors.END}\n")
                print("Select an option:")
                print(f"{Colors.GREEN}[M]{Colors.END} Manage existing deployment")
                print(f"{Colors.BLUE}[N]{Colors.END} Create new deployment")
                print(f"{Colors.RED}[R]{Colors.END} Remove existing & start fresh")
                print(f"{Colors.WHITE}[Q]{Colors.END} Quit")

                choice = self.get_user_choice("\nEnter your choice: ", ['M', 'N', 'R', 'Q'])

                if choice == 'm':
                    self.management_console()
                elif choice == 'n':
                    self.create_new_deployment()
                elif choice == 'r':
                    self.remove_existing_deployment()
                elif choice == 'q':
                    self.quit_application()
            else:
                print("Select Honeypot Configuration:\n")
                print(f"{Colors.GREEN}[1]{Colors.END} Default (SSH + Telnet)")
                print(f"{Colors.GREEN}[2]{Colors.END} Medium Interaction")
                print(f"{Colors.YELLOW}[3]{Colors.END} High Interaction (Coming Soon)")
                print(f"{Colors.WHITE}[Q]{Colors.END} Quit")

                choice = self.get_user_choice("\nEnter your choice: ", ['1', '2', '3', 'Q'])

                if choice == '1':
                    self.deploy_default_environment()
                    # After deployment, continues the while loop
                elif choice == '2':
                    self.deploy_medium_interaction()
                    # After medium returns, continues the while loop ← THIS FIXES IT
                elif choice == '3':
                    self.show_coming_soon()
                elif choice == 'q':
                    self.quit_application()

    def show_coming_soon(self):
        """Display coming soon message"""
        self.clear_screen()
        print(f"{Colors.CYAN}Feature Coming Soon{Colors.END}\n")
        print("This feature is currently under development and will be available in a future release.")
        print("Stay tuned for updates!")
        self.wait_for_input("\nPress Enter to return to main menu...")
        self.show_main_menu()

    def check_system_requirements(self) -> bool:
        """Check if system meets requirements for deployment"""
        self.print_status("Checking system requirements...", "info")
        time.sleep(1)

        requirements_passed = True

        # Check Docker installation
        try:
            self.docker_client = docker.from_env()
            docker_version = self.docker_client.version()['Version']
            self.print_status(f"Docker version {docker_version} detected", "success")
        except DockerException as e:
            self.print_status("Docker not found or not running", "error")
            print(f"  {Colors.RED}Error: {str(e)}{Colors.END}")
            requirements_passed = False

        # Check available disk space
        try:
            disk_usage = shutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            if free_gb >= 5:
                self.print_status(f"Available disk space: {free_gb:.1f}GB", "success")
            else:
                self.print_status(f"Insufficient disk space: {free_gb:.1f}GB (minimum 5GB required)", "error")
                requirements_passed = False
        except Exception as e:
            self.print_status("Could not check disk space", "warning")

        # Check port availability
        ports_to_check = [2222, 2223, 5601, 9200]
        for port in ports_to_check:
            if self.is_port_available(port):
                self.print_status(f"Port {port} available", "success")
            else:
                self.print_status(f"Port {port} is in use", "error")
                requirements_passed = False

        return requirements_passed

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except socket.error:
            return False

    def get_deployment_config(self) -> Dict:
        """Get deployment configuration from user"""
        config = {}

        print(f"\n{Colors.BOLD}SSH Honeypot Setup:{Colors.END}")
        config['ssh_port'] = self.get_port_input("Port number", 2222)
        config['ssh_enabled'] = self.get_yes_no_input("Enable SSH service", True)

        print(f"\n{Colors.BOLD}Telnet Honeypot Setup:{Colors.END}")
        config['telnet_enabled'] = self.get_yes_no_input("Enable Telnet", False)
        if config['telnet_enabled']:
            config['telnet_port'] = self.get_port_input("Telnet port number", 2223)
        else:
            config['telnet_port'] = None

        print(f"\n{Colors.BOLD}System Identity:{Colors.END}")
        while True:
            hostname_input = input(f"Hostname [ubuntu-server]: ").strip()
            hostname = hostname_input if hostname_input else "ubuntu-server"

            # Validate hostname
            if not all(c.isalnum() or c in '.-_' for c in hostname):
                print(f"{Colors.RED}Hostname can only contain letters, numbers, dots, hyphens, and underscores{Colors.END}")
                continue

            if len(hostname) > 253:
                print(f"{Colors.RED}Hostname too long (max 253 characters){Colors.END}")
                continue

            config['hostname'] = hostname
            break

        config['ssh_banner'] = input(f"SSH banner [SSH-2.0-OpenSSH_7.4]: ").strip() or "SSH-2.0-OpenSSH_7.4"

        print(f"\n{Colors.BOLD}Dashboard Access:{Colors.END}")
        config['kibana_port'] = self.get_port_input("Kibana port", 5601)
        config['external_access'] = self.get_yes_no_input("Allow external access (WARNING: Security risk)", False)

        print(f"\n{Colors.BOLD}Storage Settings:{Colors.END}")
        while True:
            data_dir_input = input(f"Data directory [./honeypot-data]: ").strip()
            data_dir = data_dir_input if data_dir_input else "./honeypot-data"

            # Basic path validation
            if any(c in data_dir for c in ['<', '>', '|', '\0']):
                print(f"{Colors.RED}Invalid characters in path{Colors.END}")
                continue

            config['data_directory'] = data_dir
            break

        config['log_retention_days'] = self.get_number_input("Log retention days", 30)

        return config

    def get_port_input(self, prompt: str, default: int) -> int:
        """Get port number from user with validation - checks for actual conflicts"""
        suggested_port = default

        # Find an available port starting from default
        if not self.is_port_available(default):
            for offset in range(1, 100):
                candidate = default + offset
                if 1 <= candidate <= 65535 and self.is_port_available(candidate):
                    suggested_port = candidate
                    break

        while True:
            try:
                # Show suggestion if different from default
                if suggested_port != default:
                    display_prompt = f"{prompt} [suggested: {suggested_port}, default was {default}]"
                else:
                    display_prompt = f"{prompt} [{default}]"

                port_str = input(f"{display_prompt}: ").strip()

                # Use suggested port if user presses enter
                if not port_str:
                    port = suggested_port
                else:
                    port = int(port_str)

                # Validate port range (OS limitation)
                if not (1 <= port <= 65535):
                    print(f"{Colors.RED}Port must be between 1 and 65535{Colors.END}")
                    continue

                # Check if port is already in use
                if not self.is_port_available(port):
                    print(f"{Colors.RED}Port {port} is already in use{Colors.END}")
                    # Find next available port
                    for offset in range(1, 100):
                        candidate = port + offset
                        if 1 <= candidate <= 65535 and self.is_port_available(candidate):
                            suggested_port = candidate
                            print(f"{Colors.YELLOW}Suggestion: Try port {suggested_port} (press Enter to use it){Colors.END}")
                            break
                    else:
                        print(f"{Colors.YELLOW}Choose a different port or stop the service using it{Colors.END}")
                    continue

                # Port is valid and available
                if port < 1024:
                    print(f"{Colors.YELLOW}Note: Port {port} is privileged (Docker will handle this){Colors.END}")

                return port

            except ValueError:
                print(f"{Colors.RED}Please enter a valid port number{Colors.END}")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"{Colors.RED}Invalid input: {str(e)}{Colors.END}")

    def get_yes_no_input(self, prompt: str, default: bool) -> bool:
        """Get yes/no input from user"""
        default_str = "Y/n" if default else "y/N"
        while True:
            try:
                choice = input(f"{prompt} [{default_str}]: ").strip().lower()
                if not choice:
                    return default
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no']:
                    return False
                else:
                    print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")
            except KeyboardInterrupt:
                raise
            except Exception:
                print(f"{Colors.RED}Invalid input, please try again{Colors.END}")

    def get_number_input(self, prompt: str, default: int) -> int:
        """Get number input from user with validation"""
        while True:
            try:
                number_str = input(f"{prompt} [{default}]: ").strip()
                if not number_str:
                    return default
                num = int(number_str)
                if num < 0:
                    print(f"{Colors.RED}Please enter a positive number{Colors.END}")
                    continue
                return num
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number{Colors.END}")
            except KeyboardInterrupt:
                raise
            except Exception:
                print(f"{Colors.RED}Invalid input, please try again{Colors.END}")

    def show_deployment_summary(self, config: Dict) -> bool:
        """Show deployment summary and get confirmation"""
        self.clear_screen()
        print(f"{Colors.BOLD}Deployment Summary{Colors.END}\n")
        print("─" * 40)
        print(f"SSH Honeypot      → Port {config['ssh_port']}")
        if config['telnet_enabled']:
            print(f"Telnet Honeypot   → Port {config['telnet_port']}")
        else:
            print(f"Telnet Honeypot   → Disabled")
        print(f"Kibana Dashboard  → Port {config['kibana_port']}")
        print(f"Hostname          → {config['hostname']}")
        print(f"Storage           → {config['data_directory']}")
        print(f"Est. Disk Usage   → ~500MB initial")
        print("─" * 40)

        print(f"\n{Colors.GREEN}[D]{Colors.END} Deploy")
        print(f"{Colors.YELLOW}[M]{Colors.END} Modify")
        print(f"{Colors.BLUE}[S]{Colors.END} Save Config")
        print(f"{Colors.WHITE}[Q]{Colors.END} Quit")

        choice = self.get_user_choice("\nEnter your choice: ", ['D', 'M', 'S', 'Q'])

        if choice == 'd':
            return True
        elif choice == 'm':
            return False
        elif choice == 's':
            self.save_config(config)
            return self.show_deployment_summary(config)
        elif choice == 'q':
            self.quit_application()

    def deploy_medium_interaction(self):
        """Deploy medium interaction honeypot"""
        try:
            if not self.medium_manager:
                self.medium_manager = MediumDeploymentManager(self)

            self.medium_manager.show_medium_deployment_menu()

        except Exception as e:
            self.print_status(f"Medium interaction error: {str(e)}", "error")
            self.log_exception("deploy_medium_interaction", e)
            self.wait_for_input()
            self.show_main_menu()

    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            self.data_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.print_status(f"Configuration saved to {self.config_file}", "success")
        except Exception as e:
            self.print_status(f"Failed to save configuration: {str(e)}", "error")
        self.wait_for_input()

    def deploy_default_environment(self):
        """Main deployment workflow for default environment"""
        self.clear_screen()
        self.print_status("Starting default honeypot deployment", "info")

        # Check system requirements
        if not self.check_system_requirements():
            print(f"\n{Colors.RED}System requirements not met.{Colors.END}")
            choice = self.get_user_choice("Retry system check? [R] or return to menu [M]: ", ['R', 'M'])
            if choice == 'r':
                self.deploy_default_environment()
            else:
                self.show_main_menu()
            return

        # Get configuration
        while True:
            self.config = self.get_deployment_config()
            if self.show_deployment_summary(self.config):
                break
            # If user chose modify, loop back to get config again

        # Perform deployment
        if self.perform_deployment():
            self.show_deployment_success()
        else:
            self.show_deployment_failure()

    def perform_deployment(self) -> bool:
        """Execute the actual deployment"""
        self.clear_screen()
        print(f"{Colors.BOLD}Deploying HoneyMesh Environment{Colors.END}\n")

        try:
            self.logger.info("=== Starting HoneyMesh deployment ===")
            self.logger.info(f"Configuration: {json.dumps(self.config, indent=2)}")

            # Log Docker environment
            self.log_docker_info()

            # Create directories
            self.print_status("Creating data directories...", "info")
            self.create_deployment_directories()
            time.sleep(1)
            self.print_status("Data directories created", "success")

            # Generate configuration files
            self.print_status("Generating configuration files...", "info")
            self.generate_config_files()
            time.sleep(1)
            self.print_status("Configuration files generated", "success")

            # Save configuration
            self.save_config(self.config)

            # Pull Docker images
            self.print_status("Pulling Docker images (this may take a few minutes)...", "info")
            self.pull_docker_images()
            self.print_status("Docker images ready", "success")

            # Start services using docker-compose
            self.start_services_with_docker_compose()
            self.print_status("All services started successfully", "success")

            # Final verification
            self.print_status("Performing final verification...", "info")
            time.sleep(2)
            status = self.get_container_status()

            all_healthy = all(s.get('health') == 'healthy' for s in status.values())
            if all_healthy:
                self.print_status("All services verified and healthy", "success")
                self.logger.info("Deployment completed successfully")
                return True
            else:
                self.print_status("Some services may not be fully ready yet", "warning")
                self.logger.warning("Some services not fully healthy, but deployment considered successful")
                return True  # Still consider successful, services might need more time

        except Exception as e:
            self.log_exception("perform_deployment", e)
            self.print_status(f"Deployment failed: {str(e)}", "error")
            self.print_status(f"Check logs at: {self.current_log_file}", "info")

            # Log current container states
            try:
                self.logger.info("=== Container states at failure ===")
                all_containers = self.docker_client.containers.list(all=True)
                for container in all_containers:
                    if any(service_name in container.name for service_name in self.services.values()):
                        self.logger.info(f"Container: {container.name}, Status: {container.status}")
                        logs = container.logs(tail=20).decode('utf-8', errors='ignore')
                        self.logger.info(f"Recent logs for {container.name}:\n{logs}")
            except Exception as log_error:
                self.logger.error(f"Could not log container states: {log_error}")

            # Attempt cleanup on failure
            try:
                self.stop_services()
            except:
                pass

            return False

    def create_deployment_directories(self):
        """Create necessary directories for deployment"""
        directories = [
            self.data_dir,
            self.data_dir / "logs",
            self.data_dir / "elasticsearch",
            self.data_dir / "kibana",
            self.data_dir / "logstash",
            self.data_dir / "cowrie" / "config",
            self.data_dir / "cowrie" / "var" / "log" / "cowrie",
            self.data_dir / "cowrie" / "var" / "lib" / "cowrie" / "downloads",
            self.data_dir / "cowrie" / "var" / "lib" / "cowrie" / "tty",
            self.data_dir / "elk-config" / "logstash",
            self.data_dir / "elk-config" / "filebeat"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Set proper permissions for Cowrie directories
        self.set_cowrie_permissions()

        # Create user database files for Cowrie
        self.create_cowrie_user_files()

    def create_cowrie_user_files(self):
        """Create user database files for Cowrie authentication"""
        try:
            # Create userdb.txt file for Cowrie authentication
            userdb_content = """root:x:123456
admin:x:123456
user:x:123456
test:x:test
guest:x:guest
"""

            userdb_file = self.data_dir / "cowrie" / "config" / "userdb.txt"
            with open(userdb_file, 'w') as f:
                f.write(userdb_content)

            # Set proper permissions
            userdb_file.chmod(0o644)

            self.logger.info("Cowrie user database created successfully")
            self.print_status("Cowrie user database created", "success")

        except Exception as e:
            self.logger.error(f"Failed to create Cowrie user files: {e}")
            self.print_status(f"Failed to create user files: {str(e)}", "error")
            raise

    def set_cowrie_permissions(self):
        """Set proper permissions for Cowrie directories"""
        try:
            import subprocess

            # The Cowrie container typically runs as UID 1000 or needs write access
            # Set ownership and permissions for Cowrie directories
            cowrie_dirs = [
                self.data_dir / "cowrie",
                self.data_dir / "logs"
            ]

            for cowrie_dir in cowrie_dirs:
                if cowrie_dir.exists():
                    # Make directories writable by the cowrie user (typically UID 1000)
                    # Use chmod to make directories writable
                    subprocess.run(['chmod', '-R', '777', str(cowrie_dir)],
                                 capture_output=True, text=True, check=False)
                    self.logger.info(f"Set permissions for {cowrie_dir}")

            self.print_status("Set proper permissions for Cowrie directories", "success")

        except Exception as e:
            self.logger.error(f"Failed to set Cowrie permissions: {e}")
            self.print_status(f"Warning: Could not set permissions: {str(e)}", "warning")

    def create_cowrie_filesystem_files(self):
        """Create essential filesystem files that Cowrie needs"""
        try:
            # Create passwd file
            passwd_content = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
uuidd:x:105:109::/run/uuidd:/usr/sbin/nologin
avahi-autoipd:x:106:110:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/usr/sbin/nologin
usbmux:x:107:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
dnsmasq:x:108:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
rtkit:x:109:114:RealtimeKit,,,:/proc:/usr/sbin/nologin
cups-pk-helper:x:110:116:user for cups-pk-helper service,,,:/home/cups-pk-helper:/usr/sbin/nologin
speech-dispatcher:x:111:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/false
whoopsie:x:112:117::/nonexistent:/bin/false
kernoops:x:113:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin
saned:x:114:119::/var/lib/saned:/usr/sbin/nologin
pulse:x:115:120:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
avahi:x:116:122:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
colord:x:117:123:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
hplip:x:118:7:HPLIP system user,,,:/var/run/hplip:/bin/false
geoclue:x:119:124::/var/lib/geoclue:/usr/sbin/nologin
gnome-initial-setup:x:120:65534::/run/gnome-initial-setup/:/bin/false
gdm:x:121:125:Gnome Display Manager:/var/lib/gdm3:/bin/false
user:x:1000:1000:user,,,:/home/user:/bin/bash
admin:x:1001:1001:admin,,,:/home/admin:/bin/bash
"""

            passwd_file = self.data_dir / "cowrie" / "honeyfs" / "etc" / "passwd"
            with open(passwd_file, 'w') as f:
                f.write(passwd_content)

            # Create group file
            group_content = """root:x:0:
daemon:x:1:
bin:x:2:
sys:x:3:
adm:x:4:syslog,user
tty:x:5:
disk:x:6:
lp:x:7:
mail:x:8:
news:x:9:
uucp:x:10:
man:x:12:
proxy:x:13:
kmem:x:15:
dialout:x:20:user
fax:x:21:
voice:x:22:
cdrom:x:24:user
floppy:x:25:user
tape:x:26:
sudo:x:27:user
audio:x:29:pulse,user
dip:x:30:user
www-data:x:33:
backup:x:34:
operator:x:37:
list:x:38:
irc:x:39:
src:x:40:
gnats:x:41:
shadow:x:42:
utmp:x:43:
video:x:44:user
sasl:x:45:
plugdev:x:46:user
staff:x:50:
games:x:60:
users:x:100:
nogroup:x:65534:
systemd-journal:x:101:
systemd-network:x:102:
systemd-resolve:x:103:
input:x:104:
crontab:x:105:
syslog:x:106:
messagebus:x:107:
netdev:x:108:
uuidd:x:109:
avahi-autoipd:x:110:
bluetooth:x:111:
scanner:x:112:saned
colord:x:113:
pulse:x:114:
pulse-access:x:115:
gdm:x:116:
lpadmin:x:117:user
user:x:1000:
admin:x:1001:
"""

            group_file = self.data_dir / "cowrie" / "honeyfs" / "etc" / "group"
            with open(group_file, 'w') as f:
                f.write(group_content)

            # Create shadow file
            shadow_content = """root:*:17000:0:99999:7:::
daemon:*:17000:0:99999:7:::
bin:*:17000:0:99999:7:::
sys:*:17000:0:99999:7:::
sync:*:17000:0:99999:7:::
games:*:17000:0:99999:7:::
man:*:17000:0:99999:7:::
lp:*:17000:0:99999:7:::
mail:*:17000:0:99999:7:::
news:*:17000:0:99999:7:::
uucp:*:17000:0:99999:7:::
proxy:*:17000:0:99999:7:::
www-data:*:17000:0:99999:7:::
backup:*:17000:0:99999:7:::
list:*:17000:0:99999:7:::
irc:*:17000:0:99999:7:::
gnats:*:17000:0:99999:7:::
nobody:*:17000:0:99999:7:::
systemd-network:*:17000:0:99999:7:::
systemd-resolve:*:17000:0:99999:7:::
syslog:*:17000:0:99999:7:::
messagebus:*:17000:0:99999:7:::
_apt:*:17000:0:99999:7:::
uuidd:*:17000:0:99999:7:::
user:$6$rounds=656000$YQKJLk.j1ajqhDx/$Dq9YloqmBXNbvGJYKjfCGK7x6l.zpRNKs6hb7XWE56.CSSyGCqFYZzLLxTNEXiYa4NwOEA9zX6.VgdQXpgTQy.:17000:0:99999:7:::
admin:$6$rounds=656000$YQKJLk.j1ajqhDx/$Dq9YloqmBXNbvGJYKjfCGK7x6l.zpRNKs6hb7XWE56.CSSyGCqFYZzLLxTNEXiYa4NwOEA9zX6.VgdQXpgTQy.:17000:0:99999:7:::
"""

            shadow_file = self.data_dir / "cowrie" / "honeyfs" / "etc" / "shadow"
            with open(shadow_file, 'w') as f:
                f.write(shadow_content)

            # Create basic shell scripts and binaries simulation
            self.create_basic_commands()

            self.logger.info("Cowrie filesystem files created successfully")
            self.print_status("Cowrie filesystem files created", "success")

        except Exception as e:
            self.logger.error(f"Failed to create Cowrie filesystem files: {e}")
            self.print_status(f"Failed to create filesystem files: {str(e)}", "error")
            raise

    def create_basic_commands(self):
        """Create basic command files for the honeypot"""
        try:
            # Create bin directory files (fake commands)
            bin_commands = ['ls', 'cat', 'pwd', 'whoami', 'id', 'uname', 'ps', 'netstat', 'ifconfig', 'wget', 'curl']

            bin_dir = self.data_dir / "cowrie" / "honeyfs" / "bin"
            usr_bin_dir = self.data_dir / "cowrie" / "honeyfs" / "usr" / "bin"

            for cmd in bin_commands:
                # Create fake command files (empty files are sufficient for Cowrie)
                bin_file = bin_dir / cmd
                usr_bin_file = usr_bin_dir / cmd

                bin_file.touch()
                usr_bin_file.touch()

                # Make them executable
                bin_file.chmod(0o755)
                usr_bin_file.chmod(0o755)

            # Create some basic directories that programs expect
            home_dirs = ['user', 'admin']
            for home_dir in home_dirs:
                home_path = self.data_dir / "cowrie" / "honeyfs" / "home" / home_dir
                home_path.mkdir(parents=True, exist_ok=True)

            # Create root home directory
            root_home = self.data_dir / "cowrie" / "honeyfs" / "root"
            root_home.mkdir(parents=True, exist_ok=True)

            # Set permissions on all created files
            self.set_file_permissions()

            self.logger.info("Basic command files created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create basic commands: {e}")
            raise

    def set_file_permissions(self):
        """Set proper permissions on all created files"""
        try:
            import subprocess

            # Set permissions on the honeyfs directory and contents
            honeyfs_path = self.data_dir / "cowrie" / "honeyfs"
            if honeyfs_path.exists():
                subprocess.run(['chmod', '-R', '755', str(honeyfs_path)],
                             capture_output=True, text=True, check=False)

            # Make specific files readable
            files_to_fix = [
                self.data_dir / "cowrie" / "honeyfs" / "etc" / "passwd",
                self.data_dir / "cowrie" / "honeyfs" / "etc" / "group",
                self.data_dir / "cowrie" / "honeyfs" / "etc" / "shadow"
            ]

            for file_path in files_to_fix:
                if file_path.exists():
                    subprocess.run(['chmod', '644', str(file_path)],
                                 capture_output=True, text=True, check=False)

            self.logger.info("File permissions set successfully")

        except Exception as e:
            self.logger.error(f"Failed to set file permissions: {e}")

    def generate_config_files(self):
        """Generate configuration files for all services"""
        # Generate docker-compose.yml
        docker_compose_content = self.get_docker_compose_template()
        with open(self.docker_compose_file, 'w') as f:
            f.write(docker_compose_content)

        # Generate Logstash configuration
        self.generate_logstash_config()

        # Generate Filebeat configuration
        self.generate_filebeat_config()

        # Generate Cowrie configuration
        self.generate_cowrie_config()

    def generate_logstash_config(self):
        """Generate Logstash pipeline configuration"""
        logstash_config = """
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][honeypot] == "cowrie" {
    # Parse timestamp if present
    if [timestamp] {
      date {
        match => [ "timestamp", "ISO8601" ]
      }
    }

    # Add GeoIP data if source IP present
    if [src_ip] {
      geoip {
        source => "src_ip"
        target => "geoip"
      }
    }

    # Clean up fields
    mutate {
      remove_field => [ "@version", "host", "agent", "ecs", "log", "input" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "cowrie-%{+YYYY.MM.dd}"
  }

  stdout {
    codec => rubydebug
  }
}
"""

        pipeline_path = self.data_dir / "elk-config" / "logstash" / "logstash.conf"
        self.logger.info(f"Writing Logstash config to: {pipeline_path}")

        try:
            # Ensure directory exists
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)

            with open(pipeline_path, 'w') as f:
                f.write(logstash_config.strip())

            self.logger.info(f"Logstash config written successfully")

        except Exception as e:
            self.logger.error(f"Failed to write Logstash config: {e}")
            raise

    def generate_cowrie_config(self):
        """Generate Cowrie configuration"""
        cowrie_config = f"""[honeypot]
hostname = {self.config.get('hostname', 'ubuntu-server')}
log_path = /cowrie/var/log/cowrie
download_path = /cowrie/var/lib/cowrie/downloads
state_path = /cowrie/var/lib/cowrie
contents_path = honeyfs
ttylog_path = /cowrie/var/lib/cowrie/tty

[ssh]
enabled = {'true' if self.config.get('ssh_enabled', True) else 'false'}
listen_endpoints = tcp:2222:interface=0.0.0.0
version = {self.config.get('ssh_banner', 'SSH-2.0-OpenSSH_7.4')}

[telnet]
enabled = {'true' if self.config.get('telnet_enabled', False) else 'false'}
listen_endpoints = tcp:2223:interface=0.0.0.0

[shell]
filesystem = src/cowrie/data/fs.pickle
processes = src/cowrie/data/cmdoutput.json

[output_jsonlog]
enabled = true
logfile = /cowrie/var/log/cowrie/cowrie.json
epoch_timestamp = false

[backend_pool]
pool_only = false

[proxy]
enabled = false
"""

        # Write the configuration to the cowrie.cfg file
        config_path = self.data_dir / "cowrie" / "config" / "cowrie.cfg"
        self.logger.info(f"Writing Cowrie config to: {config_path}")

        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                f.write(cowrie_config.strip())

            self.logger.info(f"Cowrie config written successfully")
            self.print_status(f"Cowrie configuration created at {config_path}", "success")

        except Exception as e:
            self.logger.error(f"Failed to write Cowrie config: {e}")
            self.print_status(f"Failed to write Cowrie config: {str(e)}", "error")
            raise

    def generate_filebeat_config(self):
        """Generate Filebeat configuration"""
        filebeat_config = f"""
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/cowrie/cowrie.json*
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    honeypot: cowrie
  fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded

logging.level: info
logging.to_files: true
logging.files:
  path: /usr/share/filebeat/logs
  name: filebeat
  keepfiles: 7
  permissions: 0644
"""

        config_path = self.data_dir / "elk-config" / "filebeat" / "filebeat.yml"
        with open(config_path, 'w') as f:
            f.write(filebeat_config.strip())

    def get_docker_compose_template(self) -> str:
        """Generate docker-compose.yml content based on configuration"""
        telnet_port_mapping = ""
        if self.config.get('telnet_enabled', False):
            telnet_port_mapping = f"      - \"{self.config['telnet_port']}:2223\""

        kibana_bind = "127.0.0.1" if not self.config.get('external_access', False) else "0.0.0.0"

        template = f"""version: '3.8'

networks:
  honeymesh:
    driver: bridge

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: honeymesh-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
      - xpack.security.enrollment.enabled=false
      - cluster.name=honeymesh-cluster
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - ./elasticsearch:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - honeymesh
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: honeymesh-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - SERVER_NAME=honeymesh-kibana
      - SERVER_HOST=0.0.0.0
    volumes:
      - ./kibana:/usr/share/kibana/data
    ports:
      - "{kibana_bind}:{self.config['kibana_port']}:5601"
    depends_on:
      - elasticsearch
    networks:
      - honeymesh
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5601/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: honeymesh-logstash
    environment:
      - "LS_JAVA_OPTS=-Xms256m -Xmx256m"
    volumes:
      - ./logstash:/usr/share/logstash/data
      - ./elk-config/logstash:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
      - "9600:9600"
    depends_on:
      - elasticsearch
    networks:
      - honeymesh
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9600/_node/stats || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  cowrie:
    image: cowrie/cowrie:latest
    container_name: honeymesh-cowrie
    user: "1000:1000"
    ports:
      - "{self.config['ssh_port']}:2222"
{telnet_port_mapping}
    volumes:
      - ./cowrie/config:/cowrie/cowrie-git/etc
      - ./cowrie/var:/cowrie/var
    networks:
      - honeymesh
    restart: unless-stopped

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: honeymesh-filebeat
    user: root
    command: filebeat -e --strict.perms=false
    volumes:
      - ./elk-config/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./cowrie/var/log/cowrie:/var/log/cowrie:ro
    depends_on:
      - logstash
      - cowrie
    networks:
      - honeymesh
    restart: unless-stopped
"""
        return template

    def pull_docker_images(self):
        """Pull required Docker images with progress tracking"""
        images = [
            "docker.elastic.co/elasticsearch/elasticsearch:8.11.0",
            "docker.elastic.co/logstash/logstash:8.11.0",
            "docker.elastic.co/kibana/kibana:8.11.0",
            "docker.elastic.co/beats/filebeat:8.11.0",
            "cowrie/cowrie:latest"
        ]

        for image in images:
            try:
                self.print_status(f"Pulling {image}...", "info")
                self.docker_client.images.pull(image)
                self.print_status(f"Successfully pulled {image}", "success")
            except DockerException as e:
                raise Exception(f"Failed to pull image {image}: {str(e)}")

    def start_services_with_docker_compose(self) -> bool:
        """Start services using docker-compose"""
        try:
            self.logger.info("Starting docker-compose deployment")

            # Change to data directory
            original_dir = os.getcwd()
            self.logger.info(f"Changing directory from {original_dir} to {self.data_dir}")
            os.chdir(self.data_dir)

            # Log docker-compose file contents
            try:
                with open("docker-compose.yml", 'r') as f:
                    compose_content = f.read()
                    self.logger.info("Docker-compose.yml contents:")
                    self.logger.info(compose_content)
            except Exception as e:
                self.logger.error(f"Could not read docker-compose.yml: {e}")

            # Start services with docker-compose
            self.print_status("Starting services with docker-compose...", "info")

            # Start in detached mode
            cmd = ['docker-compose', 'up', '-d']
            self.logger.info(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Log command results
            self.logger.info(f"Command return code: {result.returncode}")
            self.logger.info(f"STDOUT: {result.stdout}")
            self.logger.info(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                self.print_status(f"Docker-compose failed with return code {result.returncode}", "error")
                self.print_status(f"STDERR: {result.stderr}", "error")
                raise Exception(f"docker-compose failed: {result.stderr}")

            # Wait for services to be healthy
            self.wait_for_services_healthy()

            # Set up Kibana index patterns
            self.setup_kibana_index_patterns()

            return True

        except subprocess.TimeoutExpired as e:
            self.log_exception("start_services_with_docker_compose - timeout", e)
            raise Exception("Docker compose startup timed out after 5 minutes")
        except FileNotFoundError as e:
            self.log_exception("start_services_with_docker_compose - file not found", e)
            raise Exception("docker-compose command not found. Please install docker-compose.")
        except Exception as e:
            self.log_exception("start_services_with_docker_compose", e)
            raise Exception(f"Failed to start services: {str(e)}")
        finally:
            os.chdir(original_dir)
            self.logger.info(f"Changed directory back to {original_dir}")

    def wait_for_services_healthy(self, timeout: int = 300):
        """Wait for all services to become healthy"""
        self.logger.info(f"Waiting for services to become healthy (timeout: {timeout}s)")

        start_time = time.time()
        services_to_check = list(self.services.keys())

        self.print_status("Waiting for services to become healthy...", "info")

        while services_to_check and (time.time() - start_time) < timeout:
            self.logger.info(f"Health check iteration - services remaining: {services_to_check}")
            time.sleep(10)

            # Get container status
            try:
                status = self.get_container_status()
                self.logger.info(f"Container status: {json.dumps(status, indent=2)}")
            except Exception as e:
                self.logger.error(f"Error getting container status: {e}")
                continue

            healthy_services = []
            for service in services_to_check:
                if service in status:
                    service_status = status[service]
                    self.logger.info(f"{service}: status={service_status.get('status')}, health={service_status.get('health')}")

                    if service_status.get('health') == 'healthy':
                        healthy_services.append(service)
                        self.print_status(f"{service.capitalize()} is healthy", "success")
                    elif service_status.get('status') == 'exited':
                        self.logger.error(f"{service} container exited - checking logs")
                        self.log_container_logs(service)
                else:
                    self.logger.warning(f"Service {service} not found in container status")

            # Remove healthy services from check list
            for service in healthy_services:
                services_to_check.remove(service)

        if services_to_check:
            unhealthy = ", ".join(services_to_check)
            self.logger.error(f"Services failed to become healthy: {unhealthy}")

            # Log container logs for unhealthy services
            for service in services_to_check:
                self.log_container_logs(service)

            raise Exception(f"Services failed to become healthy within {timeout}s: {unhealthy}")

        self.logger.info("All services are healthy")

    def setup_kibana_index_patterns(self):
        """Automatically create Kibana index patterns for Cowrie data"""
        try:
            import requests
            import time

            self.print_status("Setting up Kibana index patterns...", "info")

            # Wait a bit for Kibana to be fully ready
            time.sleep(30)

            kibana_port = self.config.get('kibana_port', 5601)
            kibana_url = f"http://localhost:{kibana_port}"

            # Check if Kibana is ready
            for attempt in range(5):
                try:
                    response = requests.get(f"{kibana_url}/api/status", timeout=10)
                    if response.status_code == 200:
                        break
                    time.sleep(10)
                except requests.exceptions.RequestException:
                    if attempt == 4:
                        raise
                    time.sleep(10)

            # Create index pattern for Cowrie
            index_pattern_data = {
                "attributes": {
                    "title": "cowrie-*",
                    "timeFieldName": "@timestamp"
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'kbn-xsrf': 'true'
            }

            # Create the index pattern
            response = requests.post(
                f"{kibana_url}/api/saved_objects/index-pattern",
                json=index_pattern_data,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 409]:  # 409 means it already exists
                self.print_status("Kibana index pattern 'cowrie-*' created successfully", "success")
                self.logger.info("Kibana index pattern created successfully")
            else:
                self.print_status(f"Failed to create Kibana index pattern: HTTP {response.status_code}", "warning")
                self.logger.warning(f"Kibana index pattern creation failed: {response.text}")

        except Exception as e:
            self.logger.error(f"Failed to setup Kibana index patterns: {e}")
            self.print_status("Could not auto-create Kibana index patterns - you'll need to create manually", "warning")
            self.print_status("Go to Kibana -> Stack Management -> Index Patterns -> Create 'cowrie-*'", "info")

    def log_container_logs(self, service: str):
        """Log container logs for debugging"""
        try:
            container_name = self.services.get(service, f"honeymesh-{service}")
            self.logger.info(f"=== Container logs for {container_name} ===")

            container = self.docker_client.containers.get(container_name)
            logs = container.logs(tail=50).decode('utf-8', errors='ignore')
            self.logger.info(f"Logs for {container_name}:\n{logs}")

        except Exception as e:
            self.logger.error(f"Could not get logs for {service}: {e}")

    def stop_services(self) -> bool:
        """Stop all HoneyMesh services"""
        try:
            original_dir = os.getcwd()
            os.chdir(self.data_dir)

            self.print_status("Stopping services...", "info")

            result = subprocess.run([
                'docker-compose', 'down'
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                self.print_status(f"Warning: {result.stderr}", "warning")

            self.print_status("Services stopped", "success")
            return True

        except Exception as e:
            self.print_status(f"Error stopping services: {str(e)}", "error")
            return False
        finally:
            os.chdir(original_dir)

    def restart_services(self, deployment_name: str = 'default') -> bool:
        """
        Restart all services for a deployment

        Args:
            deployment_name: Name of deployment to restart

        Returns:
            True if successful, False otherwise
        """
        try:
            original_dir = os.getcwd()

            # Determine deployment directory
            if deployment_name == 'default':
                deploy_dir = self.data_dir
            else:
                deploy_dir = Path("./honeypot-data/medium") / deployment_name

            if not deploy_dir.exists():
                raise Exception(f"Deployment directory not found: {deploy_dir}")

            os.chdir(deploy_dir)

            self.print_status("Restarting services...", "info")

            # Stop services
            subprocess.run(['docker-compose', 'down'], capture_output=True, text=True, timeout=60)
            time.sleep(5)

            # Start services
            result = subprocess.run([
                'docker-compose', 'up', '-d'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise Exception(f"Failed to restart services: {result.stderr}")

            self.print_status("Services restarted successfully", "success")
            return True

        except Exception as e:
            self.print_status(f"Failed to restart services: {str(e)}", "error")
            return False
        finally:
            os.chdir(original_dir)

    def remove_deployment(self, deployment_name: str = 'default') -> bool:
        """
        Remove deployment containers and networks

        Args:
            deployment_name: Name of deployment to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            original_dir = os.getcwd()

            # Determine deployment directory
            if deployment_name == 'default':
                deploy_dir = self.data_dir
            else:
                deploy_dir = Path("./honeypot-data/medium") / deployment_name

            if not deploy_dir.exists():
                self.print_status(f"Deployment directory not found: {deploy_dir}", "warning")
                return True  # Consider it removed if directory doesn't exist

            os.chdir(deploy_dir)

            self.print_status("Removing deployment...", "info")

            # Stop and remove containers, networks
            result = subprocess.run([
                'docker-compose', 'down', '--volumes', '--remove-orphans'
            ], capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                self.print_status(f"Warning during removal: {result.stderr}", "warning")

            # Remove unused images
            try:
                subprocess.run(['docker', 'image', 'prune', '-f'],
                             capture_output=True, text=True, timeout=30)
            except:
                pass  # Not critical if this fails

            self.print_status("Deployment removed successfully", "success")
            return True

        except Exception as e:
            self.print_status(f"Error during removal: {str(e)}", "error")
            return False
        finally:
            os.chdir(original_dir)

    def show_deployment_success(self):
        """Display successful deployment information"""
        self.clear_screen()
        print(f"{Colors.GREEN}{Colors.BOLD}HoneyMesh deployment successful!{Colors.END}\n")

        # Get real-time container status
        status = self.get_container_status()

        print(f"{Colors.BOLD}Service Status:{Colors.END}")
        print("─" * 65)
        print(f"{'Service':<17} {'Status':<12} {'Port':<8} {'Health':<10}")
        print("─" * 65)

        for service, info in status.items():
            service_name = service.replace('_', ' ').title()
            status_color = Colors.GREEN if info['status'] == 'running' else Colors.RED
            health_symbol = "✓" if info['health'] == 'healthy' else "✗"

            # Get main port for display
            main_port = ""
            if service == 'cowrie' and self.config.get('ssh_enabled'):
                main_port = str(self.config['ssh_port'])
            elif service == 'kibana':
                main_port = str(self.config['kibana_port'])
            elif service == 'elasticsearch':
                main_port = "9200"
            elif service == 'logstash':
                main_port = "9600"

            print(f"{service_name:<17} {status_color}{info['status']:<12}{Colors.END} {main_port:<8} {health_symbol}")

        print("─" * 65)

        # Show log pipeline status
        try:
            es_healthy = status.get('elasticsearch', {}).get('health') == 'healthy'
            ls_healthy = status.get('logstash', {}).get('health') == 'healthy'
            pipeline_status = "✓" if es_healthy and ls_healthy else "⚠"
            print(f"\nLog Pipeline: Cowrie → Logstash → Elasticsearch {pipeline_status}")
        except:
            print(f"\nLog Pipeline: Status checking...")

        print(f"\n{Colors.BOLD}Access Your Honeypots:{Colors.END}")
        print(f"• SSH:    ssh user@localhost -p {self.config['ssh_port']}")
        if self.config.get('telnet_enabled'):
            print(f"• Telnet: telnet localhost {self.config['telnet_port']}")

        print(f"\n{Colors.BOLD}Monitor Activity:{Colors.END}")
        print(f"• Dashboard: http://localhost:{self.config['kibana_port']}")
        print(f"• Logs: tail -f {self.data_dir}/logs/cowrie.json")

        print(f"\n{Colors.GREEN}[M]{Colors.END} Management menu")
        print(f"{Colors.WHITE}[E]{Colors.END} Exit")

        choice = self.get_user_choice("\nEnter your choice: ", ['M', 'E'])

        if choice == 'm':
            self.management_console()
        else:
            self.quit_application()

    def show_deployment_failure(self):
        """Display deployment failure information"""
        self.clear_screen()
        print(f"{Colors.RED}{Colors.BOLD}Deployment Failed{Colors.END}\n")
        print("The deployment encountered an error and could not complete successfully.")
        print("Please check the system requirements and try again.")

        print(f"\n{Colors.YELLOW}[R]{Colors.END} Retry deployment")
        print(f"{Colors.BLUE}[M]{Colors.END} Return to main menu")
        print(f"{Colors.WHITE}[Q]{Colors.END} Quit")

        choice = self.get_user_choice("\nEnter your choice: ", ['R', 'M', 'Q'])

        if choice == 'r':
            self.deploy_default_environment()
        elif choice == 'm':
            self.show_main_menu()
        else:
            self.quit_application()

    def management_console(self, selected_deployment: str = None):
        """
        Display the management console

        Args:
            selected_deployment: Name of deployment to manage (None = auto-select)
        """
        # Detect all deployments
        all_deployments = self.get_all_honeymesh_deployments()

        if not all_deployments:
            self.print_status("No HoneyMesh deployments found", "warning")
            self.wait_for_input()
            return

        # If no deployment selected and multiple exist, show selector
        if not selected_deployment and len(all_deployments) > 1:
            selected_deployment = self.select_deployment(all_deployments)
            if not selected_deployment:
                return

        # If still no deployment selected, use first available
        if not selected_deployment:
            selected_deployment = list(all_deployments.keys())[0]

        # Store current deployment
        self.current_deployment = selected_deployment

        while True:
            self.clear_screen()

            # Load existing config if available
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as f:
                        self.config = json.load(f)
                except:
                    pass

            print(f"{Colors.BOLD}HoneyMesh Management Console{Colors.END}\n")

            # Show deployment info
            deployment_type = "Default" if selected_deployment == 'default' else "Medium Interaction"
            print(f"Deployment: {Colors.CYAN}{selected_deployment}{Colors.END} ({deployment_type})")

            # Show real uptime if possible
            try:
                status = self.get_container_status(selected_deployment)
                running_containers = sum(1 for s in status.values() if s['status'] == 'running')
                total_containers = len(status)
                print(f"Running Services: {running_containers}/{total_containers}")
            except:
                print("Status: Checking...")

            # Show option to switch deployment if multiple exist
            if len(all_deployments) > 1:
                print(f"{Colors.YELLOW}[W]{Colors.END} Switch to different deployment")

            print("─" * 40)

            print(f"{Colors.GREEN}[S]{Colors.END} Service status & health")
            print(f"{Colors.BLUE}[L]{Colors.END} Live log monitoring")
            print(f"{Colors.YELLOW}[R]{Colors.END} Restart services")
            print(f"{Colors.CYAN}[C]{Colors.END} Change configuration")
            print(f"{Colors.MAGENTA}[B]{Colors.END} Backup data & config")
            print(f"{Colors.RED}[D]{Colors.END} Stop & remove deployment")
            print(f"{Colors.WHITE}[E]{Colors.END} Exit to main menu")

            valid_choices = ['S', 'L', 'R', 'C', 'B', 'D', 'E']
            if len(all_deployments) > 1:
                valid_choices.append('W')

            choice = self.get_user_choice("\nEnter your choice: ", valid_choices)

            if choice == 's':
                self.show_service_status(selected_deployment)
            elif choice == 'l':
                self.show_live_logs(selected_deployment)
            elif choice == 'r':
                self.restart_services_interactive(selected_deployment)
            elif choice == 'c':
                self.change_configuration()
            elif choice == 'b':
                self.backup_deployment()
            elif choice == 'd':
                if self.stop_and_remove_deployment(selected_deployment):
                    break
            elif choice == 'w' and len(all_deployments) > 1:
                # Switch deployment
                new_deployment = self.select_deployment(all_deployments)
                if new_deployment:
                    selected_deployment = new_deployment
                    self.current_deployment = selected_deployment
            elif choice == 'e':
                self.show_main_menu()
                break

    def select_deployment(self, deployments: Dict[str, List]) -> Optional[str]:
        """
        Show deployment selector menu

        Args:
            deployments: Dict of deployment names to container lists

        Returns:
            Selected deployment name or None
        """
        self.clear_screen()
        print(f"{Colors.BOLD}Select Deployment to Manage{Colors.END}\n")
        print("─" * 70)
        print(f"{'#':<4} {'Name':<30} {'Type':<20} {'Containers':<10}")
        print("─" * 70)

        deployment_list = list(deployments.keys())

        for idx, deployment_name in enumerate(deployment_list, 1):
            deployment_type = "Default" if deployment_name == 'default' else "Medium Interaction"
            container_count = len(deployments[deployment_name])
            running_count = sum(1 for c in deployments[deployment_name] if c.status == 'running')

            print(f"{idx:<4} {deployment_name:<30} {deployment_type:<20} {running_count}/{container_count}")

        print("─" * 70)
        print(f"{Colors.WHITE}[C]{Colors.END} Cancel")

        valid_choices = [str(i) for i in range(1, len(deployment_list) + 1)] + ['C']
        choice = self.get_user_choice("\nSelect deployment number: ", valid_choices)

        if choice == 'c':
            return None

        return deployment_list[int(choice) - 1]

    def show_service_status(self, deployment_name: str = 'default'):
        """
        Show detailed service status

        Args:
            deployment_name: Name of deployment to show status for
        """
        self.clear_screen()
        print(f"{Colors.BOLD}Service Status & Health Details{Colors.END}")
        print(f"Deployment: {deployment_name}\n")

        try:
            status = self.get_container_status(deployment_name)

            if not status:
                self.print_status("No containers found for this deployment", "warning")
            else:
                for service, info in status.items():
                    service_name = service.replace('_', ' ').title()
                    print(f"{Colors.BOLD}{service_name}:{Colors.END}")
                    print(f"  Container: {info['name']}")
                    print(f"  Status: {Colors.GREEN if info['status'] == 'running' else Colors.RED}{info['status']}{Colors.END}")
                    print(f"  Health: {Colors.GREEN if info['health'] == 'healthy' else Colors.YELLOW}{info['health']}{Colors.END}")

                    if info['ports']:
                        print(f"  Ports: {', '.join([f'{k}→{v}' for k, v in info['ports'].items()])}")
                    else:
                        print(f"  Ports: Internal only")
                    print()

        except Exception as e:
            self.print_status(f"Error getting service status: {str(e)}", "error")

        self.wait_for_input()

    def show_live_logs(self, deployment_name: str = 'default'):
        """
        Show live log monitoring with real-time streaming

        Args:
            deployment_name: Name of deployment to show logs for
        """
        self.clear_screen()
        print(f"{Colors.BOLD}Live Log Monitoring{Colors.END}")
        print(f"Deployment: {deployment_name}\n")
        print("Showing recent Cowrie activity (Press Ctrl+C to stop):\n")

        try:
            # Find log file based on deployment type
            if deployment_name == 'default':
                log_file = self.data_dir / "logs" / "cowrie.json"
            else:
                # Medium interaction deployment
                log_file = Path("./honeypot-data/medium") / deployment_name / "log" / "cowrie.json"

            if not log_file.exists():
                print(f"{Colors.YELLOW}No log file found yet. Honeypot may still be starting up.{Colors.END}")
                print(f"Expected location: {log_file}")
                self.wait_for_input("\nPress Enter to return to management console...")
                return

            # Show last 20 lines of history
            print(f"{Colors.BOLD}--- Recent History ---{Colors.END}\n")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines

            for line in recent_lines:
                self._format_and_print_log(line)

            print(f"\n{Colors.BOLD}--- Live Stream (watching for new entries) ---{Colors.END}\n")

            # Start real-time tailing
            stop_event = threading.Event()

            def tail_log_file():
                """Tail the log file and print new lines"""
                try:
                    with open(log_file, 'r') as f:
                        # Move to end of file
                        f.seek(0, 2)

                        while not stop_event.is_set():
                            line = f.readline()
                            if line:
                                self._format_and_print_log(line)
                            else:
                                # No new data, wait a bit
                                time.sleep(0.1)
                except Exception as e:
                    if not stop_event.is_set():
                        print(f"\n{Colors.RED}Error reading log file: {str(e)}{Colors.END}")

            # Start tailing thread
            tail_thread = threading.Thread(target=tail_log_file, daemon=True)
            tail_thread.start()

            # Wait for Ctrl+C
            try:
                print(f"{Colors.BLUE}[Monitoring... Press Ctrl+C to return to menu]{Colors.END}\n")
                while True:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print(f"\n\n{Colors.GREEN}Stopping log monitoring...{Colors.END}")
                stop_event.set()
                tail_thread.join(timeout=1.0)

        except Exception as e:
            self.print_status(f"Error reading logs: {str(e)}", "error")
            self.wait_for_input("\nPress Enter to return to management console...")

    def _format_and_print_log(self, line: str):
        """
        Format and print a single log line with color coding based on event type

        Args:
            line: JSON log line to format and print
        """
        try:
            log_entry = json.loads(line.strip())
            timestamp = log_entry.get('timestamp', 'N/A')
            src_ip = log_entry.get('src_ip', 'N/A')
            message = log_entry.get('message', 'N/A')
            eventid = log_entry.get('eventid', '')

            # Extract additional relevant fields based on event type
            extra_info = ""

            # Color code based on event type
            if 'login' in eventid:
                username = log_entry.get('username', '')
                password = log_entry.get('password', '')

                if 'success' in eventid or 'login.success' in eventid:
                    # Successful login - RED (security concern)
                    color = Colors.RED
                    if username and password:
                        extra_info = f" [{username}:{password}]"
                    elif username:
                        extra_info = f" [{username}]"
                else:
                    # Failed login - YELLOW (attempted breach)
                    color = Colors.YELLOW
                    if username and password:
                        extra_info = f" [{username}:{password}]"
                    elif username:
                        extra_info = f" [{username}]"

            elif 'command' in eventid or 'input' in eventid:
                # Command execution - MAGENTA (interesting activity)
                color = Colors.MAGENTA
                command_input = log_entry.get('input', '')
                if command_input:
                    extra_info = f" CMD: {command_input}"

            elif 'session' in eventid:
                if 'connect' in eventid or 'session.connect' in eventid:
                    # New connection - GREEN (new activity)
                    color = Colors.GREEN
                elif 'closed' in eventid or 'session.closed' in eventid:
                    # Connection closed - BLUE (session end)
                    color = Colors.BLUE
                    duration = log_entry.get('duration', '')
                    if duration:
                        extra_info = f" (duration: {duration}s)"
                else:
                    color = Colors.CYAN

            elif 'download' in eventid or 'client.file' in eventid:
                # File download/upload - RED (potential malware)
                color = Colors.RED
                url = log_entry.get('url', '')
                outfile = log_entry.get('outfile', '')
                if url:
                    extra_info = f" URL: {url}"
                if outfile:
                    extra_info += f" File: {outfile}"

            else:
                # Default - CYAN
                color = Colors.CYAN

            # Format: [timestamp] [src_ip] message [extra_info]
            timestamp_short = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp
            print(f"{Colors.BOLD}{timestamp_short}{Colors.END} {color}{src_ip:15s}{Colors.END} {message}{extra_info}")

        except json.JSONDecodeError:
            # Not JSON, print as-is
            print(line.strip())
        except Exception as e:
            # Any other error, print line as-is
            print(line.strip())

    def restart_services_interactive(self, deployment_name: str = 'default'):
        """
        Restart services with user feedback

        Args:
            deployment_name: Name of deployment to restart
        """
        self.clear_screen()
        print(f"{Colors.BOLD}Restart Services{Colors.END}")
        print(f"Deployment: {deployment_name}\n")
        print("This will restart all HoneyMesh services. Any active connections will be dropped.")

        confirm = self.get_yes_no_input("Continue with restart", False)

        if confirm:
            if self.restart_services(deployment_name):
                self.print_status("All services restarted successfully", "success")
            else:
                self.print_status("Some services may have failed to restart", "warning")
        else:
            self.print_status("Restart cancelled", "info")

        self.wait_for_input()

    def change_configuration(self):
        """Change deployment configuration"""
        self.clear_screen()
        print(f"{Colors.BOLD}Change Configuration{Colors.END}\n")
        print("Configuration changes require service restart to take effect.")
        print("Current configuration:")

        if self.config:
            print(f"  SSH Port: {self.config.get('ssh_port', 'N/A')}")
            print(f"  Telnet Enabled: {self.config.get('telnet_enabled', 'N/A')}")
            if self.config.get('telnet_enabled'):
                print(f"  Telnet Port: {self.config.get('telnet_port', 'N/A')}")
            print(f"  Hostname: {self.config.get('hostname', 'N/A')}")
            print(f"  Kibana Port: {self.config.get('kibana_port', 'N/A')}")

        print(f"\n{Colors.YELLOW}Note: Advanced configuration editing will be available in future versions.{Colors.END}")
        print("For now, you can manually edit the docker-compose.yml file in the data directory.")

        self.wait_for_input()

    def backup_deployment(self):
        """Backup deployment data and configuration"""
        self.clear_screen()
        print(f"{Colors.BOLD}Backup Deployment{Colors.END}\n")

        try:
            backup_dir = Path(f"./honeymesh-backup-{int(time.time())}")
            backup_dir.mkdir(exist_ok=True)

            self.print_status("Creating backup...", "info")

            # Copy configuration files
            if self.config_file.exists():
                shutil.copy2(self.config_file, backup_dir / "config.json")

            if self.docker_compose_file.exists():
                shutil.copy2(self.docker_compose_file, backup_dir / "docker-compose.yml")

            # Copy logs directory
            logs_dir = self.data_dir / "logs"
            if logs_dir.exists():
                shutil.copytree(logs_dir, backup_dir / "logs")

            # Copy configs directory
            configs_dir = self.data_dir / "configs"
            if configs_dir.exists():
                shutil.copytree(configs_dir, backup_dir / "configs")

            self.print_status(f"Backup created successfully at {backup_dir}", "success")

        except Exception as e:
            self.print_status(f"Backup failed: {str(e)}", "error")

        self.wait_for_input()

    def stop_and_remove_deployment(self, deployment_name: str = 'default') -> bool:
        """
        Stop and remove the deployment

        Args:
            deployment_name: Name of deployment to remove

        Returns:
            True if successful, False otherwise
        """
        self.clear_screen()
        print(f"{Colors.RED}{Colors.BOLD}Stop & Remove Deployment{Colors.END}")
        print(f"Deployment: {deployment_name}\n")
        print("This will stop all honeypot services and remove containers.")
        print(f"{Colors.YELLOW}WARNING: Containers will be removed but log data will be preserved.{Colors.END}")

        confirm = self.get_yes_no_input("Are you sure you want to continue", False)

        if confirm:
            if self.remove_deployment(deployment_name):
                self.print_status("Deployment stopped and removed successfully", "success")
                self.wait_for_input("Press Enter to return to main menu...")
                self.show_main_menu()
                return True
            else:
                self.print_status("Failed to completely remove deployment", "error")
                self.wait_for_input()

        return False

    def create_new_deployment(self):
        """Create a new deployment (when existing one is detected)"""
        self.deploy_default_environment()

    def remove_existing_deployment(self):
        """Remove existing deployment and start fresh"""
        if self.stop_and_remove_deployment():
            self.deploy_default_environment()

    def quit_application(self):
        """Exit the application"""
        print(f"\n{Colors.CYAN}Thank you for using HoneyMesh!{Colors.END}")
        sys.exit(0)

    def run(self):
        """Main application entry point"""
        try:
            # Check if running as root/sudo - this should NOT be the case
#            if os.geteuid() == 0:
#                self.clear_screen()
#                print(f"{Colors.RED}{Colors.BOLD}WARNING: Running as root/sudo detected!{Colors.END}\n")
#                print(f"{Colors.YELLOW}HoneyMesh should NOT be run as root for security reasons:{Colors.END}")
#                print("• Docker containers will run with elevated privileges")
#                print("• Log files will be owned by root")
#                print("• Security risks if honeypot is compromised")
#                print("• Docker group membership allows non-root Docker access")

#                print(f"\n{Colors.GREEN}Recommended approach:{Colors.END}")
#                print("1. Exit this script (Ctrl+C)")
#                print("2. Add your user to docker group: sudo usermod -aG docker $USER")
#                print("3. Logout and login again")
#                print("4. Run script as normal user: python3 honeymesh.py")

#                choice = input(f"\n{Colors.RED}Continue running as root anyway? [y/N]: {Colors.END}").strip().lower()
#                if choice not in ['y', 'yes']:
#                    print(f"{Colors.CYAN}Exiting for security. Please run as normal user.{Colors.END}")
#                    sys.exit(1)
#                else:
#                    print(f"{Colors.YELLOW}Continuing as root (not recommended)...{Colors.END}")
#                    time.sleep(2)

            # Run dependency check
            print(f"{Colors.BOLD}HoneyMesh - Checking Dependencies{Colors.END}\n")

            checker = DependencyChecker()
            if not checker.check_critical_dependencies():
                print(f"{Colors.RED}Critical dependencies missing!{Colors.END}")
                print("Errors found:")
                for error in checker.errors:
                    print(f"  {Colors.RED}[x]{Colors.END} {error}")

                checker.print_quick_fix()

                choice = input(f"\n{Colors.YELLOW}Continue anyway? [y/N]: {Colors.END}").strip().lower()
                if choice not in ['y', 'yes']:
                    print(f"{Colors.CYAN}Please install dependencies and try again.{Colors.END}")
                    sys.exit(1)
            else:
                print(f"{Colors.GREEN}All critical dependencies satisfied!{Colors.END}")
                time.sleep(1)

            # Proceed to main menu
            self.show_main_menu()

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.END}")
            self.quit_application()
        except Exception as e:
            print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}")
            sys.exit(1)

def main():
    """Application entry point"""
    app = HoneyMeshApp()
    app.run()

if __name__ == "__main__":
    main()
