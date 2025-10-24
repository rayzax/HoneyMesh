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
