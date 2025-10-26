#!/usr/bin/env python3
"""
YAML Template Loader for HoneyMesh Medium Interaction Honeypots
Loads honeypot templates from YAML files
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import os


class YAMLTemplate:
    """Class to represent a honeypot template loaded from YAML"""
    
    def __init__(self, yaml_file: Path):
        self.yaml_file = yaml_file
        self.data = self._load_yaml()
        
        # Extract template information
        self.metadata = self.data.get('metadata', {})
        self.name = self.metadata.get('name', 'Unknown')
        self.description = self.metadata.get('description', '')
        self.category = self.metadata.get('category', 'general')
        self.version = self.metadata.get('version', '1.0')
        
        # Extract configuration
        self.config = self.data.get('configuration', {})
        self.hostname = self.config.get('hostname', 'honeypot.local')
        self.ssh_banner = self.config.get('ssh_banner', 'SSH-2.0-OpenSSH_8.4p1')
        self.timezone = self.config.get('timezone', 'US/Eastern')
        
        # Extract users
        self.users = self._parse_users()
        
        # Extract filesystem structure
        self.filesystem_structure = self.data.get('filesystem', {})
        
        # Extract file contents
        self.file_contents = self._parse_files()
        
        # Extract custom commands
        self.custom_commands = self._parse_custom_commands()
    
    def _load_yaml(self) -> Dict:
        """Load and parse YAML file"""
        try:
            with open(self.yaml_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load YAML template {self.yaml_file}: {str(e)}")
    
    def _parse_users(self) -> Dict[str, str]:
        """Parse users section and return username:password dict"""
        users = {}
        users_data = self.data.get('users', {})
        
        for username, user_info in users_data.items():
            if isinstance(user_info, dict):
                password = user_info.get('password', 'password123')
            else:
                password = str(user_info)
            users[username] = password
        
        return users
    
    def _parse_files(self) -> Dict[str, str]:
        """Parse files section and return filepath:content dict"""
        files = {}
        files_data = self.data.get('files', {})
        
        for filepath, file_info in files_data.items():
            if isinstance(file_info, dict):
                content = file_info.get('content', '')
            else:
                content = str(file_info)
            
            # Handle multiline strings properly
            if isinstance(content, str):
                files[filepath] = content
        
        return files
    
    def _parse_custom_commands(self) -> Dict[str, Dict]:
        """Parse custom commands section"""
        commands = {}
        commands_data = self.data.get('custom_commands', {})
        
        for cmd_name, cmd_info in commands_data.items():
            if isinstance(cmd_info, dict):
                commands[cmd_name] = {
                    'path': cmd_info.get('path', f'/usr/local/bin/{cmd_name}'),
                    'content': cmd_info.get('content', '#!/bin/bash\necho "Command not implemented"')
                }
            else:
                commands[cmd_name] = {
                    'path': f'/usr/local/bin/{cmd_name}',
                    'content': str(cmd_info)
                }
        
        return commands
    
    def get_filesystem_structure(self) -> Dict:
        """Return the filesystem directory structure"""
        return self.filesystem_structure
    
    def get_file_contents(self) -> Dict:
        """Return mapping of file paths to contents"""
        return self.file_contents
    
    def get_users(self) -> Dict:
        """Return user credentials dictionary"""
        return self.users
    
    def get_user_details(self) -> Dict:
        """Return detailed user information"""
        return self.data.get('users', {})
    
    def get_config(self) -> Dict:
        """Return honeypot configuration"""
        return {
            'hostname': self.hostname,
            'ssh_banner': self.ssh_banner,
            'timezone': self.timezone,
            'custom_commands': self.custom_commands
        }
    
    def get_motd(self) -> Optional[str]:
        """Get MOTD from files section"""
        return self.file_contents.get('/etc/motd')


class TemplateLibrary:
    """Manages collection of YAML templates"""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all YAML templates from directory"""
        if not self.templates_dir.exists():
            return
        
        for yaml_file in self.templates_dir.glob('*.yaml'):
            try:
                template = YAMLTemplate(yaml_file)
                template_id = yaml_file.stem  # Filename without extension
                self.templates[template_id] = template
            except Exception as e:
                print(f"Warning: Failed to load template {yaml_file}: {str(e)}")
    
    def get_template(self, template_id: str) -> Optional[YAMLTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                'id': template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'version': template.version
            }
            for template_id, template in self.templates.items()
        ]
    
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get templates filtered by category"""
        return [
            {
                'id': template_id,
                'name': template.name,
                'description': template.description
            }
            for template_id, template in self.templates.items()
            if template.category == category
        ]
    
    def reload_templates(self):
        """Reload all templates from disk"""
        self.templates = {}
        self._load_templates()
    
    def add_template_from_file(self, yaml_file: Path) -> bool:
        """Add a new template from a YAML file"""
        try:
            template = YAMLTemplate(yaml_file)
            template_id = yaml_file.stem
            self.templates[template_id] = template
            return True
        except Exception as e:
            print(f"Failed to add template: {str(e)}")
            return False


class TemplateExporter:
    """Export honeypot configuration as YAML template"""
    
    @staticmethod
    def export_to_yaml(honeypot_info: Dict, output_file: Path):
        """
        Export a deployed honeypot configuration as a reusable YAML template
        
        Args:
            honeypot_info: Dictionary with honeypot details
            output_file: Path to save YAML template
        """
        template_data = {
            'metadata': {
                'name': honeypot_info.get('name', 'Custom Template'),
                'description': f"Exported template from {honeypot_info.get('name')}",
                'category': 'custom',
                'version': '1.0',
                'author': 'HoneyMesh User'
            },
            'configuration': {
                'hostname': honeypot_info.get('hostname', 'server.local'),
                'ssh_banner': 'SSH-2.0-OpenSSH_8.4p1 Ubuntu-5ubuntu1.3',
                'timezone': 'US/Eastern'
            },
            'users': {}
        }
        
        # Add users
        for username, password in honeypot_info.get('users', {}).items():
            template_data['users'][username] = {
                'password': password,
                'uid': 1000 + len(template_data['users']),
                'gid': 1000 + len(template_data['users']),
                'home': f'/home/{username}',
                'shell': '/bin/bash',
                'gecos': username
            }
        
        # Add filesystem structure if available
        if 'filesystem' in honeypot_info:
            template_data['filesystem'] = honeypot_info['filesystem']
        
        # Add files if available
        if 'files' in honeypot_info:
            template_data['files'] = {}
            for filepath, content in honeypot_info['files'].items():
                template_data['files'][filepath] = {'content': content}
        
        # Add custom commands if available
        if 'custom_commands' in honeypot_info:
            template_data['custom_commands'] = {}
            for cmd_name, cmd_info in honeypot_info['custom_commands'].items():
                if isinstance(cmd_info, dict):
                    template_data['custom_commands'][cmd_name] = cmd_info
                else:
                    template_data['custom_commands'][cmd_name] = {
                        'path': f'/usr/local/bin/{cmd_name}',
                        'content': cmd_info
                    }
        
        # Write YAML file
        with open(output_file, 'w') as f:
            yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)


def create_filesystem_from_template(template: YAMLTemplate, base_path: Path):
    """
    Create physical filesystem structure from YAML template
    
    Args:
        template: YAMLTemplate object
        base_path: Base directory to create structure in
    """
    def create_dirs(structure: Dict, current_path: Path):
        """Recursively create directory structure"""
        for name, subdirs in structure.items():
            dir_path = current_path / name
            dir_path.mkdir(parents=True, exist_ok=True)
            if isinstance(subdirs, dict) and subdirs:
                create_dirs(subdirs, dir_path)
    
    # Create standard Linux directories first
    standard_dirs = [
        'proc', 'sys', 'dev', 'run', 'tmp',
        'usr/bin', 'usr/sbin', 'usr/local/bin',
        'sbin', 'lib', 'bin', 'etc', 'var/log',
        'opt', 'home', 'root'
    ]
    
    for dir_path in standard_dirs:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create template-specific directories
    create_dirs(template.get_filesystem_structure(), base_path)
    
    # Create user home directories
    for username in template.get_users().keys():
        user_home = base_path / 'home' / username
        user_home.mkdir(parents=True, exist_ok=True)
        (user_home / '.ssh').mkdir(exist_ok=True)


def write_files_from_template(template: YAMLTemplate, base_path: Path):
    """
    Write file contents from YAML template
    
    Args:
        template: YAMLTemplate object
        base_path: Base directory containing filesystem structure
    """
    # Write /etc/passwd
    passwd_content = "root:x:0:0:root:/root:/bin/bash\n"
    
    user_details = template.get_user_details()
    for username, user_info in user_details.items():
        if isinstance(user_info, dict):
            uid = user_info.get('uid', 1000)
            gid = user_info.get('gid', 1000)
            home = user_info.get('home', f'/home/{username}')
            shell = user_info.get('shell', '/bin/bash')
            gecos = user_info.get('gecos', username)
            passwd_content += f"{username}:x:{uid}:{gid}:{gecos}:{home}:{shell}\n"
        else:
            uid = 1000 + len(passwd_content.split('\n'))
            passwd_content += f"{username}:x:{uid}:{uid}::/home/{username}:/bin/bash\n"
    
    passwd_file = base_path / 'etc' / 'passwd'
    passwd_file.parent.mkdir(parents=True, exist_ok=True)
    with open(passwd_file, 'w') as f:
        f.write(passwd_content)
    
    # Write template files
    for filepath, content in template.get_file_contents().items():
        file_path = base_path / filepath.lstrip('/')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)


def create_custom_commands_from_template(template: YAMLTemplate, txtcmds_path: Path):
    """
    Create custom command scripts from YAML template
    
    Args:
        template: YAMLTemplate object
        txtcmds_path: Path to txtcmds directory
    """
    config = template.get_config()
    for cmd_name, cmd_info in config.get('custom_commands', {}).items():
        cmd_path_str = cmd_info['path']
        cmd_content = cmd_info['content']
        
        # Remove leading slash and create under txtcmds
        cmd_path = txtcmds_path / cmd_path_str.lstrip('/')
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cmd_path, 'w') as f:
            f.write(cmd_content)
        
        # Make executable
        os.chmod(cmd_path, 0o755)


# Example usage
if __name__ == "__main__":
    # Load templates
    library = TemplateLibrary(Path('./templates'))
    
    print("Available Templates:")
    print("=" * 50)
    for template_info in library.list_templates():
        print(f"ID: {template_info['id']}")
        print(f"Name: {template_info['name']}")
        print(f"Description: {template_info['description']}")
        print(f"Category: {template_info['category']}")
        print("-" * 50)
    
    # Load specific template
    template = library.get_template('epic_healthcare')
    if template:
        print(f"\nLoaded template: {template.name}")
        print(f"Hostname: {template.hostname}")
        print(f"Users: {list(template.get_users().keys())}")
        print(f"Custom Commands: {list(template.get_config()['custom_commands'].keys())}")
