#!/usr/bin/env python3
"""
HoneyMesh - Medium Interaction Honeypot Deployment
Handles custom Cowrie honeypot deployments with industry templates
"""

import os
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for importing Colors from main app
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from honeymesh import Colors
    from generatePickle import generate_pickle
    from template_loader import (
        TemplateLibrary,
        YAMLTemplate,
        create_filesystem_from_template,
        write_files_from_template,
        create_custom_commands_from_template
    )
    from medium.templateBuilder import TemplateBuilder
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are in the medium/ directory")
    sys.exit(1)


class MediumDeploymentManager:
    """Manages medium interaction honeypot deployments"""

    def __init__(self, parent_app):
        """
        Initialize medium deployment manager

        Args:
            parent_app: Reference to main HoneyMeshApp instance
        """
        self.app = parent_app
        self.templates_dir = Path("./medium/templates")
        self.medium_data_dir = Path("./honeypot-data/medium")

        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.medium_data_dir.mkdir(parents=True, exist_ok=True)

        # Template definitions
        self.industry_presets = {
            '1': {
                'name': 'Epic Healthcare System',
                'key': 'epic-healthcare',
                'description': 'Hospital Epic EMR production server',
                'default_port': 2224
            },
            '2': {
                'name': 'Corporate IT Infrastructure',
                'key': 'corporate-it',
                'description': 'Standard corporate Linux server',
                'default_port': 2226
            },
            '3': {
                'name': 'Financial Services',
                'key': 'financial-services',
                'description': 'Banking/financial institution server',
                'default_port': 2228
            }
        }

    def show_medium_deployment_menu(self):
        """Main entry point for medium interaction deployment"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Medium Interaction Honeypot Deployment{Colors.END}\n")

        # Check for existing templates
        existing_templates = self.get_existing_templates()

        print("Select template source:\n")

        if existing_templates:
            print(f"{Colors.GREEN}[1]{Colors.END} Use existing template")
        print(f"{Colors.CYAN}[2]{Colors.END} Build custom template wizard")
        print(f"{Colors.WHITE}[Q]{Colors.END} Return to main menu")

        valid_choices = ['2', '3', 'Q']
        if existing_templates:
            valid_choices.insert(0, '1')

        choice = self.app.get_user_choice("\nEnter your choice: ", valid_choices)

        if choice == '1' and existing_templates:
            self.use_existing_template()
        elif choice == '3':
            self.build_custom_template()
        elif choice == 'q':
            return

    def get_existing_templates(self) -> List[Dict]:
        """
        Scan templates directory for existing templates

        Returns:
            List of template metadata dictionaries
        """
        templates = []

        if not self.templates_dir.exists():
            return templates

        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                templates.append({
                    'file': template_file,
                    'name': template_file.stem,
                    'created': template_file.stat().st_ctime,
                    'modified': template_file.stat().st_mtime
                })
            except Exception as e:
                self.app.logger.warning(f"Could not load template {template_file}: {e}")

        return sorted(templates, key=lambda x: x['modified'], reverse=True)

    def use_existing_template(self):
        """Display and select from existing templates"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Available Templates{Colors.END}\n")

        templates = self.get_existing_templates()

        if not templates:
            self.app.print_status("No templates found", "warning")
            self.app.wait_for_input()
            self.show_medium_deployment_menu()
            return

        print("─" * 60)
        print(f"{'#':<4} {'Name':<40} {'Modified':<15}")
        print("─" * 60)

        for idx, template in enumerate(templates, 1):
            mod_time = time.strftime("%Y-%m-%d", time.localtime(template['modified']))
            print(f"{idx:<4} {template['name']:<40} {mod_time:<15}")

        print("─" * 60)
        print(f"\n{Colors.WHITE}[B]{Colors.END} Back to template selection")

        valid_choices = [str(i) for i in range(1, len(templates) + 1)] + ['B']
        choice = self.app.get_user_choice("\nSelect template number: ", valid_choices)

        if choice == 'b':
            self.show_medium_deployment_menu()
            return

        selected_template = templates[int(choice) - 1]
        self.load_and_configure(selected_template['file'])

    def create_from_preset(self):
        """Create new template from industry preset"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Industry Preset Selection{Colors.END}\n")

        for key, preset in self.industry_presets.items():
            print(f"{Colors.GREEN}[{key}]{Colors.END} {preset['name']}")
            print(f"    {Colors.WHITE}{preset['description']}{Colors.END}")
            print()

        print(f"{Colors.WHITE}[B]{Colors.END} Back to template selection")

        valid_choices = list(self.industry_presets.keys()) + ['B']
        choice = self.app.get_user_choice("\nSelect industry preset: ", valid_choices)

        if choice == 'b':
            self.show_medium_deployment_menu()
            return

        preset = self.industry_presets[choice]

        # Check if template file exists
        template_file = self.templates_dir / f"{preset['key']}.yaml"
        if template_file.exists():
            self.load_and_configure(template_file)
        else:
            self.app.print_status(f"Template file not found: {template_file}", "error")
            self.app.print_status("Please ensure template YAML files are in medium/templates/", "info")
            self.app.wait_for_input()
            self.show_medium_deployment_menu()

    def build_custom_template(self):
        """Build custom template from scratch (wizard)"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Custom Template Builder{Colors.END}\n")
    
        try:
            # Initialize template builder
            builder = TemplateBuilder()
        
            # Run the interactive builder
            builder.run()
        
            # After builder finishes, show the template selection menu again
            self.app.wait_for_input("\nPress Enter to return to template selection...")
            self.show_medium_deployment_menu()
        
        except KeyboardInterrupt:
            self.app.print_status("Template building cancelled", "warning")
            self.app.wait_for_input()
            self.show_medium_deployment_menu()
        except Exception as e:
            self.app.print_status(f"Template builder error: {str(e)}", "error")
            self.app.log_exception("build_custom_template", e)
            self.app.wait_for_input()
            self.show_medium_deployment_menu()

    def load_and_configure(self, template_file: Path):
        """
        Load template and configure deployment

        Args:
            template_file: Path to template YAML file
        """
        try:
            # Initialize template library and load template
            template_library = TemplateLibrary(self.templates_dir)
            template = template_library.get_template(template_file.stem)

            if not template:
                raise Exception(f"Could not load template from {template_file}")

            # Initialize configuration with template defaults
            config = {
                'template_name': template.name,
                'template_file': template_file,
                'template_id': template_file.stem,
                'deployment_name': '',
                'hostname': template.hostname,
                'ssh_port': self.industry_presets.get('1', {}).get('default_port', 2224),
                'telnet_enabled': False,
                'telnet_port': None,
                'users': [{'username': u, 'password': p} for u, p in template.get_users().items()],
                'external_access': False
            }

            # Start configuration wizard
            self.configure_and_deploy(config, template)

        except Exception as e:
            self.app.print_status(f"Error loading template: {str(e)}", "error")
            self.app.log_exception("load_and_configure", e)
            self.app.wait_for_input()
            self.show_medium_deployment_menu()

    def configure_and_deploy(self, config: Dict, template):
        """
        Configure and deploy honeypot from template

        Args:
            config: Configuration dictionary
            template: YAMLTemplate object
        """
        # Configuration menu loop
        while True:
            choice = self.show_customization_menu(config)

            if choice == '1':
                self.configure_hostname(config)
            elif choice == '2':
                self.configure_users(config)
            elif choice == '3':
                self.configure_ports(config)
            elif choice == '4':
                self.configure_deployment_name(config)
            elif choice == 'p':
                self.preview_configuration(config)
            elif choice == 'd':
                if not config.get('deployment_name'):
                    self.app.print_status("Please set a deployment name first", "warning")
                    time.sleep(2)
                    continue
                if self.show_deployment_summary(config):
                    self.perform_medium_deployment(config, template)
                    return
            elif choice == 'b':
                self.show_medium_deployment_menu()
                return

    def show_customization_menu(self, config: Dict) -> str:
        """Display customization menu and get choice"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Configure Deployment: {config['template_name']}{Colors.END}\n")

        if config.get('deployment_name'):
            print(f"Deployment Name: {Colors.CYAN}{config['deployment_name']}{Colors.END}")
        else:
            print(f"Deployment Name: {Colors.YELLOW}Not set (required){Colors.END}")

        print(f"Hostname: {config['hostname']}")
        print(f"SSH Port: {config['ssh_port']}")
        print(f"Users: {len(config['users'])} configured")
        print()

        print("Customize deployment:\n")
        print(f"{Colors.GREEN}[1]{Colors.END} Modify hostname/FQDN")
        print(f"{Colors.GREEN}[2]{Colors.END} Configure user accounts")
        print(f"{Colors.GREEN}[3]{Colors.END} Configure SSH/Telnet ports")
        print(f"{Colors.GREEN}[4]{Colors.END} Set deployment name")
        print()
        print(f"{Colors.CYAN}[P]{Colors.END} Preview final configuration")
        print(f"{Colors.BLUE}[D]{Colors.END} Deploy with current settings")
        print(f"{Colors.WHITE}[B]{Colors.END} Back to template selection")

        valid_choices = ['1', '2', '3', '4', 'P', 'D', 'B']
        return self.app.get_user_choice("\nEnter your choice: ", valid_choices)

    def configure_deployment_name(self, config: Dict):
        """Set deployment name"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Set Deployment Name{Colors.END}\n")
        print("Choose a unique name for this honeypot deployment.")
        print("Examples: epic-prod-01, corp-server-02, finance-web-01")
        print()

        while True:
            name = input("Deployment name: ").strip()

            if not name:
                print(f"{Colors.RED}Name cannot be empty{Colors.END}")
                continue

            # Check if deployment already exists
            deployment_dir = self.medium_data_dir / name
            if deployment_dir.exists():
                print(f"{Colors.RED}Deployment '{name}' already exists{Colors.END}")
                continue

            # Validate name format
            if not all(c.isalnum() or c in '-_' for c in name):
                print(f"{Colors.RED}Name can only contain letters, numbers, hyphens, and underscores{Colors.END}")
                continue

            config['deployment_name'] = name
            self.app.print_status(f"Deployment name set to: {name}", "success")
            time.sleep(1)
            break

    def configure_hostname(self, config: Dict):
        """Configure hostname/FQDN"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Configure Hostname{Colors.END}\n")
        print(f"Current: {config['hostname']}")
        print()

        hostname = input(f"New hostname [{config['hostname']}]: ").strip()
        if hostname:
            config['hostname'] = hostname
            self.app.print_status("Hostname updated", "success")
        else:
            self.app.print_status("Hostname unchanged", "info")
        time.sleep(1)

    def configure_users(self, config: Dict):
        """Configure user accounts"""
        while True:
            self.app.clear_screen()
            print(f"{Colors.BOLD}User Account Configuration{Colors.END}\n")

            print("Current users:")
            print("─" * 60)
            print(f"{'#':<4} {'Username':<20} {'Password':<20}")
            print("─" * 60)

            for idx, user in enumerate(config['users'], 1):
                print(f"{idx:<4} {user['username']:<20} {user['password']:<20}")

            print("─" * 60)
            print()

            print(f"{Colors.GREEN}[A]{Colors.END} Add new user")
            print(f"{Colors.YELLOW}[E]{Colors.END} Edit existing user")
            print(f"{Colors.RED}[D]{Colors.END} Delete user")
            print(f"{Colors.WHITE}[C]{Colors.END} Continue")

            choice = self.app.get_user_choice("\nEnter your choice: ", ['A', 'E', 'D', 'C'])

            if choice == 'a':
                self.add_user(config)
            elif choice == 'e':
                self.edit_user(config)
            elif choice == 'd':
                self.delete_user(config)
            elif choice == 'c':
                break

    def add_user(self, config: Dict):
        """Add new user account"""
        print(f"\n{Colors.BOLD}Add New User{Colors.END}\n")

        username = input("Username: ").strip()
        if not username:
            return

        password = input("Password: ").strip()
        if not password:
            return

        config['users'].append({
            'username': username,
            'password': password
        })

        self.app.print_status(f"User '{username}' added", "success")
        time.sleep(1)

    def edit_user(self, config: Dict):
        """Edit existing user"""
        if not config['users']:
            self.app.print_status("No users to edit", "warning")
            time.sleep(1)
            return

        print(f"\n{Colors.BOLD}Edit User{Colors.END}\n")
        user_num = input("Enter user number to edit: ").strip()

        try:
            idx = int(user_num) - 1
            if 0 <= idx < len(config['users']):
                user = config['users'][idx]

                new_password = input(f"New password for '{user['username']}' [keep current]: ").strip()
                if new_password:
                    user['password'] = new_password
                    self.app.print_status("Password updated", "success")

                time.sleep(1)
            else:
                self.app.print_status("Invalid user number", "error")
                time.sleep(1)
        except ValueError:
            self.app.print_status("Invalid input", "error")
            time.sleep(1)

    def delete_user(self, config: Dict):
        """Delete user account"""
        if not config['users']:
            self.app.print_status("No users to delete", "warning")
            time.sleep(1)
            return

        print(f"\n{Colors.BOLD}Delete User{Colors.END}\n")
        user_num = input("Enter user number to delete: ").strip()

        try:
            idx = int(user_num) - 1
            if 0 <= idx < len(config['users']):
                deleted_user = config['users'].pop(idx)
                self.app.print_status(f"User '{deleted_user['username']}' deleted", "success")
                time.sleep(1)
            else:
                self.app.print_status("Invalid user number", "error")
                time.sleep(1)
        except ValueError:
            self.app.print_status("Invalid input", "error")
            time.sleep(1)

    def configure_ports(self, config: Dict):
        """Configure SSH/Telnet ports"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Configure Ports{Colors.END}\n")

        # SSH Port
        ssh_port = self.app.get_port_input("SSH port", config['ssh_port'])
        config['ssh_port'] = ssh_port

        # Telnet
        telnet_enabled = self.app.get_yes_no_input("Enable Telnet", config['telnet_enabled'])
        config['telnet_enabled'] = telnet_enabled

        if telnet_enabled:
            default_telnet = config.get('telnet_port', config['ssh_port'] + 1)
            config['telnet_port'] = self.app.get_port_input("Telnet port", default_telnet)
        else:
            config['telnet_port'] = None

    def preview_configuration(self, config: Dict):
        """Display configuration preview"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Configuration Preview{Colors.END}\n")
        print("─" * 60)
        print(f"Template: {config['template_name']}")
        print(f"Deployment Name: {config.get('deployment_name', 'NOT SET')}")
        print(f"Hostname: {config['hostname']}")
        print(f"SSH Port: {config['ssh_port']}")
        if config['telnet_enabled']:
            print(f"Telnet Port: {config['telnet_port']}")
        else:
            print(f"Telnet: Disabled")
        print()
        print(f"User Accounts ({len(config['users'])}):")
        for user in config['users']:
            print(f"  • {user['username']} / {user['password']}")
        print("─" * 60)

        self.app.wait_for_input()

    def show_deployment_summary(self, config: Dict) -> bool:
        """Show deployment summary and get confirmation"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Deployment Summary{Colors.END}\n")
        print("─" * 60)
        print(f"Template:         {config['template_name']}")
        print(f"Deployment Name:  {config['deployment_name']}")
        print(f"Hostname:         {config['hostname']}")
        print(f"SSH Port:         {config['ssh_port']}")
        if config['telnet_enabled']:
            print(f"Telnet Port:      {config['telnet_port']}")
        print(f"User Accounts:    {len(config['users'])}")
        print(f"Estimated Disk:   ~50MB")
        print(f"Setup Time:       3-5 minutes")
        print("─" * 60)

        print(f"\n{Colors.GREEN}[D]{Colors.END} Deploy now")
        print(f"{Colors.YELLOW}[M]{Colors.END} Modify settings")
        print(f"{Colors.WHITE}[Q]{Colors.END} Cancel and return")

        choice = self.app.get_user_choice("\nEnter your choice: ", ['D', 'M', 'Q'])

        if choice == 'd':
            return True
        elif choice == 'm':
            return False
        elif choice == 'q':
            self.show_medium_deployment_menu()
            return False

    def perform_medium_deployment(self, config: Dict, template):
        """Execute the actual deployment using your existing build system"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Deploying Medium Interaction Honeypot{Colors.END}\n")

        deployment_dir = self.medium_data_dir / config['deployment_name']

        try:
            # Initialize template library
            self.app.print_status("Loading template library...", "info")
            template_library = TemplateLibrary(self.templates_dir)

            # Get the template
            template_id = config.get('template_id', config['template_file'].stem)
            loaded_template = template_library.get_template(template_id)

            if not loaded_template:
                raise Exception(f"Template '{template_id}' not found in library")

            # Build honeypot using your existing MediumInteractionHoneypot logic
            self.app.print_status("Creating honeypot structure...", "info")

            # Create base directories
            deployment_dir.mkdir(parents=True, exist_ok=True)

            config_dir = deployment_dir / 'config'
            share_dir = deployment_dir / 'share' / 'cowrie'
            temp_dir = share_dir / 'temp' / 'tmp'
            honeyfs_dir = deployment_dir / 'honeyfs' / 'tmp'
            txtcmds_dir = deployment_dir / 'txtcmds'
            log_dir = deployment_dir / 'log'
            keys_dir = deployment_dir / 'keys'
            downloads_dir = deployment_dir / 'downloads'
            elk_config_dir = deployment_dir / 'elk-config'

            # Create all directories
            for directory in [config_dir, share_dir, temp_dir, honeyfs_dir,
                             txtcmds_dir, log_dir, keys_dir, downloads_dir]:
                directory.mkdir(parents=True, exist_ok=True)

            # Create log subdirectories
            (log_dir / 'tty').mkdir(parents=True, exist_ok=True)
            (log_dir / '.gitkeep').touch()
            (log_dir / 'tty' / '.gitkeep').touch()

            # Build filesystem structure from template
            self.app.print_status("Building filesystem structure...", "info")
            create_filesystem_from_template(loaded_template, temp_dir)
            write_files_from_template(loaded_template, temp_dir)

            # Copy to honeyfs
            self.app.print_status("Creating honeyfs contents...", "info")
            if honeyfs_dir.exists():
                shutil.rmtree(honeyfs_dir)
            shutil.copytree(temp_dir, honeyfs_dir)

            # Generate pickle file
            self.app.print_status("Generating Cowrie filesystem pickle...", "info")
            pickle_path = share_dir / 'fs.pickle'
            success = generate_pickle(str(temp_dir), str(pickle_path), maxdepth=15, verbose=False)

            if not success:
                raise Exception("Failed to generate pickle filesystem")

            # Create cmdoutput.json
            self.app.print_status("Creating command output simulation...", "info")
            self.create_cmdoutput_json(share_dir, loaded_template)

            # Create configuration files
            self.app.print_status("Generating configuration files...", "info")
            self.create_userdb(config, config_dir / 'userdb.txt')
            self.create_cowrie_config(config, loaded_template, config_dir / 'cowrie.cfg')

            # Create custom commands if template has them
            if loaded_template.get_config().get('custom_commands'):
                self.app.print_status("Creating custom commands...", "info")
                create_custom_commands_from_template(loaded_template, txtcmds_dir)

            # Generate SSH keys
            self.app.print_status("Generating SSH host keys...", "info")
            self.generate_ssh_keys(keys_dir)

            # Create ELK configuration
            self.app.print_status("Creating ELK stack configuration...", "info")
            self.create_elk_configs(deployment_dir, config['deployment_name'])

            # Generate docker-compose.yml
            self.app.print_status("Creating Docker Compose configuration...", "info")
            self.generate_docker_compose_file(deployment_dir, config)

            # Fix permissions for Cowrie
            self.app.print_status("Setting file permissions...", "info")
            self.fix_permissions(deployment_dir)

            # Save metadata
            metadata = {
                'name': config['deployment_name'],
                'template': config['template_name'],
                'template_id': template_id,
                'hostname': config['hostname'],
                'ssh_port': config['ssh_port'],
                'telnet_port': config.get('telnet_port'),
                'users': {u['username']: u['password'] for u in config['users']},
                'category': loaded_template.category if hasattr(loaded_template, 'category') else 'custom',
                'version': loaded_template.version if hasattr(loaded_template, 'version') else '1.0',
                'created': time.time()
            }

            metadata_file = deployment_dir / 'metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Pull Docker images
            self.app.print_status("Pulling Docker images...", "info")
            self.pull_docker_images()

            # Create Docker network if needed
            self.ensure_docker_network()

            # Deploy containers
            self.app.print_status("Starting containers...", "info")
            self.deploy_containers(deployment_dir)

            # Wait for services
            self.app.print_status("Waiting for services to be healthy...", "info")
            time.sleep(10)

            self.app.print_status("Deployment completed successfully!", "success")
            time.sleep(2)

            # Show success screen
            self.show_medium_deployment_success(config)

        except Exception as e:
            self.app.log_exception("perform_medium_deployment", e)
            self.app.print_status(f"Deployment failed: {str(e)}", "error")
            self.app.wait_for_input()
            self.show_medium_deployment_menu()

    def create_userdb(self, config: Dict, output_path: Path):
        """Create Cowrie userdb.txt file"""
        users = config.get('users', [])

        with open(output_path, 'w') as f:
            for user in users:
                username = user.get('username')
                password = user.get('password')
                f.write(f"{username}:x:{password}\n")

    def create_cmdoutput_json(self, share_dir: Path, template: YAMLTemplate):
        """Create cmdoutput.json with simulated command outputs in Cowrie's exact format"""
        config = template.get_config()
        hostname = config.get('hostname', 'server')

        cmdoutput = {
            "command": {
                "ps": {
                    "": "  PID TTY          TIME CMD\n    1 ?        00:00:01 systemd\n  523 ?        00:00:00 sshd\n 1337 pts/0    00:00:00 bash\n 1429 pts/0    00:00:00 ps"
                },
                "uname": {
                    "-a": f"Linux {hostname} 5.4.0-74-generic #83-Ubuntu SMP Sat May 8 02:35:39 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux",
                    "-r": "5.4.0-74-generic"
                },
                "uptime": {
                    "": " 18:46:53 up 42 days,  3:27,  1 user,  load average: 0.34, 0.52, 0.48"
                },
                "whoami": {
                    "": "admin"
                },
                "hostname": {
                    "": hostname
                },
                "df": {
                    "-h": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       450G  356G   71G  84% /\ntmpfs            32G     0   32G   0% /dev/shm"
                }
            }
        }

        cmdoutput_file = share_dir / 'cmdoutput.json'
        with open(cmdoutput_file, 'w') as f:
            json.dump(cmdoutput, f, indent=2)

    def create_cowrie_config(self, config: Dict, template: YAMLTemplate, output_path: Path):
        """Create Cowrie configuration file"""
        template_config = template.get_config()

        cowrie_cfg = f"""[honeypot]
hostname = {config['hostname']}
log_path = var/log/cowrie
download_path = var/lib/cowrie/downloads
share_path = share/cowrie
state_path = var/lib/cowrie
etc_path = etc
contents_path = honeyfs/tmp
txtcmds_path = txtcmds
ttylog = true
ttylog_path = var/log/cowrie/tty/
interactive_timeout = 180
authentication_timeout = 120
backend = shell
timezone = {template_config.get('timezone', 'US/Eastern')}
auth_class = UserDB
auth_class_parameters = userdb.txt

[shell]
filesystem = share/cowrie/fs.pickle
processes = share/cowrie/cmdoutput.json
arch = linux-x64-lsb
kernel_version = 5.4.0-74-generic #83-Ubuntu
kernel_build_string = #83-Ubuntu SMP Sat May 8 02:35:39 UTC 2021
hardware_platform = x86_64
operating_system = GNU/Linux
ssh_version = {template_config.get('ssh_banner', 'SSH-2.0-OpenSSH_8.4p1')}

[ssh]
enabled = true
rsa_public_key = etc/ssh_host_rsa_key.pub
rsa_private_key = etc/ssh_host_rsa_key
dsa_public_key = etc/ssh_host_dsa_key.pub
dsa_private_key = etc/ssh_host_dsa_key
ecdsa_public_key = etc/ssh_host_ecdsa_key.pub
ecdsa_private_key = etc/ssh_host_ecdsa_key
ed25519_public_key = etc/ssh_host_ed25519_key.pub
ed25519_private_key = etc/ssh_host_ed25519_key
version = {template_config.get('ssh_banner', 'SSH-2.0-OpenSSH_8.4p1')}
listen_endpoints = tcp:2222:interface=0.0.0.0

[telnet]
enabled = {"true" if config.get('telnet_enabled') else "false"}
{"listen_endpoints = tcp:2223:interface=0.0.0.0" if config.get('telnet_enabled') else ""}

[output_jsonlog]
enabled = true
logfile = var/log/cowrie/cowrie.json
epoch_timestamp = false
"""

        with open(output_path, 'w') as f:
            f.write(cowrie_cfg)

    def generate_ssh_keys(self, keys_dir: Path):
        """Generate SSH host keys"""
        key_types = ['rsa', 'dsa', 'ecdsa', 'ed25519']

        for key_type in key_types:
            key_file = keys_dir / f'ssh_host_{key_type}_key'
            if not key_file.exists():
                try:
                    subprocess.run([
                        'ssh-keygen', '-t', key_type,
                        '-f', str(key_file),
                        '-N', '',
                        '-q'
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    pass

    def create_elk_configs(self, deployment_dir: Path, name: str):
        """Create ELK stack configuration files"""
        elk_config_dir = deployment_dir / 'elk-config'
        logstash_dir = elk_config_dir / 'logstash'
        filebeat_dir = elk_config_dir / 'filebeat'

        logstash_dir.mkdir(parents=True, exist_ok=True)
        filebeat_dir.mkdir(parents=True, exist_ok=True)

        # Logstash configuration
        logstash_conf = """input {
  beats {
    port => 5044
  }
}

filter {
  if [honeypot] {
    if [timestamp] {
      date {
        match => [ "timestamp", "ISO8601" ]
      }
    }

    if [src_ip] {
      geoip {
        source => "src_ip"
        target => "geoip"
      }
    }

    mutate {
      remove_field => [ "@version", "host", "agent", "ecs", "log", "input" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "honeymesh-%{[honeypot]}-%{+YYYY.MM.dd}"
  }

  stdout {
    codec => rubydebug
  }
}
"""

        with open(logstash_dir / 'logstash.conf', 'w') as f:
            f.write(logstash_conf)

        # Filebeat configuration
        filebeat_conf = f"""filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/{name}/cowrie.json*
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    honeypot: {name}
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

        with open(filebeat_dir / 'filebeat.yml', 'w') as f:
            f.write(filebeat_conf)

    def generate_docker_compose_file(self, deployment_dir: Path, config: Dict):
        """Generate complete docker-compose.yml with ELK stack"""
        name = config['deployment_name']
        ssh_port = config['ssh_port']
        telnet_port = config.get('telnet_port')
        hostname = config['hostname']

        # Build port mappings
        ports = [f'      - "{ssh_port}:2222"']
        if telnet_port:
            ports.append(f'      - "{telnet_port}:2223"')
        ports_str = '\n'.join(ports)

        compose_content = f"""version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: honeymesh-elasticsearch-{name}
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
      - xpack.security.enrollment.enabled=false
      - cluster.name=honeymesh-cluster
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - honeymesh
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: honeymesh-kibana-{name}
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - SERVER_NAME=honeymesh-kibana
      - SERVER_HOST=0.0.0.0
    volumes:
      - kibana-data:/usr/share/kibana/data
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - honeymesh
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: honeymesh-logstash-{name}
    environment:
      - "LS_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - logstash-data:/usr/share/logstash/data
      - ./elk-config/logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
      - "9600:9600"
    depends_on:
      - elasticsearch
    networks:
      - honeymesh
    restart: unless-stopped

  {name}:
    image: cowrie/cowrie:latest
    container_name: honeymesh-{name}
    hostname: {hostname}
    restart: unless-stopped
    user: "2000:2000"

    tmpfs:
      - /tmp/cowrie:uid=2000,gid=2000
      - /tmp/cowrie/data:uid=2000,gid=2000

    ports:
{ports_str}

    volumes:
      - ./config/cowrie.cfg:/cowrie/cowrie-git/etc/cowrie.cfg:ro
      - ./config/userdb.txt:/cowrie/cowrie-git/etc/userdb.txt:ro
      - ./keys:/cowrie/cowrie-git/etc
      - ./log:/cowrie/cowrie-git/var/log/cowrie
      - ./log/tty:/cowrie/cowrie-git/var/log/cowrie/tty
      - ./downloads:/cowrie/cowrie-git/var/lib/cowrie/downloads
      - ./share/cowrie:/cowrie/cowrie-git/share/cowrie
      - ./honeyfs:/cowrie/cowrie-git/honeyfs:ro
      - ./txtcmds:/cowrie/cowrie-git/txtcmds:ro

    networks:
      - honeymesh

    environment:
      - COWRIE_HOSTNAME={hostname}

    depends_on:
      - logstash

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: honeymesh-filebeat-{name}
    user: root
    command: filebeat -e --strict.perms=false
    volumes:
      - ./elk-config/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./log:/var/log/{name}:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - logstash
      - {name}
    networks:
      - honeymesh
    restart: unless-stopped

networks:
  honeymesh:
    driver: bridge

volumes:
  elasticsearch-data:
  kibana-data:
  logstash-data:
"""

        compose_file = deployment_dir / 'docker-compose.yml'
        with open(compose_file, 'w') as f:
            f.write(compose_content)

    def fix_permissions(self, deployment_dir: Path):
        """Fix permissions for Cowrie (UID 2000, GID 2000)"""
        cowrie_uid = 2000
        cowrie_gid = 2000

        dirs_to_chown = [
            deployment_dir / 'keys',
            deployment_dir / 'log',
            deployment_dir / 'downloads',
            deployment_dir / 'share' / 'cowrie',
        ]

        for directory in dirs_to_chown:
            if directory.exists():
                try:
                    for root, dirs, files in os.walk(directory):
                        os.chown(root, cowrie_uid, cowrie_gid)
                        for d in dirs:
                            os.chown(os.path.join(root, d), cowrie_uid, cowrie_gid)
                        for f in files:
                            os.chown(os.path.join(root, f), cowrie_uid, cowrie_gid)
                except Exception:
                    pass

        # Fix SSH key permissions
        keys_dir = deployment_dir / 'keys'
        if keys_dir.exists():
            try:
                for key_file in keys_dir.glob('ssh_host_*_key'):
                    if not key_file.name.endswith('.pub'):
                        os.chmod(key_file, 0o600)
                        os.chown(key_file, cowrie_uid, cowrie_gid)
                    else:
                        os.chmod(key_file, 0o644)
                        os.chown(key_file, cowrie_uid, cowrie_gid)
            except Exception:
                pass

    def pull_docker_images(self):
        """Pull required Docker images"""
        images = [
            "docker.elastic.co/elasticsearch/elasticsearch:8.11.0",
            "docker.elastic.co/logstash/logstash:8.11.0",
            "docker.elastic.co/kibana/kibana:8.11.0",
            "docker.elastic.co/beats/filebeat:8.11.0",
            "cowrie/cowrie:latest"
        ]

        try:
            if not self.app.docker_client:
                import docker
                self.app.docker_client = docker.from_env()

            for image in images:
                try:
                    self.app.docker_client.images.pull(image)
                except:
                    pass
        except:
            pass

    def ensure_docker_network(self):
        """Create honeymesh Docker network if it doesn't exist"""
        try:
            result = subprocess.run(
                ['docker', 'network', 'inspect', 'honeymesh'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                subprocess.run(
                    ['docker', 'network', 'create', 'honeymesh'],
                    check=True,
                    capture_output=True
                )
        except Exception:
            pass

    def deploy_containers(self, deployment_dir: Path):
        """Deploy containers using docker-compose"""
        original_dir = os.getcwd()

        try:
            os.chdir(deployment_dir)

            # Stop any existing containers
            subprocess.run(
                ['docker-compose', 'down'],
                capture_output=True,
                timeout=30
            )

            # Start containers
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise Exception(f"docker-compose failed: {result.stderr}")

        finally:
            os.chdir(original_dir)

    def show_medium_deployment_success(self, config: Dict):
        """Display successful medium deployment information"""
        self.app.clear_screen()
        print(f"{Colors.GREEN}{Colors.BOLD}Medium Interaction Honeypot Deployed Successfully!{Colors.END}\n")

        print(f"{Colors.BOLD}Deployment Information:{Colors.END}")
        print("─" * 70)
        print(f"Name:             {config['deployment_name']}")
        print(f"Template:         {config['template_name']}")
        print(f"Hostname:         {config['hostname']}")
        print(f"Container:        honeymesh-{config['deployment_name']}")
        print("─" * 70)

        print(f"\n{Colors.BOLD}Access Your Honeypot:{Colors.END}")
        print(f"• SSH:    ssh {config['users'][0]['username']}@localhost -p {config['ssh_port']}")
        if config.get('telnet_enabled'):
            print(f"• Telnet: telnet localhost {config['telnet_port']}")

        print(f"\n{Colors.BOLD}Test Credentials:{Colors.END}")
        for user in config['users'][:3]:
            print(f"  {user['username']} / {user['password']}")
        if len(config['users']) > 3:
            print(f"  ... and {len(config['users']) - 3} more")

        print(f"\n{Colors.BOLD}Monitor Activity:{Colors.END}")
        deployment_dir = self.medium_data_dir / config['deployment_name']
        print(f"• Logs: tail -f {deployment_dir}/log/cowrie.json")
        print(f"• Dashboard: http://localhost:5601")

        print(f"\n{Colors.GREEN}[T]{Colors.END} Show test connection command")
        print(f"{Colors.BLUE}[M]{Colors.END} Management menu")
        print(f"{Colors.WHITE}[E]{Colors.END} Exit to main menu")

        choice = self.app.get_user_choice("\nEnter your choice: ", ['T', 'M', 'E'])

        if choice == 't':
            self.show_test_connection(config)
        elif choice == 'm':
            self.app.management_console()
        else:
            self.app.show_main_menu()

    def show_test_connection(self, config: Dict):
        """Display test connection command"""
        self.app.clear_screen()
        print(f"{Colors.BOLD}Test Connection{Colors.END}\n")

        print("Copy and paste this command in a new terminal:\n")
        print(f"{Colors.CYAN}ssh {config['users'][0]['username']}@localhost -p {config['ssh_port']}{Colors.END}")
        print(f"\nPassword: {Colors.YELLOW}{config['users'][0]['password']}{Colors.END}")

        print(f"\n{Colors.BOLD}Once connected, try these commands:{Colors.END}")
        print("  ls /")
        print(f"  cat /etc/hostname")
        print("  whoami")
        print("  pwd")

        self.app.wait_for_input("\nPress Enter to continue...")
        self.show_medium_deployment_success(config)
