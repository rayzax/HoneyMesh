<img width="85" height="84" alt="image" src="https://github.com/user-attachments/assets/68ead79b-5888-4a03-a5da-18c2e8647711" />

# HoneyMesh

A self-hosted honeypot deployment platform inspired by T-Pot that simplifies honeypot creation and management for security professionals and educational institutions.

## About HoneyMesh

HoneyMesh provides an interactive CLI interface for deploying production-ready honeypots with integrated logging and analysis. The platform focuses on usability improvements and industry-specific customization while leveraging proven open-source honeypot technologies.

## Features
- Full stack Python CLI for honeypot orchestration, customization, and deployment
- Custom Cowrie honeypot builder
- Honeypot Management Console
- ELK stack integration for analysis

## Architecture/Design Overview

<img width="1464" height="341" alt="diagram-export-10-7-2025-8_39_23-PM" src="https://github.com/user-attachments/assets/6f6ac830-6ba4-4ae4-b9c9-3cdcb34868cf" />


**Data Flow:**
1. Attacker connects to honeypot
2. Cowrie logs interaction as JSON
3. Filebeat ships logs to Logstash
4. Logstash enriches with GeoIP data
5. Elasticsearch stores and indexes
6. Kibana visualizes attacks

**Tech Stack:**
- Docker & Docker Compose for orchestration
- Cowrie for SSH/Telnet honeypot
- ELK stack for logging and analysis
- Python CLI for management

## Installation

**Prerequisites:**
- Ubuntu 20.04+ (or compatible Linux)
- Docker 20.10+
- Docker Compose 1.29+
- User in the docker user group
- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- 25GB free disk space

**Quick Install:**

```bash
# Clone repository
git clone https://github.com/yourusername/honeymesh.git
cd honeymesh

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Run HoneyMesh
python3 honeymesh.py
```

Then follow the interactive wizard to configure and deploy your honeypot.

## Usage

**Starting HoneyMesh:**
```bash
python3 honeymesh.py
```

**Main Menu:**

<img width="635" height="373" alt="image" src="https://github.com/user-attachments/assets/cabe351a-6a05-46e7-9abd-29eaae6dc380" />


**Management Console:**

<img width="457" height="373" alt="image" src="https://github.com/user-attachments/assets/322c9ea4-9b8f-405e-938a-5fd0e52c4553" />


**Accessing Services:**
```bash
# SSH honeypot
ssh user@localhost -p 2222

# Kibana dashboard
http://localhost:5601

# View logs
tail -f ./honeypot-data/logs/cowrie.json
```

## Configuration

**Port Configuration:**
- SSH Honeypot: 2222 (configurable during setup)
- Telnet Honeypot: 2223 (optional)
- Kibana Dashboard: 5601 (configurable)
- Elasticsearch: 9200

**Files:**
- `honeypot-data/config/cowrie.cfg` - Cowrie configuration
- `honeypot-data/docker-compose.yml` - Service definitions
- `honeypot-data/elk-config/` - ELK stack configurations

**Customization:**
- Modify hostname and SSH banner in cowrie.cfg
- Choose from a library of custom honeypots that mimic vulnerable industry specific servers
- Build your own custom honeypots and filesystems
- Configure log retention and storage paths

## Logging and Analysis

**Log Format:**
All events logged as JSON with:
- Timestamp
- Source IP with GeoIP data
- Event type (login, command, file transfer)
- Session details
- Username/password attempts
- Commands executed

**Key Events:**
- `cowrie.login.success/failed` - Authentication attempts
- `cowrie.command.input` - Commands executed
- `cowrie.session.file_download` - Downloaded files
- `cowrie.session.connect/closed` - Connection events

**Analysis:**
Use Kibana to:
- Map attack origins geographically
- Identify common credentials used
- Track command execution patterns
- Monitor session durations
- Export data for further analysis

## The Future of HoneyMesh

**Roadmap:**
- High-interaction honeypot library with fully dedicated VMs for every attack session
- Customizable high-interaction virtual machines
- Clustered deployment of honeypots with centralized management

## Security and Ethical Disclaimers

**WARNING:**

HoneyMesh deploys honeypots that expose services to attackers. You MUST:
- Only use on networks you own or have explicit permission to test
- Comply with all applicable laws and regulations
- Implement proper network segmentation and security controls
- Handle captured data responsibly and ethically
- Not use captured credentials for unauthorized access

**Disclaimer:**
The authors are not responsible for misuse, damages, or legal consequences resulting from the use of this software. By using HoneyMesh, you accept full responsibility for its deployment and operation.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgements / Credits

**Built with:**
- [Cowrie](https://github.com/cowrie/cowrie) - SSH/Telnet honeypot
- [Elasticsearch](https://www.elastic.co/elasticsearch/) - Search and analytics
- [Logstash](https://www.elastic.co/logstash/) - Data processing
- [Kibana](https://www.elastic.co/kibana/) - Visualization
- [Docker](https://www.docker.com/) - Containerization

**Made for security research and education**
