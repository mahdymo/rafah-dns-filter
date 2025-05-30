#!/bin/bash

# Ubuntu DNS Filter Setup Script
# This script sets up the DNS filtering application on Ubuntu/Debian systems

set -e

echo "=== Ubuntu DNS Filter Setup ==="
echo "Setting up DNS filtering application for Ubuntu..."

# Check if running as root for system configuration
if [[ $EUID -eq 0 ]]; then
   echo "Note: Running as root. This allows system DNS configuration."
   ROOT_ACCESS=true
else
   echo "Note: Not running as root. Some system features may be limited."
   ROOT_ACCESS=false
fi

# Update package list
echo "Updating package list..."
if command -v apt-get &> /dev/null; then
    if [[ "$ROOT_ACCESS" == true ]]; then
        apt-get update
        apt-get install -y python3 python3-pip python3-venv
    else
        echo "Please install python3 and pip3 if not already installed:"
        echo "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user dnslib flask requests

# Create systemd service file (if root)
if [[ "$ROOT_ACCESS" == true ]]; then
    echo "Creating systemd service..."
    cat > /etc/systemd/system/dns-filter.service << EOF
[Unit]
Description=DNS Filter Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    systemctl daemon-reload
    systemctl enable dns-filter.service
    
    echo "Service created. You can start it with: sudo systemctl start dns-filter"
fi

# Configure UFW firewall (if installed and root)
if command -v ufw &> /dev/null && [[ "$ROOT_ACCESS" == true ]]; then
    echo "Configuring firewall..."
    ufw allow 5000/tcp  # Web dashboard
    ufw allow 5353/udp  # DNS server (non-privileged port)
    echo "Firewall configured for ports 5000 (web) and 5353 (DNS)"
fi

# Create startup script for non-root users
cat > start_dns_filter.sh << 'EOF'
#!/bin/bash

# DNS Filter Startup Script for Ubuntu
echo "Starting DNS Filter Application..."

# Check if Python dependencies are installed
python3 -c "import dnslib, flask, requests" 2>/dev/null || {
    echo "Installing Python dependencies..."
    pip3 install --user dnslib flask requests
}

# Start the application
echo "Starting DNS server on port 5353 and web dashboard on port 5000..."
echo "Access the dashboard at: http://localhost:5000"
echo "Configure your system to use 127.0.0.1:5353 as DNS server"
echo ""
echo "Press Ctrl+C to stop..."

python3 main.py
EOF

chmod +x start_dns_filter.sh

# Create DNS configuration helper script
cat > configure_dns.sh << 'EOF'
#!/bin/bash

# DNS Configuration Helper for Ubuntu

echo "=== DNS Configuration Helper ==="
echo ""
echo "To use this DNS filter, you have several options:"
echo ""

if [[ $EUID -eq 0 ]]; then
    echo "1. Configure system-wide DNS (requires root):"
    echo "   This will modify /etc/systemd/resolved.conf"
    read -p "Configure system DNS now? (y/n): " configure_dns
    
    if [[ $configure_dns == "y" ]]; then
        # Backup original configuration
        cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.backup
        
        # Configure resolved to use our DNS filter
        cat >> /etc/systemd/resolved.conf << EOL

# DNS Filter Configuration
DNS=127.0.0.1:5353
FallbackDNS=8.8.8.8 1.1.1.1
DNSStubListener=no
EOL
        
        systemctl restart systemd-resolved
        echo "System DNS configured to use DNS filter"
        echo "Backup saved to /etc/systemd/resolved.conf.backup"
    fi
else
    echo "1. Manual network configuration:"
    echo "   Go to Network Settings > Wired/Wireless > IPv4 Settings"
    echo "   Set DNS servers to: 127.0.0.1:5353"
    echo ""
fi

echo "2. Test DNS filtering with dig command:"
echo "   dig @127.0.0.1 -p 5353 google.com"
echo "   dig @127.0.0.1 -p 5353 facebook.com  # Should be blocked"
echo ""

echo "3. Browser testing:"
echo "   Open http://localhost:5000 for the web dashboard"
echo ""

echo "4. Command line testing:"
echo "   nslookup google.com 127.0.0.1"
echo ""
EOF

chmod +x configure_dns.sh

# Create uninstall script
cat > uninstall.sh << 'EOF'
#!/bin/bash

echo "=== DNS Filter Uninstall ==="

# Stop and disable service (if root)
if [[ $EUID -eq 0 ]]; then
    if systemctl is-active --quiet dns-filter; then
        systemctl stop dns-filter
    fi
    
    if systemctl is-enabled --quiet dns-filter; then
        systemctl disable dns-filter
    fi
    
    if [ -f /etc/systemd/system/dns-filter.service ]; then
        rm /etc/systemd/system/dns-filter.service
        systemctl daemon-reload
    fi
    
    # Restore DNS configuration
    if [ -f /etc/systemd/resolved.conf.backup ]; then
        read -p "Restore original DNS configuration? (y/n): " restore_dns
        if [[ $restore_dns == "y" ]]; then
            mv /etc/systemd/resolved.conf.backup /etc/systemd/resolved.conf
            systemctl restart systemd-resolved
            echo "DNS configuration restored"
        fi
    fi
fi

echo "DNS Filter service uninstalled"
echo "Application files remain in current directory"
EOF

chmod +x uninstall.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Ubuntu DNS Filter has been configured with the following:"
echo "• DNS server will run on port 5353 (non-privileged)"
echo "• Web dashboard will run on port 5000"
echo "• Firewall configured (if UFW is installed)"
echo ""
echo "Next steps:"
echo "1. Start the application: ./start_dns_filter.sh"
echo "2. Configure DNS: ./configure_dns.sh"
echo "3. Access dashboard: http://localhost:5000"
echo ""
echo "Files created:"
echo "• start_dns_filter.sh - Start the application"
echo "• configure_dns.sh - Configure system DNS"
echo "• uninstall.sh - Remove service and restore DNS"
if [[ "$ROOT_ACCESS" == true ]]; then
echo "• /etc/systemd/system/dns-filter.service - System service"
fi
echo ""
echo "For testing without system changes:"
echo "dig @127.0.0.1 -p 5353 google.com"