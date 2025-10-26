#!/usr/bin/env python3
"""
Interactive Template Builder for HoneyMesh
User-friendly UI for creating custom YAML honeypot templates
"""

import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


class TemplateBuilder:
    """Interactive template builder with user-friendly interface"""
    
    def __init__(self):
        self.template = {
            'metadata': {},
            'configuration': {},
            'users': {},
            'filesystem': {},
            'files': {},
            'custom_commands': {}
        }
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")
    
    def print_section(self, text: str):
        """Print section header"""
        print(f"\n{Colors.YELLOW}{Colors.BOLD}>>> {text}{Colors.END}")
        print(f"{Colors.YELLOW}{'─' * 70}{Colors.END}")
    
    def get_input(self, prompt: str, default: str = "") -> str:
        """Get user input with optional default"""
        if default:
            user_input = input(f"{Colors.WHITE}{prompt} [{Colors.GREEN}{default}{Colors.END}{Colors.WHITE}]: {Colors.END}").strip()
            return user_input if user_input else default
        else:
            return input(f"{Colors.WHITE}{prompt}: {Colors.END}").strip()
    
    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input"""
        default_str = "Y/n" if default else "y/N"
        while True:
            choice = input(f"{Colors.WHITE}{prompt} [{default_str}]: {Colors.END}").strip().lower()
            if not choice:
                return default
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")
    
    def get_multiline_input(self, prompt: str, end_marker: str = "END") -> str:
        """Get multiline text input"""
        print(f"{Colors.WHITE}{prompt}{Colors.END}")
        print(f"{Colors.YELLOW}(Type '{end_marker}' on a new line to finish){Colors.END}")
        lines = []
        while True:
            line = input()
            if line.strip() == end_marker:
                break
            lines.append(line)
        return '\n'.join(lines)
    
    def choose_from_list(self, items: List[str], prompt: str = "Select option") -> Optional[str]:
        """Display list and get user selection"""
        if not items:
            return None
        
        for i, item in enumerate(items, 1):
            print(f"  {Colors.GREEN}[{i}]{Colors.END} {item}")
        
        print(f"  {Colors.YELLOW}[0]{Colors.END} Cancel")
        
        while True:
            try:
                choice = int(input(f"\n{Colors.WHITE}{prompt}: {Colors.END}").strip())
                if choice == 0:
                    return None
                if 1 <= choice <= len(items):
                    return items[choice - 1]
                print(f"{Colors.RED}Invalid selection{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a number{Colors.END}")
    
    def run(self):
        """Main template builder flow"""
        self.clear_screen()
        self.print_header("HoneyMesh Template Builder")
        
        print(f"{Colors.CYAN}Create custom honeypot templates with ease!{Colors.END}\n")
        
        # Step 1: Metadata
        self.build_metadata()
        
        # Step 2: Configuration
        self.build_configuration()
        
        # Step 3: Users
        self.build_users()
        
        # Step 4: Filesystem
        self.build_filesystem()
        
        # Step 5: Files
        self.build_files()
        
        # Step 6: Custom Commands
        self.build_custom_commands()
        
        # Step 7: Review and Save
        self.review_and_save()
    
    def build_metadata(self):
        """Build template metadata"""
        self.clear_screen()
        self.print_header("Step 1: Template Metadata")
        
        self.template['metadata']['name'] = self.get_input("Template name", "My Custom Template")
        self.template['metadata']['description'] = self.get_input("Description", "Custom honeypot template")
        
        print(f"\n{Colors.CYAN}Available categories:{Colors.END}")
        categories = ['healthcare', 'financial', 'corporate', 'education', 'government', 'retail', 'custom']
        for cat in categories:
            print(f"  • {cat}")
        
        self.template['metadata']['category'] = self.get_input("Category", "custom")
        self.template['metadata']['version'] = self.get_input("Version", "1.0")
        self.template['metadata']['author'] = self.get_input("Author", "HoneyMesh User")
        
        print(f"\n{Colors.GREEN}✓ Metadata configured{Colors.END}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def build_configuration(self):
        """Build system configuration"""
        self.clear_screen()
        self.print_header("Step 2: System Configuration")
        
        self.template['configuration']['hostname'] = self.get_input("Hostname", "server-prd-01.local")
        self.template['configuration']['ssh_banner'] = self.get_input(
            "SSH Banner", 
            "SSH-2.0-OpenSSH_8.4p1 Ubuntu-5ubuntu1.3"
        )
        
        print(f"\n{Colors.CYAN}Common timezones:{Colors.END}")
        timezones = ['US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific', 'UTC', 'Europe/London']
        for tz in timezones:
            print(f"  • {tz}")
        
        self.template['configuration']['timezone'] = self.get_input("Timezone", "US/Eastern")
        
        print(f"\n{Colors.GREEN}✓ Configuration set{Colors.END}")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def build_users(self):
        """Build user accounts"""
        self.clear_screen()
        self.print_header("Step 3: User Accounts")
        
        print(f"{Colors.CYAN}Add user accounts for the honeypot{Colors.END}\n")
        
        uid_counter = 1001
        
        while True:
            print(f"\n{Colors.YELLOW}Current users: {len(self.template['users'])}{Colors.END}")
            if self.template['users']:
                for username in self.template['users'].keys():
                    print(f"  • {username}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Add user")
            print(f"{Colors.YELLOW}[2]{Colors.END} Add user (advanced)")
            print(f"{Colors.RED}[3]{Colors.END} Remove user")
            print(f"{Colors.WHITE}[0]{Colors.END} Continue")
            
            choice = self.get_input("\nSelect option", "0")
            
            if choice == '1':
                self.add_simple_user(uid_counter)
                uid_counter += 1
            elif choice == '2':
                self.add_advanced_user(uid_counter)
                uid_counter += 1
            elif choice == '3':
                self.remove_user()
            elif choice == '0':
                if not self.template['users']:
                    print(f"{Colors.YELLOW}Warning: No users defined. Adding default user 'admin'{Colors.END}")
                    self.template['users']['admin'] = {
                        'password': 'admin123',
                        'uid': 1001,
                        'gid': 1001,
                        'home': '/home/admin',
                        'shell': '/bin/bash',
                        'gecos': 'Administrator'
                    }
                break
    
    def add_simple_user(self, uid: int):
        """Add user with basic configuration"""
        print(f"\n{Colors.CYAN}Add User (Simple Mode){Colors.END}")
        username = self.get_input("Username")
        if not username:
            return
        
        password = self.get_input("Password", "password123")
        gecos = self.get_input("Full name/description", username)
        
        self.template['users'][username] = {
            'password': password,
            'uid': uid,
            'gid': uid,
            'home': f'/home/{username}',
            'shell': '/bin/bash',
            'gecos': gecos
        }
        
        print(f"{Colors.GREEN}✓ User '{username}' added{Colors.END}")
    
    def add_advanced_user(self, uid: int):
        """Add user with advanced configuration"""
        print(f"\n{Colors.CYAN}Add User (Advanced Mode){Colors.END}")
        username = self.get_input("Username")
        if not username:
            return
        
        password = self.get_input("Password", "password123")
        uid_input = self.get_input("UID", str(uid))
        gid_input = self.get_input("GID", uid_input)
        home = self.get_input("Home directory", f"/home/{username}")
        shell = self.get_input("Shell", "/bin/bash")
        gecos = self.get_input("GECOS (full name)", username)
        
        self.template['users'][username] = {
            'password': password,
            'uid': int(uid_input),
            'gid': int(gid_input),
            'home': home,
            'shell': shell,
            'gecos': gecos
        }
        
        print(f"{Colors.GREEN}✓ User '{username}' added{Colors.END}")
    
    def remove_user(self):
        """Remove a user"""
        if not self.template['users']:
            print(f"{Colors.RED}No users to remove{Colors.END}")
            return
        
        username = self.choose_from_list(list(self.template['users'].keys()), "Select user to remove")
        if username:
            del self.template['users'][username]
            print(f"{Colors.GREEN}✓ User '{username}' removed{Colors.END}")
    
    def build_filesystem(self):
        """Build filesystem structure"""
        self.clear_screen()
        self.print_header("Step 4: Filesystem Structure")
        
        print(f"{Colors.CYAN}Define custom directory structure{Colors.END}")
        print(f"{Colors.YELLOW}Standard Linux directories will be added automatically{Colors.END}\n")
        
        print(f"{Colors.GREEN}[1]{Colors.END} Quick mode (add directories one by one)")
        print(f"{Colors.GREEN}[2]{Colors.END} Batch mode (paste directory tree)")
        print(f"{Colors.GREEN}[3]{Colors.END} Template mode (use predefined structure)")
        print(f"{Colors.WHITE}[0]{Colors.END} Skip")
        
        choice = self.get_input("\nSelect mode", "1")
        
        if choice == '1':
            self.build_filesystem_quick()
        elif choice == '2':
            self.build_filesystem_batch()
        elif choice == '3':
            self.build_filesystem_template()
    
    def build_filesystem_quick(self):
        """Quick mode for adding directories"""
        print(f"\n{Colors.CYAN}Quick Mode - Add Directories{Colors.END}")
        print(f"{Colors.YELLOW}Enter directory paths (e.g., /opt/myapp/data){Colors.END}")
        print(f"{Colors.YELLOW}Press Enter on empty line to finish{Colors.END}\n")
        
        while True:
            path = input(f"{Colors.WHITE}Directory path: {Colors.END}").strip()
            if not path:
                break
            
            if not path.startswith('/'):
                path = '/' + path
            
            self.add_directory_to_filesystem(path)
            print(f"{Colors.GREEN}✓ Added: {path}{Colors.END}")
    
    def build_filesystem_batch(self):
        """Batch mode for pasting directory tree"""
        print(f"\n{Colors.CYAN}Batch Mode - Paste Directory Tree{Colors.END}")
        print(f"{Colors.YELLOW}Paste your directory structure (one per line){Colors.END}")
        print(f"{Colors.YELLOW}Type 'END' on a new line to finish{Colors.END}\n")
        
        lines = []
        while True:
            line = input().strip()
            if line == 'END':
                break
            if line:
                lines.append(line)
        
        for line in lines:
            # Clean up the path (remove tree characters, spaces, etc.)
            path = line.replace('├──', '').replace('└──', '').replace('│', '').strip()
            if path and not path.startswith('#'):
                if not path.startswith('/'):
                    path = '/' + path
                self.add_directory_to_filesystem(path)
        
        print(f"{Colors.GREEN}✓ Added {len(lines)} directories{Colors.END}")
    
    def build_filesystem_template(self):
        """Use predefined filesystem templates"""
        print(f"\n{Colors.CYAN}Template Mode - Predefined Structures{Colors.END}\n")
        
        templates = {
            'Web Server': {
                'var': {'www': {'html': {}, 'apps': {}}, 'log': {'apache2': {}, 'nginx': {}}},
                'opt': {'applications': {}},
                'srv': {'www': {}}
            },
            'Database Server': {
                'var': {'lib': {'mysql': {}, 'postgresql': {}}},
                'opt': {'database': {'backup': {}, 'data': {}}},
                'etc': {'mysql': {}, 'postgresql': {}}
            },
            'Application Server': {
                'opt': {'application': {'bin': {}, 'lib': {}, 'config': {}}},
                'var': {'application': {'data': {}, 'logs': {}, 'temp': {}}},
                'srv': {'application': {}}
            }
        }
        
        template_name = self.choose_from_list(list(templates.keys()), "Select template")
        if template_name:
            self.template['filesystem'].update(templates[template_name])
            print(f"{Colors.GREEN}✓ Applied '{template_name}' template{Colors.END}")
    
    def add_directory_to_filesystem(self, path: str):
        """Add a directory path to filesystem structure"""
        parts = [p for p in path.split('/') if p]
        current = self.template['filesystem']
        
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    def build_files(self):
        """Build file contents"""
        self.clear_screen()
        self.print_header("Step 5: File Contents")
        
        print(f"{Colors.CYAN}Add file contents to your honeypot{Colors.END}\n")
        
        # Always add essential files
        self.add_essential_files()
        
        while True:
            print(f"\n{Colors.YELLOW}Current files: {len(self.template['files'])}{Colors.END}")
            if self.template['files']:
                for filepath in list(self.template['files'].keys())[:10]:
                    print(f"  • {filepath}")
                if len(self.template['files']) > 10:
                    print(f"  ... and {len(self.template['files']) - 10} more")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Add file")
            print(f"{Colors.YELLOW}[2]{Colors.END} Edit file")
            print(f"{Colors.RED}[3]{Colors.END} Remove file")
            print(f"{Colors.BLUE}[4]{Colors.END} Import file from disk")
            print(f"{Colors.WHITE}[0]{Colors.END} Continue")
            
            choice = self.get_input("\nSelect option", "0")
            
            if choice == '1':
                self.add_file()
            elif choice == '2':
                self.edit_file()
            elif choice == '3':
                self.remove_file()
            elif choice == '4':
                self.import_file()
            elif choice == '0':
                break
    
    def add_essential_files(self):
        """Add essential system files automatically"""
        hostname = self.template['configuration'].get('hostname', 'server.local')
        
        # Hostname
        self.template['files']['/etc/hostname'] = {'content': hostname}
        
        # MOTD
        if '/etc/motd' not in self.template['files']:
            motd = f"""{'=' * 70}
    {self.template['metadata']['name'].upper()}
    {hostname}
{'=' * 70}

WARNING: Authorized access only. All activity is monitored and logged.

{'=' * 70}
"""
            self.template['files']['/etc/motd'] = {'content': motd}
        
        print(f"{Colors.GREEN}✓ Essential files added automatically{Colors.END}")
    
    def add_file(self):
        """Add a new file"""
        print(f"\n{Colors.CYAN}Add File{Colors.END}")
        filepath = self.get_input("File path (e.g., /etc/config.conf)")
        if not filepath:
            return
        
        if not filepath.startswith('/'):
            filepath = '/' + filepath
        
        print(f"\n{Colors.YELLOW}Choose input method:{Colors.END}")
        print(f"{Colors.GREEN}[1]{Colors.END} Type content (multiline)")
        print(f"{Colors.GREEN}[2]{Colors.END} Single line content")
        
        method = self.get_input("Method", "1")
        
        if method == '1':
            content = self.get_multiline_input(f"Enter content for {filepath}")
        else:
            content = self.get_input("Content")
        
        self.template['files'][filepath] = {'content': content}
        print(f"{Colors.GREEN}✓ File '{filepath}' added{Colors.END}")
    
    def edit_file(self):
        """Edit existing file"""
        if not self.template['files']:
            print(f"{Colors.RED}No files to edit{Colors.END}")
            return
        
        filepath = self.choose_from_list(list(self.template['files'].keys()), "Select file to edit")
        if filepath:
            print(f"\n{Colors.CYAN}Current content:{Colors.END}")
            print(self.template['files'][filepath]['content'][:200])
            if len(self.template['files'][filepath]['content']) > 200:
                print("...")
            
            content = self.get_multiline_input(f"\nEnter new content for {filepath}")
            self.template['files'][filepath] = {'content': content}
            print(f"{Colors.GREEN}✓ File '{filepath}' updated{Colors.END}")
    
    def remove_file(self):
        """Remove a file"""
        if not self.template['files']:
            print(f"{Colors.RED}No files to remove{Colors.END}")
            return
        
        filepath = self.choose_from_list(list(self.template['files'].keys()), "Select file to remove")
        if filepath:
            del self.template['files'][filepath]
            print(f"{Colors.GREEN}✓ File '{filepath}' removed{Colors.END}")
    
    def import_file(self):
        """Import file from disk"""
        print(f"\n{Colors.CYAN}Import File from Disk{Colors.END}")
        source_path = self.get_input("Source file path")
        if not source_path or not Path(source_path).exists():
            print(f"{Colors.RED}File not found{Colors.END}")
            return
        
        dest_path = self.get_input("Destination path in honeypot (e.g., /etc/config.conf)")
        if not dest_path.startswith('/'):
            dest_path = '/' + dest_path
        
        try:
            with open(source_path, 'r') as f:
                content = f.read()
            
            self.template['files'][dest_path] = {'content': content}
            print(f"{Colors.GREEN}✓ File imported: {dest_path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Error importing file: {str(e)}{Colors.END}")
    
    def build_custom_commands(self):
        """Build custom commands"""
        self.clear_screen()
        self.print_header("Step 6: Custom Commands")
        
        print(f"{Colors.CYAN}Add custom shell commands (optional){Colors.END}\n")
        
        add_commands = self.get_yes_no("Add custom commands?", False)
        if not add_commands:
            return
        
        while True:
            print(f"\n{Colors.YELLOW}Current commands: {len(self.template['custom_commands'])}{Colors.END}")
            if self.template['custom_commands']:
                for cmd_name in self.template['custom_commands'].keys():
                    print(f"  • {cmd_name}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Add command")
            print(f"{Colors.RED}[2]{Colors.END} Remove command")
            print(f"{Colors.WHITE}[0]{Colors.END} Continue")
            
            choice = self.get_input("\nSelect option", "0")
            
            if choice == '1':
                self.add_custom_command()
            elif choice == '2':
                self.remove_custom_command()
            elif choice == '0':
                break
    
    def add_custom_command(self):
        """Add a custom command"""
        print(f"\n{Colors.CYAN}Add Custom Command{Colors.END}")
        cmd_name = self.get_input("Command name (e.g., app-status)")
        if not cmd_name:
            return
        
        cmd_path = self.get_input("Command path", f"/usr/local/bin/{cmd_name}")
        
        print(f"\n{Colors.YELLOW}Enter command script:{Colors.END}")
        script = self.get_multiline_input("#!/bin/bash")
        
        # Add shebang if not present
        if not script.startswith('#!'):
            script = "#!/bin/bash\n" + script
        
        self.template['custom_commands'][cmd_name] = {
            'path': cmd_path,
            'content': script
        }
        
        print(f"{Colors.GREEN}✓ Command '{cmd_name}' added{Colors.END}")
    
    def remove_custom_command(self):
        """Remove a custom command"""
        if not self.template['custom_commands']:
            print(f"{Colors.RED}No commands to remove{Colors.END}")
            return
        
        cmd_name = self.choose_from_list(
            list(self.template['custom_commands'].keys()), 
            "Select command to remove"
        )
        if cmd_name:
            del self.template['custom_commands'][cmd_name]
            print(f"{Colors.GREEN}✓ Command '{cmd_name}' removed{Colors.END}")
    
    def review_and_save(self):
        """Review template and save"""
        self.clear_screen()
        self.print_header("Step 7: Review and Save")
        
        print(f"{Colors.CYAN}Template Summary:{Colors.END}\n")
        print(f"{Colors.BOLD}Name:{Colors.END} {self.template['metadata']['name']}")
        print(f"{Colors.BOLD}Description:{Colors.END} {self.template['metadata']['description']}")
        print(f"{Colors.BOLD}Hostname:{Colors.END} {self.template['configuration']['hostname']}")
        print(f"{Colors.BOLD}Users:{Colors.END} {len(self.template['users'])}")
        print(f"{Colors.BOLD}Directories:{Colors.END} {self.count_directories(self.template['filesystem'])}")
        print(f"{Colors.BOLD}Files:{Colors.END} {len(self.template['files'])}")
        print(f"{Colors.BOLD}Custom Commands:{Colors.END} {len(self.template['custom_commands'])}")
        
        print(f"\n{Colors.YELLOW}Save this template?{Colors.END}")
        if not self.get_yes_no("Proceed with save", True):
            print(f"{Colors.RED}Template not saved{Colors.END}")
            return
        
        # Generate filename
        default_filename = self.template['metadata']['name'].lower().replace(' ', '_') + '.yaml'
        filename = self.get_input("Filename", default_filename)
        
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        
        output_path = Path('templates') / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to YAML
        with open(output_path, 'w') as f:
            yaml.dump(self.template, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Template saved successfully!{Colors.END}")
        print(f"{Colors.CYAN}Location: {output_path}{Colors.END}")
        print(f"\n{Colors.YELLOW}You can now use this template in HoneyMesh!{Colors.END}")
    
    def count_directories(self, structure: Dict) -> int:
        """Count total directories in structure"""
        count = 0
        for key, value in structure.items():
            count += 1
            if isinstance(value, dict):
                count += self.count_directories(value)
        return count


def main():
    """Run the template builder"""
    try:
        builder = TemplateBuilder()
        builder.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Template builder cancelled{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
