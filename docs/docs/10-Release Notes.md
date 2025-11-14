# HoneyMesh v1.0.0 Release

**Release Date:** November 14, 2025
**Status:** Alpha Release
**Version:** 1.0.0

---

## Overview

We are excited to announce the initial alpha release of **HoneyMesh**, a self-hosted honeypot deployment platform designed to simplify honeypot creation and management for security professionals, researchers, and educational institutions.

HoneyMesh provides an intuitive command-line interface for deploying and managing SSH/Telnet honeypots with integrated logging and analytics, featuring customizable deployment templates for various industry scenarios.

---

## Key Features

### Core Platform

- **Interactive CLI Interface**: User-friendly command-line interface with colored output and ASCII art banner
- **Multi-Deployment Support**: Manage multiple honeypot deployments simultaneously
- **Docker-Based Architecture**: Containerized services for easy deployment and isolation
- **Comprehensive Logging**: Detailed logging to file for debugging and audit trails
- **Health Monitoring**: Real-time service health checks and status monitoring

### Deployment Modes

#### Default Mode (SSH + Telnet Honeypots)
- **Cowrie Honeypot**: Industry-standard SSH/Telnet honeypot
- **Customizable Ports**: Configure SSH and Telnet ports
- **Hostname Customization**: Set custom hostnames and SSH banners
- **User Database**: Pre-configured with common username/password combinations
- **Filesystem Simulation**: Realistic Linux filesystem with passwd, group, and shadow files

#### Medium Interaction Mode
- **Industry Templates**: Pre-built templates for specific scenarios:
  - **Epic Healthcare Server**: Simulates Epic EMR production environment
  - **Financial Services**: Mimics banking/financial institution servers
  - **Corporate IT Infrastructure**: Generic enterprise Linux server environment
- **Custom Template Builder**: Interactive wizard for creating custom honeypot templates
- **Template Components**:
  - Custom filesystem structures
  - User accounts and permissions
  - File content simulation
  - Custom command outputs
  - Network service emulation

### ELK Stack Integration

- **Elasticsearch**: Stores and indexes honeypot interaction logs
- **Logstash**: Processes and enriches log data with GeoIP information
- **Kibana**: Web-based dashboard for log visualization and analysis
- **Filebeat**: Collects and ships Cowrie JSON logs to Logstash

### Management Console

- **Service Status & Health**: View detailed status of all services
- **Live Log Monitoring**: Real-time view of honeypot activity
- **Service Restart**: Restart individual or all services
- **Configuration Management**: View and modify deployment settings
- **Backup Functionality**: Backup deployment data and configurations
- **Deployment Removal**: Clean removal of deployments with data preservation

### Security Features

- **Isolated Networks**: Docker bridge networks for service isolation
- **External Access Control**: Optional external Kibana access with warnings
- **Port Conflict Detection**: Automatic checking for port availability
- **Privilege Management**: Runs containers with appropriate user permissions
- **Dependency Verification**: Pre-flight checks for required dependencies

---

## Technical Specifications

### Container Stack
- **Elasticsearch**: v8.11.0 - Log storage and indexing
- **Kibana**: v8.11.0 - Visualization dashboard
- **Logstash**: v8.11.0 - Log processing pipeline
- **Filebeat**: v8.11.0 - Log shipper
- **Cowrie**: Latest - SSH/Telnet honeypot

### System Requirements
- **Operating System**: Linux (Ubuntu/Debian recommended)
- **Docker**: v20.10 or higher
- **Docker Compose**: v1.29 or higher
- **Python**: v3.6 or higher
- **Disk Space**: Minimum 5GB free space
- **Memory**: Recommended 4GB RAM minimum
- **Network**: Ports 2222, 2223, 5601, 9200 available (configurable)

### Python Dependencies
- `docker` - Docker SDK for Python
- `pyyaml` - YAML configuration parsing
- `requests` - HTTP client for health checks

---

## Installation

```bash
# Clone the repository
git clone https://github.com/rayzax/HoneyMesh

# Change to HoneyMesh directory
cd HoneyMesh

# Make installation script executable
sudo chmod +x installDependencies.sh

# Run installation script
sudo ./installDependencies.sh

# Log out and back in to apply Docker permissions
# Then run HoneyMesh
python3 honeymesh.py
```

---

## Default Configuration

### Ports
- SSH Honeypot: 2222
- Telnet Honeypot: 2223 (optional)
- Kibana Dashboard: 5601
- Elasticsearch: 9200 (internal)
- Logstash: 5044, 9600 (internal)

### Default Credentials (Honeypot)
The honeypot accepts common username/password combinations including:
- root:123456
- admin:123456
- user:123456
- test:test
- guest:guest

---

## Pre-Built Templates

### 1. Epic Healthcare Server
Simulates an Epic EMR (Electronic Medical Records) production environment:
- Healthcare-specific filesystem structure
- Medical application directories
- HIPAA compliance indicators
- Epic-specific service simulation

### 2. Financial Services
Mimics a banking/financial institution server:
- Financial application directories
- Banking system indicators
- Transaction processing structure
- Compliance-related directories

### 3. Corporate IT Infrastructure
Generic enterprise Linux server environment:
- Standard corporate directory structure
- IT management tools
- Enterprise application frameworks
- Common business applications

---

## Usage Highlights

### Quick Start
1. Run `python3 honeymesh.py`
2. Select deployment type (Default or Medium Interaction)
3. Configure ports and settings
4. Deploy and monitor via Kibana dashboard

### Management Console Features
- **[S]** Service status & health monitoring
- **[L]** Live log viewing
- **[R]** Restart services
- **[C]** Change configuration
- **[B]** Backup deployment
- **[D]** Stop & remove deployment

### Template Builder Wizard
The medium interaction mode includes an interactive wizard for creating custom templates:
- Guided metadata configuration
- User account creation
- Filesystem structure design
- Custom file content
- Command output customization

---

## Data Collection

HoneyMesh captures comprehensive interaction data including:
- Source IP addresses (with GeoIP enrichment)
- Attempted usernames and passwords
- Executed commands
- Downloaded files
- Session recordings (TTY logs)
- Connection timestamps
- Protocol-specific metadata

---

## Log Storage

### Default Mode
- Configuration: `./honeypot-data/config.json`
- Cowrie Logs: `./honeypot-data/logs/cowrie.json`
- Docker Compose: `./honeypot-data/docker-compose.yml`
- System Logs: `./honeymesh-logs/honeymesh_*.log`

### Medium Interaction Mode
- Deployment Data: `./honeypot-data/medium/[deployment-name]/`
- Template Files: `./medium/templates/*.yaml`

---

## Known Limitations (Alpha Release)

1. **Configuration Changes**: Require service restart to take effect
2. **High Interaction Mode**: Not yet implemented (coming in future release)
3. **Advanced Config Editing**: Limited in-app configuration modification
4. **Real-time Log Monitoring**: Shows recent logs only, not live streaming
5. **Template Validation**: Limited validation of custom template syntax
6. **Multi-User Support**: Single-user operation only
7. **Remote Management**: No web-based management interface yet

---

## Security Considerations

### Important Warnings

1. **Network Exposure**: Honeypots intentionally expose services to potential attackers
2. **Isolated Networks**: Deploy only on networks you own or have permission to test
3. **Legal Compliance**: Ensure compliance with local laws and regulations
4. **Production Networks**: Never deploy on production or sensitive networks without proper safeguards
5. **Data Privacy**: Captured data may include personal information - handle appropriately
6. **Containment**: Monitor honeypot activity to prevent use as attack platform

### Best Practices

- Deploy in isolated, monitored environments
- Regularly review captured logs and activities
- Keep Docker and system packages updated
- Use firewall rules to restrict honeypot network access
- Implement log retention policies
- Back up configurations and data regularly

---

## Disclaimer

HoneyMesh is intended for **educational, research, and security testing purposes only**. Deploying honeypots involves exposing services to potential attackers. Users must ensure they have explicit permission to run HoneyMesh on any network or system.

The creators and contributors of HoneyMesh are **not responsible** for any misuse, damage, or legal consequences arising from the deployment or use of this software. Always follow applicable laws, regulations, and organizational policies when using HoneyMesh.

---

## Roadmap

### Planned for v1.1.0
- Template validation and testing
- Centralized cluster manager for multiple honeypots
- Elastic pipeline improvements
- General bug fixes
- Default high interaction mode

---

## Contributing

We welcome contributions from the community! Areas where we'd appreciate help:
- Additional industry templates
- Documentation improvements
- Bug reports and fixes
- Feature suggestions
- Performance optimizations
- Security enhancements

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/rayzax/HoneyMesh/issues
- Documentation: See README.md

---

## Acknowledgments

This project builds upon the excellent work of:
- **Cowrie Honeypot Project**: SSH/Telnet honeypot implementation
- **Elastic Stack**: Log aggregation and visualization
- **Docker Community**: Containerization platform

---

## License

Please refer to the LICENSE file in the repository for licensing information.

---

## Version History

### v1.0.0 (2025-11-14) - Initial Alpha Release
- First public release
- Default SSH/Telnet honeypot deployment
- Medium interaction with template support
- ELK stack integration
- Management console
- Three pre-built industry templates
- Interactive template builder wizard
- Multi-deployment support

---

**Thank you for trying HoneyMesh v1.0.0!**

We look forward to your feedback and contributions as we continue to develop and improve this platform for the security research community.


