<section class="overview-section">
  <h2><strong>Overview of HoneyMesh</strong></h2>

  <p>
    HoneyMesh is inspired by <strong>T-Pot</strong> and designed for 
    <strong>security professionals</strong>, <strong>researchers</strong>, 
    and <strong>educational institutions</strong>.
  </p>

  <p>
    It provides a simplified, production-ready platform to deploy honeypots 
    while integrating powerful logging and analysis tools.
  </p>
</section>

<section class="about-section">
  <h2><strong>About HoneyMesh</strong></h2>

  <p>
    HoneyMesh provides an interactive <strong>CLI interface</strong> for deploying
    production-ready honeypots with integrated logging and analysis.
  </p>

  <p>
    The platform focuses on <strong>usability improvements</strong> and
    <strong>industry-specific customization</strong> while leveraging proven
    <strong>open-source honeypot technologies</strong>.
  </p>
</section>
section class="architecture-section">
  <h2><strong>Architecture / Design Overview</strong></h2>

  <div class="architecture-diagram">
    <img src="img/diagram-export-10-7-2025-8_39_23-PM.png" alt="HoneyMesh Architecture Diagram" />
    <p class="diagram-caption">Figure: HoneyMesh System Architecture and Data Flow</p>
  </div>

  <h3>Data Flow:</h3>
  <ol class="architecture-list">
    <li>Attacker connects to honeypot</li>
    <li>Cowrie logs interaction as JSON</li>
    <li>Filebeat ships logs to Logstash</li>
    <li>Logstash enriches with GeoIP data</li>
    <li>Elasticsearch stores and indexes</li>
    <li>Kibana visualizes attacks</li>
  </ol>

  <h3>Tech Stack:</h3>
  <ul class="architecture-list">
    <li><strong>Docker & Docker Compose</strong> for orchestration</li>
    <li><strong>Cowrie</strong> for SSH/Telnet honeypot</li>
    <li><strong>ELK Stack</strong> (Elasticsearch, Logstash, Kibana) for logging and analysis</li>
    <li><strong>Python CLI</strong> for management</li>
  </ul>
</section>


