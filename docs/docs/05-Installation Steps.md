<section className="installation-section" id="installation-steps">
  <h2><strong>Installation Steps</strong></h2>

  <h3>1. Clone the HoneyMesh Repository</h3>
  <pre><code className="language-bash">
git clone https://github.com/rayzax/HoneyMesh.git
  </code></pre>


  <h3>2. Run the Dependency Checker</h3>
  <pre><code className="language-bash">
cd HoneyMesh/
sudo chmod +x installDependencies.sh
sudo ./installDependencies.sh
  </code></pre>

  <h3>3. Follow the Next Steps</h3>
  <p>
    After dependencies are installed, proceed with deployment using the main HoneyMesh script.
    You will need to reboot or log out in order for the changes to take effect
  </p>

  <h3>4. Run HoneyMesh</h3>
  <pre><code className="language-bash">
sudo python3 honeymesh.py
  </code></pre>

  <h3>5. Recommended Mode</h3>
  <p>
    It is recommended to run HoneyMesh in <strong>medium interaction</strong> mode to use custom industry specific templates/honeypots. The low interaction mode just spins up a default cowrie SSH honeypot which still has a fake linux file system but is a lot less convincing and pretty shallow in terms of filesystem.
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
