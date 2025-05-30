"""
Blocklist Manager
Handles loading, updating, and querying of DNS blocklists
"""

import os
import re
import threading
import requests
import time
from urllib.parse import urlparse

class BlocklistManager:
    """Manages DNS blocklists for filtering"""
    
    def __init__(self, database):
        self.database = database
        self.blocked_domains = set()
        self.blocklists = []
        self.lock = threading.RLock()
        self.last_update = None
        
    def load_blocklists(self):
        """Load all configured blocklists"""
        with self.lock:
            print("Loading blocklists...")
            self.blocked_domains.clear()
            
            # Load local blocklist files
            blocklist_dir = "blocklists"
            if os.path.exists(blocklist_dir):
                for filename in os.listdir(blocklist_dir):
                    if filename.endswith('.txt'):
                        filepath = os.path.join(blocklist_dir, filename)
                        self._load_local_blocklist(filepath)
            
            # Load remote blocklists from database config
            remote_lists = self.database.get_remote_blocklists()
            for url in remote_lists:
                self._load_remote_blocklist(url)
            
            self.last_update = time.time()
            print(f"Loaded {len(self.blocked_domains)} blocked domains")
    
    def _load_local_blocklist(self, filepath):
        """Load blocklist from local file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = self._parse_blocklist_line(line.strip())
                    if domain:
                        self.blocked_domains.add(domain.lower())
            print(f"Loaded local blocklist: {filepath}")
        except Exception as e:
            print(f"Error loading local blocklist {filepath}: {e}")
    
    def _load_remote_blocklist(self, url):
        """Load blocklist from remote URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            for line in response.text.splitlines():
                domain = self._parse_blocklist_line(line.strip())
                if domain:
                    self.blocked_domains.add(domain.lower())
            
            print(f"Loaded remote blocklist: {url}")
        except Exception as e:
            print(f"Error loading remote blocklist {url}: {e}")
    
    def _parse_blocklist_line(self, line):
        """Parse a single line from a blocklist file"""
        # Skip comments and empty lines
        if not line or line.startswith('#') or line.startswith('!'):
            return None
        
        # Handle different blocklist formats
        # AdBlock format: ||domain.com^
        if line.startswith('||') and line.endswith('^'):
            return line[2:-1]
        
        # Hosts file format: 0.0.0.0 domain.com or 127.0.0.1 domain.com
        if line.startswith(('0.0.0.0', '127.0.0.1')):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
        
        # Plain domain format
        if self._is_valid_domain(line):
            return line
        
        return None
    
    def _is_valid_domain(self, domain):
        """Check if string is a valid domain name"""
        if not domain or len(domain) > 253:
            return False
        
        # Basic domain validation
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
            r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_regex.match(domain))
    
    def is_blocked(self, domain):
        """Check if a domain is blocked"""
        with self.lock:
            domain = domain.lower()
            
            # Check exact match
            if domain in self.blocked_domains:
                return True
            
            # Check subdomain blocking
            parts = domain.split('.')
            for i in range(len(parts)):
                parent_domain = '.'.join(parts[i:])
                if parent_domain in self.blocked_domains:
                    return True
            
            return False
    
    def add_domain(self, domain):
        """Add a domain to the blocklist"""
        with self.lock:
            if self._is_valid_domain(domain):
                self.blocked_domains.add(domain.lower())
                # Save to local blocklist file
                self._save_custom_domains()
                return True
            return False
    
    def remove_domain(self, domain):
        """Remove a domain from the blocklist"""
        with self.lock:
            domain = domain.lower()
            if domain in self.blocked_domains:
                self.blocked_domains.remove(domain)
                self._save_custom_domains()
                return True
            return False
    
    def _save_custom_domains(self):
        """Save custom domains to a local file"""
        try:
            custom_file = "blocklists/custom.txt"
            os.makedirs("blocklists", exist_ok=True)
            
            # Read existing custom domains
            existing_domains = set()
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        domain = line.strip()
                        if domain and not domain.startswith('#'):
                            existing_domains.add(domain)
            
            # Find domains that were manually added
            custom_domains = self.blocked_domains - existing_domains
            
            # Write custom domains to file
            if custom_domains:
                with open(custom_file, 'a', encoding='utf-8') as f:
                    for domain in sorted(custom_domains):
                        f.write(f"{domain}\n")
        except Exception as e:
            print(f"Error saving custom domains: {e}")
    
    def get_stats(self):
        """Get blocklist statistics"""
        with self.lock:
            return {
                'total_blocked_domains': len(self.blocked_domains),
                'last_update': self.last_update,
                'blocklist_count': len(self.blocklists)
            }
    
    def add_remote_blocklist(self, url):
        """Add a remote blocklist URL"""
        if self._is_valid_url(url):
            self.database.add_remote_blocklist(url)
            return True
        return False
    
    def remove_remote_blocklist(self, url):
        """Remove a remote blocklist URL"""
        self.database.remove_remote_blocklist(url)
        return True
    
    def _is_valid_url(self, url):
        """Check if string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def update_blocklists(self):
        """Update all blocklists"""
        self.load_blocklists()
