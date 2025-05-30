"""
DNS Cache Implementation
Provides in-memory caching for DNS responses
"""

import time
import threading
from collections import OrderedDict

class DNSCache:
    """Thread-safe DNS response cache with TTL support"""
    
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key):
        """Get cached DNS response if not expired"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                current_time = time.time()
                
                if current_time < entry['expires']:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    self.stats['hits'] += 1
                    return entry['response']
                else:
                    # Expired, remove from cache
                    del self.cache[key]
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key, response, ttl=300):
        """Set DNS response in cache with TTL"""
        with self.lock:
            current_time = time.time()
            expires = current_time + ttl
            
            # Remove existing entry if present
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = {
                'response': response,
                'expires': expires,
                'created': current_time
            }
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            # Evict oldest entries if cache is full
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def clear(self):
        """Clear all cached entries"""
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0
            }
    
    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def _cleanup_expired(self):
        """Background thread to cleanup expired entries"""
        while True:
            try:
                current_time = time.time()
                expired_keys = []
                
                with self.lock:
                    for key, entry in self.cache.items():
                        if current_time >= entry['expires']:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.cache[key]
                
                # Sleep for 60 seconds before next cleanup
                time.sleep(60)
                
            except Exception as e:
                print(f"Error in cache cleanup: {e}")
                time.sleep(60)
