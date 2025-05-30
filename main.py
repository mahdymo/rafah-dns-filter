#!/usr/bin/env python3
"""
Windows DNS Filtering Application - Main Entry Point
A Pi-hole inspired DNS filtering solution for Windows
"""

import os
import sys
import signal
import threading
import time
from config import Config
from dns_server import DNSServer
from web_dashboard import WebDashboard
from database import Database
from blocklist_manager import BlocklistManager

class DNSFilterApp:
    def __init__(self):
        """Initialize the DNS filtering application"""
        self.config = Config()
        self.database = Database()
        self.blocklist_manager = BlocklistManager(self.database)
        self.dns_server = DNSServer(self.config, self.database, self.blocklist_manager)
        self.web_dashboard = WebDashboard(self.config, self.database, self.blocklist_manager)
        
        # Threading control
        self.running = True
        self.dns_thread = None
        self.web_thread = None
        
    def start(self):
        """Start all services"""
        print("Starting Windows DNS Filter Application...")
        
        # Initialize database and blocklists
        self.database.initialize()
        self.blocklist_manager.load_blocklists()
        
        # Start DNS server in a separate thread
        self.dns_thread = threading.Thread(target=self.dns_server.start, daemon=True)
        self.dns_thread.start()
        print(f"DNS Server started on {self.config.dns_host}:{self.config.dns_port}")
        
        # Start web dashboard in a separate thread
        self.web_thread = threading.Thread(target=self.web_dashboard.run, daemon=True)
        self.web_thread.start()
        print(f"Web Dashboard started on http://{self.config.web_host}:{self.config.web_port}")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("\nDNS Filter Application is running!")
        print(f"Web Dashboard: http://{self.config.web_host}:{self.config.web_port}")
        print("Press Ctrl+C to stop...")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all services gracefully"""
        print("\nShutting down DNS Filter Application...")
        self.running = False
        
        if self.dns_server:
            self.dns_server.stop()
            
        if self.web_dashboard:
            self.web_dashboard.stop()
            
        print("Application stopped successfully.")
        
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {sig}")
        self.stop()
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        app = DNSFilterApp()
        app.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
