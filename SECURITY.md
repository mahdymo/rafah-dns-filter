# Security Policy

## Supported Versions

We actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email security concerns to: security@dnsfilter.local
3. Include detailed information about the vulnerability
4. Allow reasonable time for response before public disclosure

## Security Considerations

### Network Security
- DNS server binds to configurable interfaces
- Web dashboard can be restricted to localhost
- No authentication currently implemented

### Input Validation
- All user inputs are validated
- SQL injection protection in place
- XSS prevention in web interface

### Data Protection
- Query logs stored locally in SQLite
- No external data transmission unless configured
- Configuration files should be secured

### Recommended Security Practices
- Run with minimal required privileges
- Use firewall rules to restrict access
- Regularly update blocklists from trusted sources
- Monitor query logs for suspicious activity

## Known Security Limitations

1. **No Authentication**: Web interface is publicly accessible
2. **HTTP Only**: Web dashboard uses HTTP, not HTTPS
3. **Local Storage**: All data stored in local files

## Future Security Enhancements

- User authentication for web interface
- HTTPS support for web dashboard
- API rate limiting
- Encrypted configuration storage