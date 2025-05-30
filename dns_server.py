"""
DNS Server Implementation
Handles DNS query interception, filtering, and forwarding
"""

import socket
import threading
import time
from dnslib import DNSRecord, DNSHeader, QTYPE, RCODE
from dnslib.server import DNSServer as DNSLibServer, BaseResolver
from dns_cache import DNSCache

class DNSFilterResolver(BaseResolver):
    """Custom DNS resolver with filtering and caching capabilities"""
    
    def __init__(self, config, database, blocklist_manager):
        self.config = config
        self.database = database
        self.blocklist_manager = blocklist_manager
        self.cache = DNSCache(config.cache_size)
        self.upstream_servers = config.upstream_dns
        
    def resolve(self, request, handler):
        """Resolve DNS query with filtering and caching"""
        try:
            start_time = time.time()
            
            # Parse the request
            query = request.get_q()
            qname = str(query.qname).rstrip('.')
            qtype = QTYPE[query.qtype]
            
            # Log the initial query
            client_ip = handler.client_address[0] if handler else "unknown"
            
            # Check if domain is blocked
            if self.blocklist_manager.is_blocked(qname):
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                # Estimate bandwidth saved by blocking (prevents HTTP requests)
                bytes_saved = 1024  # Average 1KB saved per blocked request
                self.database.log_query(qname, qtype, client_ip, blocked=True, 
                                      response_time=response_time, bytes_saved=bytes_saved)
                return self._create_blocked_response(request)
            
            # Check cache first
            cache_key = f"{qname}:{qtype}"
            cached_response = self.cache.get(cache_key)
            if cached_response:
                response_time = (time.time() - start_time) * 1000
                # Estimate bandwidth saved by caching (no upstream query)
                bytes_saved = 50  # Average 50 bytes saved per cached response
                self.database.log_query(qname, qtype, client_ip, cached=True,
                                      response_time=response_time, bytes_saved=bytes_saved)
                return cached_response
            
            # Forward to upstream DNS
            response = self._forward_query(request)
            if response:
                response_time = (time.time() - start_time) * 1000
                # Calculate response size for bandwidth tracking
                response_size = len(response.pack()) if hasattr(response, 'pack') else 100
                
                # Cache the response
                self.cache.set(cache_key, response, ttl=300)  # 5 minutes default TTL
                
                # Log successful query with bandwidth usage
                self.database.log_query(qname, qtype, client_ip, response_time=response_time)
                return response
            else:
                response_time = (time.time() - start_time) * 1000
                self.database.log_query(qname, qtype, client_ip, response_time=response_time)
                return self._create_error_response(request)
                
        except Exception as e:
            print(f"Error resolving DNS query: {e}")
            return self._create_error_response(request)
    
    def _create_blocked_response(self, request):
        """Create a response for blocked domains"""
        reply = request.reply()
        reply.header.rcode = RCODE.NXDOMAIN
        return reply
    
    def _create_error_response(self, request):
        """Create an error response"""
        reply = request.reply()
        reply.header.rcode = RCODE.SERVFAIL
        return reply
    
    def _forward_query(self, request):
        """Forward query to upstream DNS servers"""
        for upstream in self.upstream_servers:
            try:
                # Create socket for DNS query
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5.0)  # 5 second timeout
                
                # Send query to upstream server
                query_data = request.pack()
                sock.sendto(query_data, (upstream, 53))
                
                # Receive response
                response_data, _ = sock.recvfrom(512)
                sock.close()
                
                # Parse and return response
                response = DNSRecord.parse(response_data)
                return response
                
            except Exception as e:
                print(f"Error forwarding to {upstream}: {e}")
                continue
        
        return None

class DNSServer:
    """DNS Server wrapper class"""
    
    def __init__(self, config, database, blocklist_manager):
        self.config = config
        self.database = database
        self.blocklist_manager = blocklist_manager
        self.resolver = DNSFilterResolver(config, database, blocklist_manager)
        self.server = None
        self.running = False
        
    def start(self):
        """Start the DNS server"""
        try:
            self.running = True
            self.server = DNSLibServer(
                self.resolver,
                port=self.config.dns_port,
                address=self.config.dns_host,
                tcp=False
            )
            
            print(f"DNS Server listening on {self.config.dns_host}:{self.config.dns_port}")
            self.server.start()
            
        except Exception as e:
            print(f"Error starting DNS server: {e}")
            self.running = False
    
    def stop(self):
        """Stop the DNS server"""
        self.running = False
        if self.server:
            try:
                self.server.stop()
                print("DNS Server stopped")
            except Exception as e:
                print(f"Error stopping DNS server: {e}")
