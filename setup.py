#!/usr/bin/env python3
"""
DNS Filter Setup Script
Package configuration for distribution
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the dependencies file
with open("dependencies.txt", "r", encoding="utf-8") as fh:
    dependencies = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dns-filter",
    version="1.0.0",
    author="DNS Filter Contributors",
    author_email="contributors@dnsfilter.local",
    description="A cross-platform DNS filtering application with bandwidth monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dns-filter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dnslib>=0.9.26",
        "Flask>=3.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "monitoring": [
            "psutil>=5.9.0",
        ],
        "security": [
            "cryptography>=41.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
            "blocklists/*.txt",
            "config.json",
            "setup_ubuntu.sh",
        ],
    },
    entry_points={
        "console_scripts": [
            "dns-filter=main:main",
            "dns-filter-setup=setup_ubuntu:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dns-filter/issues",
        "Documentation": "https://github.com/yourusername/dns-filter/wiki",
        "Source": "https://github.com/yourusername/dns-filter",
        "Funding": "https://github.com/sponsors/yourusername",
    },
    keywords=[
        "dns", "filter", "pihole", "adblock", "bandwidth", "monitoring",
        "caching", "security", "privacy", "network", "administration"
    ],
)