<img width="85" height="84" alt="image" src="https://github.com/user-attachments/assets/68ead79b-5888-4a03-a5da-18c2e8647711" />

# HoneyMesh

---

## Overview of HoneyMesh

HoneyMesh is inspired by **T-Pot** and designed for **security professionals, researchers, and educational institutions**.  
It provides a simplified, production-ready platform to deploy honeypots while integrating powerful logging and analysis tools.

---

###  Key Functions

- **Captures attack activity** on exposed services like SSH and Telnet.  
- **Stores detailed logs** in JSON format, enriched with GeoIP and session metadata.  
- **Visualizes attacks and trends** using the integrated **Kibana dashboard**.  
- **Enables creation of custom honeypots** tailored to specific industries or environments.

---

###  Use Cases

-  **Cybersecurity research and experimentation** — safely analyze real-world attack behavior.  
-  **Security training for students and professionals** — simulate live attacks in controlled lab environments.  
-  **Threat intelligence and incident analysis** — identify attacker methods, tools, and evolving TTPs (Tactics, Techniques, and Procedures).

---



## About HoneyMesh

HoneyMesh provides an interactive CLI interface for deploying production-ready honeypots with integrated logging and analysis. The platform focuses on usability improvements and industry-specific customization while leveraging proven open-source honeypot technologies.

## Features
**HoneyMesh Features**
HoneyMesh is a self-hosted honeypot deployment platform that simplifies honeypot creation and management. Its main features include:

**Full-stack Python CL**I: Orchestrate, customize, and deploy honeypots with an interactive command-line interface.

**Custom Cowrie honeypot builder**: Easily configure SSH and Telnet honeypots with custom settings.

**Honeypot Management Console:** Monitor and manage multiple honeypots from a single interface.

**ELK Stack Integration:** Centralized logging and analysis with Elasticsearch, Logstash, and Kibana.

**Industry-specific customization:** Create honeypots that mimic vulnerable servers for specific industries.

**Logging and analysis:** Collect detailed JSON logs including attack metadata, session details, and executed commands.

**Interactive setup wizard:** Guided installation and configuration for quick deployment.

**Future roadmap:** High-interaction honeypots, dedicated VMs per session, clustered deployments, and advanced centralized management.

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


## FAQs

---

###  General Use

<details>
<summary><strong>What is HoneyMesh?</strong></summary>

HoneyMesh is a self-hosted honeypot deployment platform inspired by T-Pot. It provides an interactive Python CLI to deploy, manage, and monitor honeypots with integrated ELK (Elasticsearch, Logstash, Kibana) analysis tools.
</details>

<details>
<summary><strong>Who is HoneyMesh designed for?</strong></summary>

It’s intended for security researchers, network administrators, and educators who want to safely observe and analyze attack behaviors in a controlled environment.
</details>

<details>
<summary><strong>What makes HoneyMesh different from other honeypot systems?</strong></summary>

Unlike most standalone honeypots, HoneyMesh includes an orchestration CLI, Docker-based deployment, integrated ELK visualization, and a modular design for custom honeypot creation.
</details>

<details>
<summary><strong>What kind of data does HoneyMesh collect?</strong></summary>

HoneyMesh logs attacker IPs, commands, login attempts, file downloads, and session data in JSON format, enriched with GeoIP information.
</details>

---

###  Installation & Platform Support

<details>
<summary><strong>Can I deploy HoneyMesh on Windows or Mac?</strong></summary>

HoneyMesh is designed for Linux environments. Windows or Mac users can run it using a Linux virtual machine or WSL2 (Windows Subsystem for Linux).
</details>

---

###  Configuration & Customization

<details>
<summary><strong>Can I customize honeypots for specific industries?</strong></summary>

Yes. HoneyMesh supports building custom honeypots and filesystems that mimic vulnerable servers used in specific industries.
</details>

---

###  Security & Data Handling

<details>
<summary><strong>Is it safe to run HoneyMesh on my network?</strong></summary>

Only deploy on networks you own or have explicit permission to test. Always isolate honeypots using proper segmentation and security controls.
</details>

<details>
<summary><strong>Can I share my captured attack data publicly?</strong></summary>

Only if you anonymize sensitive information and comply with all applicable data protection laws, such as GDPR or CCPA.
</details>

<details>
<summary><strong>What happens if attackers compromise the honeypot?</strong></summary>

Attackers are isolated inside a containerized environment. However, always assume some risk — use firewalls, limit exposure, and regularly monitor activity.
</details>

---

### Future Development

<details>
<summary><strong>What if I need more high-interaction honeypots?</strong></summary>

Future versions of HoneyMesh will include dedicated virtual machines for each attack session and support for clustered deployments.
</details>

<details>
<summary><strong>Will HoneyMesh support high-interaction honeypots?</strong></summary>

Yes. The roadmap includes high-interaction honeypots using dedicated VMs and container-based clustering for advanced research use.
</details>

---

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
