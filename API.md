# 📡 API Documentation - Docker Manager Pro

## Base URL
```
http://localhost:3000/api
```

## Authentication
Все endpoints требуют валидный Docker access.

## Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-01-15T17:07:00Z"
}
```

### Containers

#### List All Containers
```
GET /containers
```

Response:
```json
[
  {
    "Id": "a1b2c3d4e5f6...",
    "Names": ["/nginx-web"],
    "Image": "nginx:latest",
    "State": "running",
    "Ports": [{"PrivatePort": 80, "PublicPort": 80}],
    "Created": 1674000000
  }
]
```

#### Get Container Details
```
GET /containers/:id
```

#### Create Container
```
POST /containers
Content-Type: application/json

{
  "Image": "nginx:latest",
  "name": "my-nginx",
  "Env": ["KEY=value"],
  "PortBindings": {"80/tcp": [{"HostPort": "8080"}]}
}
```

#### Start Container
```
POST /containers/:id/start
```

#### Stop Container
```
POST /containers/:id/stop
```

#### Remove Container
```
DELETE /containers/:id
```

### Images

#### List Images
```
GET /images
```

#### Pull Image
```
POST /images/create?fromImage=nginx:latest
```

#### Remove Image
```
DELETE /images/:id
```

### Networks

#### List Networks
```
GET /networks
```

#### Inspect Network
```
GET /networks/:id
```

### Volumes

#### List Volumes
```
GET /volumes
```

#### Inspect Volume
```
GET /volumes/:name
```

#### Remove Volume
```
DELETE /volumes/:name
```

## Error Responses

### 400 Bad Request
```json
{"error": "Invalid parameters"}
```

### 404 Not Found
```json
{"error": "Container not found"}
```

### 500 Internal Server Error
```json
{"error": "Docker daemon error"}
```

## Rate Limiting
- 100 requests per minute per IP
- WebSocket connections: unlimited

## Examples

### cURL

```bash
# List containers
curl http://localhost:3000/api/containers

# Get container details
curl http://localhost:3000/api/containers/a1b2c3d4e5f6

# Start container
curl -X POST http://localhost:3000/api/containers/a1b2c3d4e5f6/start

# Create container
curl -X POST http://localhost:3000/api/containers \
  -H "Content-Type: application/json" \
  -d '{"Image":"nginx","name":"my-nginx"}'
```

### JavaScript Fetch

```javascript
// List containers
fetch('http://localhost:3000/api/containers')
  .then(r => r.json())
  .then(data => console.log(data));

// Start container
fetch('http://localhost:3000/api/containers/:id/start', {
  method: 'POST'
})
.then(r => r.json())
.then(data => console.log(data));
```

### Python Requests

```python
import requests

# List containers
response = requests.get('http://localhost:3000/api/containers')
containers = response.json()

# Start container
requests.post(f'http://localhost:3000/api/containers/{id}/start')
```

## WebSocket Events (Real-time)

```javascript
const ws = new WebSocket('ws://localhost:3000/socket');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'container.status') {
    console.log('Container status changed:', data.container);
  }
};
```

---

**API Version**: 1.0.0  
**Last Updated**: 2025-01-15
