"""
Bandwidth Monitor
Advanced bandwidth tracking and analysis for DNS filtering
"""

import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

class BandwidthMonitor:
    """Advanced bandwidth monitoring and analysis"""
    
    def __init__(self, database):
        self.database = database
        self.lock = threading.RLock()
        
        # Real-time tracking
        self.hourly_stats = deque(maxlen=24)  # Last 24 hours
        self.daily_stats = deque(maxlen=30)   # Last 30 days
        
        # Bandwidth calculation constants
        self.DNS_RESPONSE_SIZE = 100          # Average DNS response size
        self.BLOCKED_REQUEST_SAVINGS = 1024   # Average savings per blocked request
        self.CACHED_RESPONSE_SAVINGS = 50     # Average savings per cached response
        self.AD_TRACKER_SAVINGS = 2048        # Higher savings for ad/tracker blocks
        
        # Domain categorization for better savings estimation
        self.high_savings_domains = {
            'googleadservices.com', 'googlesyndication.com', 'doubleclick.net',
            'facebook.com', 'connect.facebook.net', 'graph.facebook.com',
            'amazon-adsystem.com', 'ads.yahoo.com', 'adsystem.com'
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def calculate_bandwidth_savings(self, domain, blocked=False, cached=False):
        """Calculate bandwidth savings for a specific query"""
        savings = 0
        
        if blocked:
            # Higher savings for known ad/tracker domains
            if any(high_domain in domain.lower() for high_domain in self.high_savings_domains):
                savings = self.AD_TRACKER_SAVINGS
            else:
                savings = self.BLOCKED_REQUEST_SAVINGS
        elif cached:
            savings = self.CACHED_RESPONSE_SAVINGS
            
        return savings
    
    def get_detailed_stats(self, hours=24):
        """Get detailed bandwidth statistics"""
        with self.lock:
            try:
                since_timestamp = int(time.time()) - (hours * 3600)
                
                conn = self.database._get_connection()
                
                # Basic query counts
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked,
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached,
                        SUM(bytes_saved) as total_bytes_saved,
                        AVG(response_time) as avg_response_time
                    FROM queries 
                    WHERE timestamp > ?
                ''', (since_timestamp,))
                
                stats = cursor.fetchone()
                total_queries = stats[0] or 0
                blocked_queries = stats[1] or 0
                cached_queries = stats[2] or 0
                total_bytes_saved = stats[3] or 0
                avg_response_time = stats[4] or 0
                
                # Calculate bandwidth metrics
                estimated_normal_bandwidth = total_queries * self.DNS_RESPONSE_SIZE
                bandwidth_from_blocking = blocked_queries * self.BLOCKED_REQUEST_SAVINGS
                bandwidth_from_caching = cached_queries * self.CACHED_RESPONSE_SAVINGS
                total_bandwidth_saved = bandwidth_from_blocking + bandwidth_from_caching + total_bytes_saved
                
                # Calculate total potential bandwidth usage
                estimated_total_bandwidth = estimated_normal_bandwidth + bandwidth_from_blocking
                
                # Calculate savings percentage
                if estimated_total_bandwidth > 0:
                    savings_percentage = (total_bandwidth_saved / estimated_total_bandwidth) * 100
                else:
                    savings_percentage = 0
                
                # Top bandwidth-saving domains
                cursor = conn.execute('''
                    SELECT domain, COUNT(*) as count, SUM(bytes_saved) as saved
                    FROM queries 
                    WHERE timestamp > ? AND (blocked = 1 OR cached = 1)
                    GROUP BY domain 
                    ORDER BY saved DESC, count DESC
                    LIMIT 10
                ''', (since_timestamp,))
                
                top_saving_domains = [
                    {
                        'domain': row[0], 
                        'requests': row[1], 
                        'bytes_saved': row[2] or 0
                    } for row in cursor.fetchall()
                ]
                
                conn.close()
                
                return {
                    'total_queries': total_queries,
                    'blocked_queries': blocked_queries,
                    'cached_queries': cached_queries,
                    'total_bandwidth_saved': total_bandwidth_saved,
                    'estimated_total_bandwidth': estimated_total_bandwidth,
                    'bandwidth_savings_percent': round(savings_percentage, 2),
                    'avg_response_time': round(avg_response_time, 2),
                    'bandwidth_efficiency': {
                        'dns_overhead': estimated_normal_bandwidth,
                        'blocked_savings': bandwidth_from_blocking,
                        'cache_savings': bandwidth_from_caching,
                        'additional_savings': total_bytes_saved
                    },
                    'top_saving_domains': top_saving_domains
                }
                
            except Exception as e:
                print(f"Error calculating bandwidth stats: {e}")
                return self._empty_stats()
    
    def get_hourly_bandwidth_stats(self, hours=24):
        """Get hourly bandwidth statistics for charts"""
        with self.lock:
            try:
                since_timestamp = int(time.time()) - (hours * 3600)
                
                conn = self.database._get_connection()
                cursor = conn.execute('''
                    SELECT 
                        (timestamp / 3600) * 3600 as hour_timestamp,
                        COUNT(*) as total_queries,
                        SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked,
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached,
                        SUM(bytes_saved) as bytes_saved
                    FROM queries 
                    WHERE timestamp > ?
                    GROUP BY hour_timestamp
                    ORDER BY hour_timestamp
                ''', (since_timestamp,))
                
                hourly_data = []
                for row in cursor.fetchall():
                    hour_timestamp = int(row[0])
                    total_queries = row[1]
                    blocked = row[2] or 0
                    cached = row[3] or 0
                    bytes_saved = row[4] or 0
                    
                    # Calculate bandwidth for this hour
                    normal_bandwidth = total_queries * self.DNS_RESPONSE_SIZE
                    blocked_savings = blocked * self.BLOCKED_REQUEST_SAVINGS
                    cached_savings = cached * self.CACHED_RESPONSE_SAVINGS
                    total_savings = blocked_savings + cached_savings + bytes_saved
                    
                    hourly_data.append({
                        'timestamp': hour_timestamp,
                        'hour': datetime.fromtimestamp(hour_timestamp).strftime('%H:%M'),
                        'date': datetime.fromtimestamp(hour_timestamp).strftime('%Y-%m-%d'),
                        'total_queries': total_queries,
                        'blocked': blocked,
                        'cached': cached,
                        'allowed': total_queries - blocked,
                        'bandwidth_used': normal_bandwidth,
                        'bandwidth_saved': total_savings,
                        'savings_percent': round((total_savings / max(normal_bandwidth + blocked_savings, 1)) * 100, 2)
                    })
                
                conn.close()
                return hourly_data
                
            except Exception as e:
                print(f"Error getting hourly bandwidth stats: {e}")
                return []
    
    def get_domain_bandwidth_impact(self, domain):
        """Get bandwidth impact analysis for a specific domain"""
        with self.lock:
            try:
                since_timestamp = int(time.time()) - (24 * 3600)  # Last 24 hours
                
                conn = self.database._get_connection()
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN blocked = 1 THEN 1 ELSE 0 END) as blocked_requests,
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached_requests,
                        SUM(bytes_saved) as total_bytes_saved,
                        AVG(response_time) as avg_response_time
                    FROM queries 
                    WHERE timestamp > ? AND domain = ?
                ''', (since_timestamp, domain))
                
                stats = cursor.fetchone()
                if not stats or stats[0] == 0:
                    conn.close()
                    return None
                
                total_requests = stats[0]
                blocked_requests = stats[1] or 0
                cached_requests = stats[2] or 0
                bytes_saved = stats[3] or 0
                avg_response_time = stats[4] or 0
                
                # Calculate impact
                estimated_savings = self.calculate_bandwidth_savings(domain, 
                                                                   blocked=blocked_requests > 0, 
                                                                   cached=cached_requests > 0)
                total_impact = (blocked_requests * self.BLOCKED_REQUEST_SAVINGS) + \
                              (cached_requests * self.CACHED_RESPONSE_SAVINGS) + bytes_saved
                
                conn.close()
                
                return {
                    'domain': domain,
                    'total_requests': total_requests,
                    'blocked_requests': blocked_requests,
                    'cached_requests': cached_requests,
                    'bandwidth_saved': total_impact,
                    'avg_response_time': round(avg_response_time, 2),
                    'efficiency_score': round((total_impact / max(total_requests * self.DNS_RESPONSE_SIZE, 1)) * 100, 2)
                }
                
            except Exception as e:
                print(f"Error analyzing domain bandwidth impact: {e}")
                return None
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                current_hour = int(time.time() / 3600) * 3600
                stats = self.get_detailed_stats(hours=1)
                
                # Store hourly stats
                self.hourly_stats.append({
                    'timestamp': current_hour,
                    'stats': stats
                })
                
                # Sleep for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                print(f"Error in bandwidth monitoring loop: {e}")
                time.sleep(60)  # Retry in 1 minute on error
    
    def _empty_stats(self):
        """Return empty statistics structure"""
        return {
            'total_queries': 0,
            'blocked_queries': 0,
            'cached_queries': 0,
            'total_bandwidth_saved': 0,
            'estimated_total_bandwidth': 0,
            'bandwidth_savings_percent': 0,
            'avg_response_time': 0,
            'bandwidth_efficiency': {
                'dns_overhead': 0,
                'blocked_savings': 0,
                'cache_savings': 0,
                'additional_savings': 0
            },
            'top_saving_domains': []
        }
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False