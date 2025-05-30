# Installation Guide

Complete installation instructions for DNS Filter on different platforms.

## Prerequisites

- Python 3.8 or higher
- Internet connection for downloading dependencies and blocklists
- Administrator/root privileges for system-level DNS configuration (optional)

## Platform-Specific Installation

### Windows Installation

#### Method 1: Standard Installation

1. **Download Python**
   - Install Python 3.8+ from [python.org](https://python.org)
   - Ensure "Add Python to PATH" is checked during installation

2. **Download DNS Filter**
   ```cmd
   git clone https://github.com/yourusername/dns-filter.git
   cd dns-filter
   ```

3. **Install Dependencies**
   ```cmd
   pip install dnslib flask requests
   ```

4. **Run Application**
   ```cmd
   # Run as Administrator for port 53 access
   python main.py
   ```

### Ubuntu/Linux Installation

#### Method 1: Automated Setup

1. **Download and Setup**
   ```bash
   git clone https://github.com/yourusername/dns-filter.git
   cd dns-filter
   chmod +x setup_ubuntu.sh
   ./setup_ubuntu.sh
   ```

2. **Configure DNS**
   ```bash
   ./configure_dns.sh
   ```

## Verification

### Test DNS Resolution

```bash
# Test allowed domain
dig @127.0.0.1 -p 5353 google.com

# Test blocked domain
dig @127.0.0.1 -p 5353 facebook.com
```

### Access Web Dashboard

Open your browser and navigate to `http://localhost:5000`

## Troubleshooting

### Permission Issues

**Linux:**
```bash
# Allow non-root binding to privileged ports
sudo setcap CAP_NET_BIND_SERVICE=+eip $(which python3)
```

### Port Conflicts

**Check port usage:**
```bash
# Linux/macOS
netstat -tulpn | grep :5353
```