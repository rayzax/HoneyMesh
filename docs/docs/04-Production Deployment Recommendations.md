# Production Deployment Guide

## Overview

Deploy HoneyMesh on an isolated VPS (virtual private server) on its own virtual network.

## Step 1: Provision a Cloud VM

Spin up a cloud virtual machine with the following recommended specifications for production deployments:

- **RAM**: 8GB minimum
- **CPU**: 4 cores minimum
- **Storage**: 100GB or more

## Step 2: Secure SSH Access

### Change OpenSSH Port

SSH into your cloud VM and configure OpenSSH to run on port 2222 instead of the default port 22.

```bash
sudo nano /etc/ssh/sshd_config
```

Locate the line with `#Port 22`, uncomment it, and change to:

```
Port 2222
```

Save the file and restart the SSH service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket
```

## Step 3: Configure Cloud Firewall

Configure a cloud firewall for your VM with the following rules:

**Important**: Your static IP must be a public static IP address. We recommend using either:
- Another cloud self-hosted VPN
- Your home public IP address through your ISP

### Firewall Rules

1. **Allow inbound honeypot SSH (port 22)**: All sources
2. **Allow inbound admin SSH (port 2222)**: Your static IP only - this is your ssh port for managing the actual VPS
3. **Allow inbound Kibana (port 5601)**: Your static IP only
4. **Allow inbound Elasticsearch (port 9200)**: Your static IP only
5. **Allow inbound Logstash (port 9600)**: Your static IP only

### Example Rule Configuration

```
Rule 1: SSH (Honeypot) Access
- Port: 22
- Protocol: TCP
- Source: 0.0.0.0/0 (All)

Rule 2: SSH Admin (your access)
- Port: 2222
- Protocol: TCP
- Source: your.static.ip.address/32

Rule 3: Kibana Dashboard
- Port: 5601
- Protocol: TCP
- Source: your.static.ip.address/32

Rule 4: Elasticsearch
- Port: 9200
- Protocol: TCP
- Source: your.static.ip.address/32

Rule 5: Logstash
- Port: 9600
- Protocol: TCP
- Source: your.static.ip.address/32
```

## Next Steps

After completing the firewall configuration, proceed with the HoneyMesh installation
