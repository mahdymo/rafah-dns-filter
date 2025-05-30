# API Documentation

REST API endpoints for the DNS Filter application.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### Statistics

#### GET /api/stats
Get overall DNS query statistics.

**Parameters:**
- `hours` (optional): Number of hours to look back (default: 24)

**Response:**
```json
{
  "total_queries": 1250,
  "blocked_queries": 320,
  "cached_queries": 180,
  "unique_domains": 95,
  "block_rate": 25.6,
  "cache_rate": 14.4,
  "bandwidth_saved": 327680,
  "bandwidth_savings_percent": 23.5,
  "estimated_total_bandwidth": 1392640,
  "top_blocked": [
    {"domain": "facebook.com", "count": 45},
    {"domain": "googleadservices.com", "count": 32}
  ],
  "top_domains": [
    {"domain": "google.com", "count": 124},
    {"domain": "github.com", "count": 89}
  ]
}
```

#### GET /api/hourly-stats
Get hourly breakdown of DNS query statistics.

**Parameters:**
- `hours` (optional): Number of hours to look back (default: 24)

**Response:**
```json
[
  {
    "timestamp": 1640995200,
    "hour": "14:00",
    "total": 52,
    "blocked": 13,
    "allowed": 39
  }
]
```

#### GET /api/bandwidth-stats
Get detailed bandwidth usage and savings statistics.

**Response:**
```json
{
  "total_bandwidth_saved": 327680,
  "estimated_total_bandwidth": 1392640,
  "bandwidth_savings_percent": 23.5,
  "bandwidth_efficiency": {
    "dns_overhead": 125000,
    "blocked_savings": 327680,
    "cache_savings": 9000,
    "additional_savings": 0
  }
}
```

### Query Logs

#### GET /api/logs
Get recent DNS query logs.

**Parameters:**
- `limit` (optional): Maximum number of queries to return (default: 100)

**Response:**
```json
[
  {
    "timestamp": "2025-05-30 14:30:15",
    "domain": "google.com",
    "query_type": "A",
    "client_ip": "192.168.1.100",
    "blocked": false,
    "cached": true
  }
]
```

### Domain Management

#### POST /api/domain/block
Block a specific domain.

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Domain example.com blocked successfully"
}
```

#### POST /api/domain/unblock
Unblock a specific domain.

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Domain example.com unblocked successfully"
}
```

### Blocklist Management

#### GET /api/blocklists
Get all configured remote blocklists.

**Response:**
```json
[
  "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
  "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"
]
```

#### POST /api/blocklists
Add a new remote blocklist.

**Request Body:**
```json
{
  "url": "https://example.com/blocklist.txt"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Blocklist added successfully"
}
```

#### DELETE /api/blocklists
Remove a remote blocklist.

**Request Body:**
```json
{
  "url": "https://example.com/blocklist.txt"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Blocklist removed successfully"
}
```

#### POST /api/blocklists/update
Update all configured blocklists.

**Response:**
```json
{
  "success": true,
  "message": "Blocklist update started"
}
```

### System Management

#### POST /api/cleanup
Clean up old query logs.

**Request Body:**
```json
{
  "days": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cleaned up 1250 old queries"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "success": false,
  "message": "Invalid domain or failed to block"
}
```

### 404 Not Found
```json
{
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production deployments.

## Examples

### Python Example

```python
import requests

# Get statistics
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
print(f"Total queries: {stats['total_queries']}")
print(f"Blocked: {stats['blocked_queries']} ({stats['block_rate']}%)")

# Block a domain
data = {'domain': 'malware-site.com'}
response = requests.post('http://localhost:5000/api/domain/block', json=data)
result = response.json()
print(result['message'])
```

### JavaScript Example

```javascript
// Get statistics
fetch('/api/stats')
  .then(response => response.json())
  .then(data => {
    console.log(`Total queries: ${data.total_queries}`);
    console.log(`Bandwidth saved: ${data.bandwidth_saved} bytes`);
  });

// Block a domain
fetch('/api/domain/block', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({domain: 'spam-site.com'})
})
.then(response => response.json())
.then(data => console.log(data.message));
```

### cURL Examples

```bash
# Get statistics
curl http://localhost:5000/api/stats

# Block a domain
curl -X POST http://localhost:5000/api/domain/block \
  -H "Content-Type: application/json" \
  -d '{"domain": "malicious-site.com"}'

# Get query logs
curl "http://localhost:5000/api/logs?limit=50"

# Update blocklists
curl -X POST http://localhost:5000/api/blocklists/update
```