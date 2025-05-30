# Contributing to DNS Filter

We welcome contributions to the DNS Filter project! This document provides guidelines for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat everyone with respect and create a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When filing a bug report, include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **System information** (OS, Python version, etc.)
- **Log output** if applicable

### Suggesting Features

Feature requests are welcome! Please:

- Check existing feature requests first
- Provide a clear description of the feature
- Explain the use case and benefits
- Consider implementation complexity

### Pull Requests

1. **Fork the repository** and create your feature branch
2. **Follow coding standards** (see below)
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass**
6. **Submit a pull request**

## Development Setup

```bash
git clone https://github.com/yourusername/dns-filter.git
cd dns-filter
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install dnslib flask requests
```

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all classes and functions
- Keep functions focused and small

### Example Function Documentation

```python
def resolve_dns_query(domain, query_type):
    """
    Resolve a DNS query for the specified domain.
    
    Args:
        domain (str): The domain name to resolve
        query_type (str): The DNS query type (A, AAAA, etc.)
    
    Returns:
        DNSRecord: The DNS response record
    
    Raises:
        DNSException: If the query fails
    """
    pass
```

### Database Changes

- Always include database migration scripts
- Test with existing data
- Document schema changes
- Ensure backward compatibility when possible

### Frontend Changes

- Follow existing HTML/CSS structure
- Test responsive design on multiple screen sizes
- Ensure accessibility standards
- Maintain consistent styling

## Testing

### Running Tests

```bash
python -m pytest tests/
```

### Test Coverage

- Aim for at least 80% test coverage
- Include both unit and integration tests
- Test error conditions and edge cases

### Manual Testing

Before submitting:

1. Test basic DNS resolution
2. Verify web dashboard functionality
3. Test blocklist management
4. Check bandwidth monitoring accuracy

## Documentation

### Code Documentation

- Document all public functions and classes
- Include usage examples
- Explain complex algorithms
- Update API documentation for changes

### User Documentation

- Update README.md for new features
- Add configuration examples
- Include troubleshooting steps
- Provide platform-specific instructions

## Commit Messages

Use clear, descriptive commit messages:

```
Add bandwidth monitoring for cached queries

- Track bytes saved from DNS cache hits
- Display cache efficiency metrics in dashboard
- Update database schema for bandwidth tracking
```

## Branching Strategy

- `main` - Stable release branch
- `develop` - Development integration branch
- `feature/feature-name` - Feature development
- `hotfix/issue-description` - Critical bug fixes

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Build and test packages

## Platform-Specific Considerations

### Windows Development

- Test with administrator privileges
- Verify Windows Service functionality
- Check firewall integration
- Test installer packages

### Linux Development

- Test with non-privileged ports
- Verify systemd integration
- Check UFW firewall configuration
- Test on multiple distributions

## Performance Guidelines

- Profile code for performance bottlenecks
- Minimize memory usage
- Optimize database queries
- Cache frequently accessed data

## Security Considerations

- Validate all user inputs
- Sanitize database queries
- Secure configuration files
- Follow security best practices

## Getting Help

- Create an issue for questions
- Join our discussions
- Check the wiki for detailed guides
- Contact maintainers for security issues

## Recognition

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to DNS Filter!