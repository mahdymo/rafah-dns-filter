"""
Configuration Manager
Handles application configuration and settings
"""

import json
import os

class Config:
    """Configuration management for DNS filter application"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or use defaults"""
        defaults = {
            "dns_host": "127.0.0.1",
            "dns_port": 53,
            "web_host": "0.0.0.0",
            "web_port": 5000,
            "upstream_dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
            "cache_size": 10000,
            "cache_ttl": 300,
            "log_queries": True,
            "enable_blocking": True,
            "cleanup_days": 30
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    defaults.update(config_data)
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
        else:
            # Create default config file
            self.save_config(defaults)
        
        # Set attributes
        for key, value in defaults.items():
            setattr(self, key, value)
    
    def save_config(self, config_data=None):
        """Save configuration to file"""
        if config_data is None:
            config_data = {
                "dns_host": self.dns_host,
                "dns_port": self.dns_port,
                "web_host": self.web_host,
                "web_port": self.web_port,
                "upstream_dns": self.upstream_dns,
                "cache_size": self.cache_size,
                "cache_ttl": self.cache_ttl,
                "log_queries": self.log_queries,
                "enable_blocking": self.enable_blocking,
                "cleanup_days": self.cleanup_days
            }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def update_setting(self, key, value):
        """Update a single configuration setting"""
        if hasattr(self, key):
            setattr(self, key, value)
            self.save_config()
            return True
        return False
    
    def get_all_settings(self):
        """Get all configuration settings as dictionary"""
        return {
            "dns_host": self.dns_host,
            "dns_port": self.dns_port,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "upstream_dns": self.upstream_dns,
            "cache_size": self.cache_size,
            "cache_ttl": self.cache_ttl,
            "log_queries": self.log_queries,
            "enable_blocking": self.enable_blocking,
            "cleanup_days": self.cleanup_days
        }
