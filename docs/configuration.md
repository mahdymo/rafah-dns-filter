# Configuration Guide

Comprehensive configuration options for DNS Filter.

## Configuration File

The main configuration is stored in `config.json`:

```json
{
  "dns_host": "0.0.0.0",
  "dns_port": 5353,
  "web_host": "0.0.0.0",
  "web_port": 5000,
  "upstream_dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "cache_size": 10000,
  "cache_ttl": 300,
  "log_queries": true,
  "enable_blocking": true,
  "cleanup_days": 30
}
```

## Configuration Options

### DNS Server Settings

- **dns_host**: IP address to bind DNS server (0.0.0.0 for all interfaces)
- **dns_port**: Port for DNS server (53 for standard, 5353 for non-privileged)
- **upstream_dns**: List of upstream DNS servers for forwarding queries

### Web Interface Settings

- **web_host**: IP address to bind web server
- **web_port**: Port for web dashboard

### Caching Configuration

- **cache_size**: Maximum number of cached DNS responses
- **cache_ttl**: Time-to-live for cached responses (seconds)

### Logging and Maintenance

- **log_queries**: Enable/disable query logging
- **enable_blocking**: Enable/disable domain blocking
- **cleanup_days**: Days to retain query logs

## Blocklist Configuration

### Local Blocklists

Place blocklist files in the `blocklists/` directory:

```
blocklists/
├── default.txt        # Default blocked domains
├── custom.txt         # Custom additions
├── ads.txt           # Ad-specific blocks
└── malware.txt       # Malware domains
```

### Remote Blocklists

Popular blocklist sources:

```python
# Steven Black's consolidated hosts file
"https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"

# AdGuard DNS Filter
"https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"

# Pi-hole default lists
"https://raw.githubusercontent.com/pi-hole/pi-hole/master/adlists.default"
```

### Blocklist Formats

Supported formats:
- Hosts file format: `0.0.0.0 example.com`
- AdBlock format: `||example.com^`
- Plain domain list: `example.com`

## Network Configuration

### System DNS Configuration

#### Windows
1. Open Network and Sharing Center
2. Change adapter settings
3. Right-click connection → Properties
4. Select Internet Protocol Version 4
5. Set DNS servers to `127.0.0.1` and `8.8.8.8`

#### Ubuntu/Linux
```bash
# Edit systemd-resolved configuration
sudo nano /etc/systemd/resolved.conf

[Resolve]
DNS=127.0.0.1:5353
FallbackDNS=8.8.8.8 1.1.1.1
DNSStubListener=no

sudo systemctl restart systemd-resolved
```

#### Router Configuration
Configure your router's DNS settings to use the DNS Filter for all network devices.

## Performance Tuning

### Memory Optimization
```json
{
  "cache_size": 5000,
  "cleanup_days": 7
}
```

### Network Optimization
```json
{
  "cache_ttl": 600,
  "upstream_dns": ["1.1.1.1", "8.8.8.8"]
}
```

## Security Configuration

### Access Control
- Bind web interface to localhost only: `"web_host": "127.0.0.1"`
- Use firewall rules to restrict access
- Consider reverse proxy with authentication

### Blocklist Security
- Verify blocklist sources
- Use HTTPS URLs when possible
- Regular updates and monitoring

## Environment Variables

Override configuration with environment variables:

```bash
export DNS_FILTER_PORT=5353
export DNS_FILTER_WEB_PORT=5000
export DNS_FILTER_UPSTREAM_DNS="1.1.1.1,8.8.8.8"
```

## Advanced Configuration

### Custom Upstream Servers
```json
{
  "upstream_dns": [
    "1.1.1.1",        # Cloudflare
    "8.8.8.8",        # Google
    "9.9.9.9",        # Quad9
    "208.67.222.222"  # OpenDNS
  ]
}
```

### Bandwidth Monitoring
Bandwidth calculation settings are built-in:
- DNS response size: 100 bytes average
- Blocked request savings: 1KB average
- Cached response savings: 50 bytes average

## Platform-Specific Configuration

### Windows Service
```json
{
  "dns_host": "127.0.0.1",
  "dns_port": 53,
  "log_queries": true
}
```

### Linux Systemd
```json
{
  "dns_host": "0.0.0.0",
  "dns_port": 5353,
  "web_host": "0.0.0.0"
}
```

## Troubleshooting Configuration

### Common Issues

**DNS queries not being filtered:**
- Check system DNS configuration
- Verify application is running
- Test with dig command

**Web dashboard not accessible:**
- Check firewall settings
- Verify web_host and web_port settings
- Check application logs

**High memory usage:**
- Reduce cache_size
- Decrease cleanup_days
- Monitor query volume

### Validation

Test configuration changes:
```bash
# Test DNS resolution
dig @127.0.0.1 -p 5353 example.com

# Check web dashboard
curl http://localhost:5000/api/stats

# Verify configuration
python -c "import json; print(json.load(open('config.json')))"
```