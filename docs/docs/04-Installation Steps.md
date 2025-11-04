<section className="installation-section" id="installation-steps">
  <h2><strong>Installation Steps</strong></h2>

  <h3>1. Clone the HoneyMesh Repository</h3>
  <pre><code className="language-bash">
git clone https://github.com/rayzax/HoneyMesh.git
  </code></pre>

  <div style={{ textAlign: 'center', margin: '1rem 0' }}>
    <img
      src="/img/Clonerepo.jpg.png"
      alt="Cloning the HoneyMesh repository"
      style={{ maxWidth: '100%', borderRadius: '6px' }}
    />
  </div>

  <h3>2. Run the Dependency Checker</h3>
  <pre><code className="language-bash">
cd HoneyMesh/
ls
sudo ./installDependencies.sh
  </code></pre>

  <h3>3. Follow the Next Steps</h3>
  <p>
    After dependencies are installed, proceed with deployment using the main HoneyMesh script.
  </p>

  <h3>4. Run HoneyMesh</h3>
  <pre><code className="language-bash">
sudo python3 HoneyMesh.py
  </code></pre>

  <h3>5. Recommended Mode</h3>
  <p>
    It is recommended to run HoneyMesh in <strong>medium interaction</strong> mode for balanced realism and safety.
  </p>

  <h3>6. Configure and Deploy</h3>
  <p>
    Follow the on-screen wizard to configure honeypots, define logging paths, and enable ELK integration.
  </p>

  <h3>7. Deployment Success</h3>
  <p>
    Once setup completes successfully, the honeypots will begin capturing activity.
  </p>

  <h3>8. SSH Test</h3>
  <pre><code className="language-bash">
ssh user@localhost -p 2222
  </code></pre>

  <p>
    If the connection succeeds, your HoneyMesh honeypot is live and ready for analysis.
  </p>
</section>

<section className="usage-section">
  <h2><strong>Usage</strong></h2>

  <h3>Starting HoneyMesh:</h3>
  <pre><code className="language-bash">
sudo python3 honeymesh.py
  </code></pre>

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
  <pre><code className="language-bash">
# SSH honeypot
ssh user@localhost -p 2222

# Kibana dashboard
http://localhost:5601

# View logs
tail -f ./honeypot-data/logs/cowrie.json
  </code></pre>
</section>
