<section class="installation-section" id="installation-steps">
  <h2><strong>Installation Steps</strong></h2>

  <h3>Prerequisites:</h3>
  <ul class="installation-list">
    <li>Ubuntu 20.04+ (or compatible Linux)</li>
    <li>Docker 20.10+</li>
    <li>Docker Compose 1.29+</li>
    <li>User in the <code>docker</code> user group</li>
    <li>Python 3.8+</li>
    <li>4GB RAM minimum (8GB recommended)</li>
    <li>25GB free disk space</li>
  </ul>

  <h3>Quick Install:</h3>
  <pre><code class="language-bash">
# Clone repository
git clone https://github.com/yourusername/honeymesh.git
cd honeymesh

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Run HoneyMesh
python3 honeymesh.py
  </code></pre>

  <p>Then follow the interactive wizard to configure and deploy your honeypot.</p>
</section>

<section class="configuration-section">
  <h2><strong>Configuration & Logging</strong></h2>

  <h3>Port Configuration:</h3>
  <ul class="config-list">
    <li><strong>SSH Honeypot:</strong> 2222 (configurable during setup)</li>
    <li><strong>Telnet Honeypot:</strong> 2223 (optional)</li>
    <li><strong>Kibana Dashboard:</strong> 5601 (configurable)</li>
    <li><strong>Elasticsearch:</strong> 9200</li>
  </ul>

  <h3>Files:</h3>
  <ul class="config-list">
    <li><code>honeypot-data/config/cowrie.cfg</code> - Cowrie configuration</li>
    <li><code>honeypot-data/docker-compose.yml</code> - Service definitions</li>
    <li><code>honeypot-data/elk-config/</code> - ELK stack configurations</li>
  </ul>

  <h3>Customization:</h3>
  <ul class="config-list">
    <li>Modify hostname and SSH banner in <code>cowrie.cfg</code></li>
    <li>Choose from a library of custom honeypots that mimic vulnerable industry-specific servers</li>
    <li>Build your own custom honeypots and filesystems</li>
    <li>Configure log retention and storage paths</li>
  </ul>

  <h3>Logging and Analysis:</h3>
  <p>All events are logged as JSON with:</p>
  <ul class="config-list">
    <li>Timestamp</li>
    <li>Source IP with GeoIP data</li>
    <li>Event type (login, command, file transfer)</li>
    <li>Session details</li>
    <li>Username/password attempts</li>
    <li>Commands executed</li>
  </ul>

  <p>Key Events:</p>
  <ul class="config-list">
    <li><code>cowrie.login.success/failed</code> - Authentication attempts</li>
    <li><code>cowrie.command.input</code> - Commands executed</li>
    <li><code>cowrie.session.file_download</code> - Downloaded files</li>
    <li><code>cowrie.session.connect/closed</code> - Connection events</li>
  </ul>

  <p>Analysis using Kibana:</p>
  <ul class="config-list">
    <li>Map attack origins geographically</li>
    <li>Identify common credentials used</li>
    <li>Track command execution patterns</li>
    <li>Monitor session durations</li>
    <li>Export data for further analysis</li>
  </ul>
</section>
<section className="usage-section">
  <h2><strong>Usage</strong></h2>

  <h3>Starting HoneyMesh:</h3>
  <pre>
    <code className="language-bash">
python3 honeymesh.py
    </code>
  </pre>

  <h3>Main Menu:</h3>
  <p>View the HoneyMesh main menu below:</p>
  <div style={{ textAlign: 'center', margin: '1rem 0' }}>
    <img 
      src="https://github.com/user-attachments/assets/cabe351a-6a05-46e7-9abd-29eaae6dc380" 
      alt="HoneyMesh Main Menu" 
      style={{ maxWidth: '100%', height: 'auto', borderRadius: '6px' }} 
    />
  </div>

  <h3>Management Console:</h3>
  <p>View the HoneyMesh management console below:</p>
  <div style={{ textAlign: 'center', margin: '1rem 0' }}>
    <img 
      src="https://github.com/user-attachments/assets/322c9ea4-9b8f-405e-938a-5fd0e52c4553" 
      alt="HoneyMesh Management Console" 
      style={{ maxWidth: '100%', height: 'auto', borderRadius: '6px' }} 
    />
  </div>

  <h3>Accessing Services:</h3>
  <pre>
    <code className="language-bash">
# SSH honeypot
ssh user@localhost -p 2222

# Kibana dashboard
http://localhost:5601

# View logs
tail -f ./honeypot-data/logs/cowrie.json
    </code>
  </pre>
</section>
<h3>1. Clone the HoneyMesh Repository</h3>
  <pre>
    <code className="language-bash">
git clone https://github.com/rayzax/HoneyMesh.git
    </code>
  </pre>

  <h3>2. Run the Dependency Checker</h3>
  <pre>
    <code className="language-bash">
cd HoneyMesh/
ls
sudo ./installDependencies.sh
    </code>
  </pre>

  <h3>3. Follow the Next Steps</h3>
  <p>After dependencies are installed, proceed with deployment using the main HoneyMesh script.</p>

  <h3>4. Run HoneyMesh</h3>
  <pre>
    <code className="language-bash">
python3 HoneyMesh.py
    </code>
  </pre>

  <h3>5. Recommended Mode</h3>
  <p>It is recommended to run HoneyMesh in <strong>medium interaction</strong> mode for balanced realism and safety.</p>

  <h3>6. Configure and Deploy</h3>
  <p>Follow the on-screen wizard to configure honeypots, define logging paths, and enable ELK integration.</p>

  <h3>7. Deployment Success</h3>
  <p>Once setup completes successfully, the honeypots will begin capturing activity.</p>

  <h3>8. SSH Test</h3>
  <pre>
    <code className="language-bash">
ssh user@localhost -p 2222
    </code>
  </pre>

  <p>If the connection succeeds, your HoneyMesh honeypot is live and ready for analysis.</p>




