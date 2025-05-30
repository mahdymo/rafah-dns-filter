# Changelog

All notable changes to the DNS Filter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Bandwidth monitoring and savings calculation
- Real-time bandwidth usage tracking
- Percentage savings display in dashboard
- Enhanced visual dashboard with gradient cards
- Cross-platform support (Windows and Ubuntu/Linux)
- Comprehensive GitHub repository structure
- Detailed documentation and setup guides

### Changed
- Updated database schema to include bandwidth tracking
- Enhanced DNS query logging with response time and byte savings
- Improved web dashboard with bandwidth statistics
- Modified configuration for cross-platform compatibility

### Fixed
- Template rendering issues with JSON filters
- Database initialization for existing installations

## [1.0.0] - 2025-05-30

### Added
- Initial release of DNS Filter application
- DNS query interception and filtering
- In-memory DNS response caching with TTL support
- Web dashboard with real-time statistics
- Blocklist management (local and remote)
- Query logging with SQLite database
- Interactive charts and graphs
- Domain blocking/unblocking functionality
- Configuration management via JSON
- Default blocklist with common ad and tracking domains

### Features
- **DNS Server**: Custom DNS resolver with filtering capabilities
- **Web Interface**: Modern, responsive dashboard
- **Caching System**: LRU cache with automatic cleanup
- **Statistics**: Real-time query monitoring and analytics
- **Blocklists**: Support for Pi-hole compatible lists
- **Cross-platform**: Windows and Linux support

### Technical Details
- Built with Python 3.8+
- Flask web framework for dashboard
- SQLite for query logging and configuration
- dnslib for DNS protocol handling
- Bootstrap for responsive UI
- Chart.js for data visualization

### Configuration
- Configurable DNS and web server ports
- Multiple upstream DNS server support
- Adjustable cache size and TTL
- Flexible blocklist management
- Query retention policies

### Security
- Input validation for all user inputs
- SQL injection protection
- XSS prevention in web interface
- Secure configuration file handling