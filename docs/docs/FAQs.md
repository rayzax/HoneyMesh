# 🛡️ HoneyMesh FAQs

<div class="faq-container">

---

## General Use

<div class="faq-section">

### ❓ What is HoneyMesh?
<p class="faq-answer">
HoneyMesh is a self-hosted honeypot deployment platform inspired by <strong>T-Pot</strong>.  
It provides an interactive Python CLI to deploy, manage, and monitor honeypots with integrated <strong>ELK (Elasticsearch, Logstash, Kibana)</strong> analysis tools.
</p>

### 👥 Who is HoneyMesh designed for?
<p class="faq-answer">
It’s intended for <strong>security researchers, network administrators, and educators</strong> who want to safely observe and analyze attack behaviors in a controlled environment.
</p>

### ⚙️ What makes HoneyMesh different from other honeypot systems?
<p class="faq-answer">
Unlike most standalone honeypots, HoneyMesh includes an <strong>orchestration CLI</strong>, <strong>Docker-based deployment</strong>, integrated <strong>ELK visualization</strong>, and a <strong>modular design</strong> for custom honeypot creation.
</p>

### 📊 What kind of data does HoneyMesh collect?
<p class="faq-answer">
HoneyMesh logs <strong>attacker IPs, commands, login attempts, file downloads,</strong> and <strong>session data</strong> in JSON format, enriched with <strong>GeoIP</strong> information.
</p>

</div>

---

## Installation & Platform Support

<div class="faq-section">

### 💻 Can I deploy HoneyMesh on Windows or Mac?
<p class="faq-answer">
HoneyMesh is designed for <strong>Linux</strong> environments.  
Windows or Mac users can run it using a <strong>Linux virtual machine</strong> or <strong>WSL2 (Windows Subsystem for Linux)</strong>.
</p>

</div>

---

## Configuration & Customization

<div class="faq-section">

### 🧩 Can I customize honeypots for specific industries?
<p class="faq-answer">
Yes. HoneyMesh supports building <strong>custom honeypots and filesystems</strong> that mimic vulnerable servers used in specific industries.
</p>

</div>

---

## Security & Data Handling

<div class="faq-section">

### 🔐 Is it safe to run HoneyMesh on my network?
<p class="faq-answer">
Only deploy on networks you <strong>own or have explicit permission</strong> to test.  
Always <strong>isolate honeypots</strong> using proper segmentation and security controls.
</p>

### 🌍 Can I share my captured attack data publicly?
<p class="faq-answer">
Only if you <strong>anonymize sensitive information</strong> and comply with all applicable <strong>data protection laws</strong>, such as <strong>GDPR</strong> or <strong>CCPA</strong>.
</p>

### 🧱 What happens if attackers compromise the honeypot?
<p class="faq-answer">
Attackers are <strong>isolated inside a containerized environment</strong>.  
However, always assume some risk — use firewalls, limit exposure, and regularly monitor activity.
</p>

</div>

---

## Future Development

<div class="faq-section">

### 🚀 What if I need more high-interaction honeypots?
<p class="faq-answer">
Future versions of HoneyMesh will include <strong>dedicated virtual machines for each attack session</strong> and support for <strong>clustered deployments</strong>.
</p>

### 🔄 Will HoneyMesh support high-interaction honeypots?
<p class="faq-answer">
Yes. The roadmap includes <strong>high-interaction honeypots</strong> using dedicated VMs and container-based clustering for advanced research use.
</p>

</div>

</div>
