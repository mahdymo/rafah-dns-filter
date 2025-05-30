"""
Web Dashboard
Flask-based web interface for monitoring and configuration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import time

class WebDashboard:
    """Flask web dashboard for DNS filter application"""
    
    def __init__(self, config, database, blocklist_manager):
        self.config = config
        self.database = database
        self.blocklist_manager = blocklist_manager
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.secret_key = 'dns-filter-secret-key'
        self.setup_routes()
        
        self.server_thread = None
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            stats = self.database.get_query_stats(24)
            hourly_stats = self.database.get_hourly_stats(24)
            cache_stats = self.blocklist_manager.get_stats()
            
            return render_template('index.html', 
                                 stats=stats, 
                                 hourly_stats=hourly_stats,
                                 cache_stats=cache_stats)
        
        @self.app.route('/api/stats')
        def api_stats():
            """API endpoint for statistics"""
            hours = request.args.get('hours', 24, type=int)
            stats = self.database.get_query_stats(hours)
            return jsonify(stats)
        
        @self.app.route('/api/bandwidth-stats')
        def api_bandwidth_stats():
            """API endpoint for detailed bandwidth statistics"""
            hours = request.args.get('hours', 24, type=int)
            stats = self.database.get_query_stats(hours)
            return jsonify(stats)
        
        @self.app.route('/api/hourly-stats')
        def api_hourly_stats():
            """API endpoint for hourly statistics"""
            hours = request.args.get('hours', 24, type=int)
            stats = self.database.get_hourly_stats(hours)
            return jsonify(stats)
        
        @self.app.route('/logs')
        def logs():
            """Query logs page"""
            limit = request.args.get('limit', 100, type=int)
            queries = self.database.get_recent_queries(limit)
            return render_template('logs.html', queries=queries)
        
        @self.app.route('/api/logs')
        def api_logs():
            """API endpoint for query logs"""
            limit = request.args.get('limit', 100, type=int)
            queries = self.database.get_recent_queries(limit)
            return jsonify(queries)
        
        @self.app.route('/blocklists')
        def blocklists():
            """Blocklists management page"""
            remote_lists = self.database.get_remote_blocklists()
            return render_template('blocklists.html', remote_lists=remote_lists)
        
        @self.app.route('/api/blocklists', methods=['GET', 'POST', 'DELETE'])
        def api_blocklists():
            """API endpoint for blocklist management"""
            if request.method == 'GET':
                return jsonify(self.database.get_remote_blocklists())
            
            elif request.method == 'POST':
                data = request.get_json()
                url = data.get('url')
                if url and self.blocklist_manager.add_remote_blocklist(url):
                    return jsonify({'success': True, 'message': 'Blocklist added successfully'})
                else:
                    return jsonify({'success': False, 'message': 'Invalid URL or failed to add blocklist'}), 400
            
            elif request.method == 'DELETE':
                data = request.get_json()
                url = data.get('url')
                if url:
                    self.blocklist_manager.remove_remote_blocklist(url)
                    return jsonify({'success': True, 'message': 'Blocklist removed successfully'})
                else:
                    return jsonify({'success': False, 'message': 'URL required'}), 400
        
        @self.app.route('/api/blocklists/update', methods=['POST'])
        def api_update_blocklists():
            """API endpoint to update all blocklists"""
            try:
                # Run update in background thread
                threading.Thread(target=self.blocklist_manager.update_blocklists, daemon=True).start()
                return jsonify({'success': True, 'message': 'Blocklist update started'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/domain/block', methods=['POST'])
        def api_block_domain():
            """API endpoint to block a domain"""
            data = request.get_json()
            domain = data.get('domain')
            if domain and self.blocklist_manager.add_domain(domain):
                return jsonify({'success': True, 'message': f'Domain {domain} blocked successfully'})
            else:
                return jsonify({'success': False, 'message': 'Invalid domain or failed to block'}), 400
        
        @self.app.route('/api/domain/unblock', methods=['POST'])
        def api_unblock_domain():
            """API endpoint to unblock a domain"""
            data = request.get_json()
            domain = data.get('domain')
            if domain and self.blocklist_manager.remove_domain(domain):
                return jsonify({'success': True, 'message': f'Domain {domain} unblocked successfully'})
            else:
                return jsonify({'success': False, 'message': 'Domain not found in blocklist'}), 400
        
        @self.app.route('/settings')
        def settings():
            """Settings page"""
            return render_template('settings.html', config=self.config)
        
        @self.app.route('/api/cleanup', methods=['POST'])
        def api_cleanup():
            """API endpoint to cleanup old queries"""
            data = request.get_json()
            days = data.get('days', 30)
            deleted_count = self.database.cleanup_old_queries(days)
            return jsonify({'success': True, 'message': f'Cleaned up {deleted_count} old queries'})
        
        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('index.html'), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    def run(self):
        """Run the Flask web server"""
        try:
            self.app.run(
                host=self.config.web_host,
                port=self.config.web_port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            print(f"Error running web dashboard: {e}")
    
    def stop(self):
        """Stop the web server"""
        # Flask doesn't have a built-in stop method when run with app.run()
        # In a production environment, you would use a WSGI server like Gunicorn
        print("Web dashboard stop requested")
