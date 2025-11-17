# HoneyMesh

A self-hosted honeypot deployment platform that simplifies honeypot creation and management for security professionals, researchers, and educational institutions.

## Getting Started with HoneyMesh

### Step 1: Clone the Repository

```bash
git clone https://github.com/rayzax/HoneyMesh
```

### Step 2: Change Directory to HoneyMesh

```bash
cd HoneyMesh
```

### Step 3: Make the Installation Script Executable

```bash
sudo chmod +x installDependencies.sh
```

### Step 4: Run the Installation Script

```bash
sudo ./installDependencies.sh
```

### Step 5: Log Out and Back In

After installation completes, log out of your system and log back in to apply Docker group permissions.

### Step 6: Run HoneyMesh

```bash
python3 honeymesh.py
```

### Step 7: Follow the CLI

Follow the interactive command-line interface to configure and spin up your honeypot deployment.

---

## Important Notes

### Production Deployments

For production deployments, follow the production deployment guide in the documentation.

### Industry Templates

HoneyMesh comes preloaded with 3 industry template customizations:

- **Epic Healthcare Server** - Simulates an Epic electronic health record (EHR) production environment
- **Financial Banking Server** - Mimics a Jack Henry Symitar core banking platform
- **Corporate IT Server** - Generic enterprise IT environment

To learn more about templates and template structure, refer to the templates documentation.

---

## Disclaimer

HoneyMesh is intended for educational, research, and security testing purposes only. Deploying honeypots involves exposing services to potential attackers. Users must ensure they have explicit permission to run HoneyMesh on any network or system.

The creators and contributors of HoneyMesh are not responsible for any misuse, damage, or legal consequences arising from the deployment or use of this software. Always follow applicable laws, regulations, and organizational policies when using HoneyMesh.

Users should deploy HoneyMesh in isolated, controlled environments, and never expose it to production or sensitive networks without proper safeguards.
