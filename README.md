# Windows DNS Filter

A Windows-compatible DNS filtering application inspired by Pi-hole, providing DNS query interception, caching, and blocking capabilities with a modern web dashboard.

## Features

- **DNS Query Interception**: Intercepts and filters DNS queries on Windows systems
- **Advanced Caching**: In-memory DNS response caching with TTL support
- **Web Dashboard**: Modern, responsive web interface for monitoring and management
- **Blocklist Management**: Support for local and remote blocklists with automatic updates
- **Query Logging**: Comprehensive logging of all DNS queries with statistics
- **Real-time Monitoring**: Live dashboard with charts and statistics
- **Domain Management**: Easy blocking/unblocking of individual domains
- **Windows Service Ready**: Can be configured to run as a Windows service

## System Requirements

- **Operating System**: Windows 10/11 or Windows Server 2016+
- **Python**: Python 3.8 or higher
- **Memory**: Minimum 512MB RAM (1GB recommended)
- **Storage**: 100MB free disk space
- **Network**: Administrator privileges required for DNS port binding (port 53)

## Installation

### Prerequisites

1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Run as Administrator** (required for DNS port binding)

### Quick Installation

1. **Clone or download** the application files to a directory (e.g., `C:\DNSFilter`)

2. **Install Python dependencies**:
   ```bash
   pip install dnslib flask requests
   ```

3. **Configure Windows DNS** (optional but recommended):
   - Open Network Adapter settings
   - Set primary DNS to `127.0.0.1` (localhost)
   - Set secondary DNS to `8.8.8.8` (Google DNS as fallback)

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the dashboard** at: `http://localhost:5000`

## Configuration

### Main Configuration File (`config.json`)

The application can be configured via the `config.json` file:

```json
{
  "dns_host": "127.0.0.1",
  "dns_port": 53,
  "web_host": "0.0.0.0",
  "web_port": 5000,
  "upstream_dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "cache_size": 10000,
  "cache_ttl": 300,
  "log_queries": true,
  "enable_blocking": true,
  "cleanup_days": 30
}
