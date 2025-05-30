"""
Database Manager
Handles SQLite database operations for query logging and configuration
"""

import sqlite3
import threading
import time
from datetime import datetime, timedelta

class Database:
    """SQLite database manager for DNS filter application"""
    
    def __init__(self, db_path="dns_filter.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
        
    def initialize(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Create queries table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp INTEGER NOT NULL,
                        domain TEXT NOT NULL,
                        query_type TEXT NOT NULL,
                        client_ip TEXT NOT NULL,
                        blocked INTEGER DEFAULT 0,
                        cached INTEGER DEFAULT 0,
                        response_time REAL DEFAULT 0,
                        bytes_saved INTEGER DEFAULT 0
                    )
                ''')
                
                # Add bytes_saved column if it doesn't exist (for existing databases)
                try:
                    conn.execute('ALTER TABLE queries ADD COLUMN bytes_saved INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                # Create settings table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                ''')
                
                # Create blocklists table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS remote_blocklists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        enabled INTEGER DEFAULT 1,
                        last_updated INTEGER DEFAULT 0
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_queries_domain ON queries(domain)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_queries_blocked ON queries(blocked)')
                
                conn.commit()
                print("Database initialized successfully")
                
            except Exception as e:
                print(f"Error initializing database: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def log_query(self, domain, query_type, client_ip, blocked=False, cached=False, response_time=0, bytes_saved=0):
        """Log a DNS query"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute('''
                    INSERT INTO queries (timestamp, domain, query_type, client_ip, blocked, cached, response_time, bytes_saved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (int(time.time()), domain, query_type, client_ip, 
                      1 if blocked else 0, 1 if cached else 0, response_time, bytes_saved))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error logging query: {e}")
    
    def get_query_stats(self, hours=24):
        """Get query statistics for the last N hours"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                since_timestamp = int(time.time()) - (hours * 3600)
                
                # Total queries
                cursor = conn.execute('SELECT COUNT(*) FROM queries WHERE timestamp > ?', (since_timestamp,))
                total_queries = cursor.fetchone()[0]
                
                # Blocked queries
                cursor = conn.execute('SELECT COUNT(*) FROM queries WHERE timestamp > ? AND blocked = 1', (since_timestamp,))
                blocked_queries = cursor.fetchone()[0]
                
                # Cached queries
                cursor = conn.execute('SELECT COUNT(*) FROM queries WHERE timestamp > ? AND cached = 1', (since_timestamp,))
                cached_queries = cursor.fetchone()[0]
                
                # Unique domains
                cursor = conn.execute('SELECT COUNT(DISTINCT domain) FROM queries WHERE timestamp > ?', (since_timestamp,))
                unique_domains = cursor.fetchone()[0]
                
                # Top blocked domains
                cursor = conn.execute('''
                    SELECT domain, COUNT(*) as count 
                    FROM queries 
                    WHERE timestamp > ? AND blocked = 1 
                    GROUP BY domain 
                    ORDER BY count DESC 
                    LIMIT 10
                ''', (since_timestamp,))
                top_blocked = cursor.fetchall()
                
                # Top queried domains
                cursor = conn.execute('''
                    SELECT domain, COUNT(*) as count 
                    FROM queries 
                    WHERE timestamp > ? 
                    GROUP BY domain 
                    ORDER BY count DESC 
                    LIMIT 10
                ''', (since_timestamp,))
                top_domains = cursor.fetchall()
                
                # Bandwidth savings calculations
                cursor = conn.execute('SELECT SUM(bytes_saved) FROM queries WHERE timestamp > ?', (since_timestamp,))
                total_bytes_saved = cursor.fetchone()[0] or 0
                
                # Estimated bandwidth usage (approximate calculations)
                # Average DNS response size: 100 bytes
                # Average blocked request savings: 1KB (prevents HTTP request)
                # Average cached response savings: 50 bytes (no upstream query)
                dns_response_size = 100
                blocked_request_savings = 1024  # 1KB per blocked request
                cached_response_savings = 50    # 50 bytes per cached response
                
                estimated_total_bandwidth = (total_queries * dns_response_size) + (blocked_queries * blocked_request_savings)
                bandwidth_saved = (blocked_queries * blocked_request_savings) + (cached_queries * cached_response_savings) + total_bytes_saved
                bandwidth_savings_percent = round((bandwidth_saved / max(estimated_total_bandwidth, 1) * 100), 2)
                
                conn.close()
                
                return {
                    'total_queries': total_queries,
                    'blocked_queries': blocked_queries,
                    'cached_queries': cached_queries,
                    'unique_domains': unique_domains,
                    'block_rate': round((blocked_queries / total_queries * 100) if total_queries > 0 else 0, 2),
                    'cache_rate': round((cached_queries / total_queries * 100) if total_queries > 0 else 0, 2),
                    'top_blocked': [{'domain': row[0], 'count': row[1]} for row in top_blocked],
                    'top_domains': [{'domain': row[0], 'count': row[1]} for row in top_domains],
                    'bandwidth_saved': bandwidth_saved,
                    'bandwidth_savings_percent': bandwidth_savings_percent,
                    'estimated_total_bandwidth': estimated_total_bandwidth
                }
                
            except Exception as e:
                print(f"Error getting query stats: {e}")
                return {
                    'total_queries': 0,
                    'blocked_queries': 0,
                    'cached_queries': 0,
                    'unique_domains': 0,
                    'block_rate': 0,
                    'cache_rate': 0,
                    'top_blocked': [],
                    'top_domains': [],
                    'bandwidth_saved': 0,
                    'bandwidth_savings_percent': 0,
                    'estimated_total_bandwidth': 0
                }
    
    def get_recent_queries(self, limit=100):
        """Get recent queries"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute('''
                    SELECT timestamp, domain, query_type, client_ip, blocked, cached
                    FROM queries 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                queries = []
                for row in cursor.fetchall():
                    queries.append({
                        'timestamp': datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'),
                        'domain': row[1],
                        'query_type': row[2],
                        'client_ip': row[3],
                        'blocked': bool(row[4]),
                        'cached': bool(row[5])
                    })
                
                conn.close()
                return queries
                
            except Exception as e:
                print(f"Error getting recent queries: {e}")
                return []
    
    def get_hourly_stats(self, hours=24):
        """Get hourly query statistics"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                since_timestamp = int(time.time()) - (hours * 3600)
                
                cursor = conn.execute('''
                    SELECT 
                        (timestamp / 3600) * 3600 as hour_timestamp,
                        COUNT(*) as total,
                        SUM(blocked) as blocked
                    FROM queries 
                    WHERE timestamp > ?
                    GROUP BY hour_timestamp
                    ORDER BY hour_timestamp
                ''', (since_timestamp,))
                
                stats = []
                for row in cursor.fetchall():
                    stats.append({
                        'timestamp': int(row[0]),
                        'hour': datetime.fromtimestamp(row[0]).strftime('%H:%M'),
                        'total': row[1],
                        'blocked': row[2],
                        'allowed': row[1] - row[2]
                    })
                
                conn.close()
                return stats
                
            except Exception as e:
                print(f"Error getting hourly stats: {e}")
                return []
    
    def cleanup_old_queries(self, days=30):
        """Clean up queries older than specified days"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cutoff_timestamp = int(time.time()) - (days * 24 * 3600)
                
                cursor = conn.execute('DELETE FROM queries WHERE timestamp < ?', (cutoff_timestamp,))
                deleted_count = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                print(f"Cleaned up {deleted_count} old query records")
                return deleted_count
                
            except Exception as e:
                print(f"Error cleaning up old queries: {e}")
                return 0
    
    def get_remote_blocklists(self):
        """Get all remote blocklist URLs"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute('SELECT url FROM remote_blocklists WHERE enabled = 1')
                urls = [row[0] for row in cursor.fetchall()]
                conn.close()
                return urls
            except Exception as e:
                print(f"Error getting remote blocklists: {e}")
                return []
    
    def add_remote_blocklist(self, url):
        """Add a remote blocklist URL"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute('INSERT OR IGNORE INTO remote_blocklists (url) VALUES (?)', (url,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error adding remote blocklist: {e}")
                return False
    
    def remove_remote_blocklist(self, url):
        """Remove a remote blocklist URL"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute('DELETE FROM remote_blocklists WHERE url = ?', (url,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error removing remote blocklist: {e}")
                return False
