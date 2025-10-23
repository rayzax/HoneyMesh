<details>
<summary><strong>FAQs</strong></summary>

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
