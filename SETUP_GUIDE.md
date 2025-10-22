# Setup Guide - Real Estate Data API with MCP Integration

## Quick Start

### Step 1: Install Dependencies

```bash
# Install API dependencies
pip install -r requirements_api.txt

# Or install individually
pip install fastapi uvicorn pydantic pytz requests geopy
```

### Step 2: Start the API Server

```bash
python app.py
```

Server will start on: `http://localhost:8000`

### Step 3: Test the API

Open in browser or curl:

```bash
# Health check
curl http://localhost:8000/health

# Get properties
curl "http://localhost:8000/properties?zip_code=78704&timezone=America/Chicago"

# View API documentation (interactive)
open http://localhost:8000/docs
```

---

## API Server Details

### Main Application File: `app.py`

**Features:**
- FastAPI REST endpoints
- Automatic API documentation (Swagger/ReDoc)
- Timezone-aware timestamps
- CORS enabled for n8n integration
- Error handling and validation
- Pydantic models for response validation

**Endpoints:**
- `GET /health` - Health check
- `GET /properties` - Get properties by ZIP
- `GET /properties/{zip_code}` - Alternative endpoint
- `GET /properties/{zip_code}/top` - Top property
- `GET /properties/{zip_code}/filter` - Filter properties
- `GET /properties/{zip_code}/stats` - Statistics

**Query Parameters:**
- `zip_code` (required): ZIP code to search
- `timezone` (optional): Timezone for timestamp (default: UTC)
- `use_sample` (optional): Use sample data (default: false)
- `force_refresh` (optional): Bypass cache (default: false)

### MCP Server: `mcp_server.py`

**Features:**
- JSON-RPC 2.0 protocol implementation
- 5 available tools:
  1. `get_properties` - Get properties by ZIP
  2. `get_top_property` - Get best property
  3. `filter_properties` - Filter by criteria
  4. `get_statistics` - Get statistics
  5. `compare_zip_codes` - Compare multiple ZIPs

**Usage:**

```bash
python mcp_server.py
```

**Example tool call:**
```json
{
  "jsonrpc": "2.0",
  "method": "call_tool",
  "params": {
    "name": "get_properties",
    "arguments": {
      "zip_code": "78704",
      "timezone": "America/Chicago"
    }
  },
  "id": 1
}
```

---

## Integration Points

### 1. REST API Integration

**For n8n HTTP Request nodes:**
```
http://localhost:8000/properties?zip_code={{$json.zip_code}}&timezone=America/Chicago
```

### 2. MCP Protocol Integration

**For n8n MCP tool nodes:**
- Tool name: `get_properties`
- Arguments: `{"zip_code": "78704", "timezone": "America/Chicago"}`

### 3. Direct Python Integration

```python
from data_collector import data_collector

# Get properties
properties = data_collector.collect_real_estate_data("78704")

# Filter
high_score = [p for p in properties if p['investment_score'] > 80]
```

---

## Timezone Support

The API displays all timestamps with the specified timezone.

**Common Timezones:**
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `Europe/London` - GMT/BST
- `Asia/Tokyo` - JST

**Example Response:**
```json
{
  "timestamp": "2024-01-15 14:30:45 CST (UTC-0600)",
  "timezone": "America/Chicago"
}
```

---

## n8n Workflow Integration

### Option 1: Simple HTTP Request

1. Create HTTP Request node
2. URL: `http://localhost:8000/properties`
3. Query: `zip_code=78704&timezone=America/Chicago`
4. Process results

### Option 2: With Filtering

1. HTTP Request node → Get properties
2. Code node → Filter high-score properties
3. Email/Slack node → Send results

### Option 3: Scheduled Search

1. Cron trigger → Daily 9 AM
2. HTTP Request → Get new properties
3. Compare with previous results
4. Alert if new matches found

See `N8N_INTEGRATION.md` for detailed examples.

---

## MCP Server Integration

The MCP server allows AI agents and other tools to:
- Discover available tools
- Execute property searches
- Filter and compare data
- Get statistics

**Integration with n8n MCP nodes:**
1. Create MCP Tool node in n8n
2. Select tool from `get_properties`, `filter_properties`, etc.
3. Provide parameters
4. Process results

---

## Docker Deployment

### Build Docker Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY data_collector.py .
COPY config.py .
COPY database.py .
COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

### Run with Docker

```bash
# Build
docker build -t realestateapi .

# Run
docker run -p 8000:8000 realestateapi

# With environment variables
docker run -p 8000:8000 \
  -e ZILLOW_API_KEY=your_key \
  -e GOOGLE_PLACES_API_KEY=your_key \
  realestateapi
```

---

## Development & Testing

### Test Endpoints

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Get properties
curl "http://localhost:8000/properties?zip_code=78704&timezone=America/Chicago"

# 3. Get statistics
curl "http://localhost:8000/properties/78704/stats"

# 4. Filter properties
curl "http://localhost:8000/properties/78704/filter?min_price=300000&max_price=500000&min_score=75"

# 5. Get top property
curl "http://localhost:8000/properties/78704/top"
```

### API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Debugging

```python
# Enable logging in app.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

---

## Configuration

### Required Files

1. **config.py** - API configuration
   ```python
   class Config:
       GOOGLE_PLACES_API_KEY = "your_key"
       ZILLOW_API_KEY = "your_key"
       ZILLOW_API_HOST = "zillow56.p.rapidapi.com"
   ```

2. **database.py** - Database manager
   - Handles caching
   - Stores searches
   - Retrieves cached data

3. **data_collector.py** - Main data collection logic
   - Fetches from APIs
   - Calculates scores
   - Manages amenity data

---

## Performance Optimization

### Caching Strategy

- Properties cached for 24 hours per ZIP code
- Use `force_refresh=true` to bypass cache
- Cache stored in database

### Rate Limiting

- Respects upstream API rate limits
- Implements exponential backoff
- Graceful fallback to sample data

### Response Optimization

- Filter results at API level
- Use statistics endpoint for aggregates
- Batch multiple requests efficiently

---

## Error Handling

### Common Issues

**Issue:** API returns 404 for valid ZIP code
- **Solution:** Check if properties exist in that ZIP, try `use_sample=true`

**Issue:** Timezone not recognized
- **Solution:** Use standard IANA timezone format (e.g., `America/Chicago`)

**Issue:** Slow response time
- **Solution:** Use `force_refresh=false` to use cache, try statistics endpoint

**Issue:** No properties found
- **Solution:** Check ZIP code validity, enable sample data, check API logs

---

## Security Considerations

### API Key Management

1. Store API keys in environment variables
   ```bash
   export ZILLOW_API_KEY="your_key"
   export GOOGLE_PLACES_API_KEY="your_key"
   ```

2. Never commit keys to git
3. Use `.env` file (not in git)

### n8n Security

1. Use HTTPS in production
2. Implement API key authentication
3. Restrict webhook URLs
4. Enable n8n access control

---

## Monitoring & Logging

### Application Logs

```bash
# Run with verbose logging
LOGLEVEL=DEBUG python app.py

# Save logs to file
python app.py 2>&1 | tee api.log
```

### Health Monitoring

```bash
# Monitor health endpoint
watch -n 5 'curl http://localhost:8000/health'
```

---

## Next Steps

1. **Configure APIs:**
   - Set Zillow API key
   - Set Google Places API key

2. **Test Integration:**
   - Verify API endpoints work
   - Test with n8n workflow
   - Check timezone handling

3. **Deploy:**
   - Choose deployment method (local, Docker, cloud)
   - Set up monitoring
   - Configure backups

4. **Automate:**
   - Create n8n workflows
   - Set up scheduled searches
   - Configure notifications

---

## Files Overview

| File | Purpose |
|------|---------|
| `app.py` | FastAPI REST application |
| `mcp_server.py` | MCP protocol server |
| `data_collector.py` | Core data collection logic |
| `config.py` | Configuration settings |
| `database.py` | Database operations |
| `API_DOCUMENTATION.md` | Complete API reference |
| `N8N_INTEGRATION.md` | n8n setup & examples |
| `requirements_api.txt` | Python dependencies |

---

## Support

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- See `API_DOCUMENTATION.md` for endpoint details
- See `N8N_INTEGRATION.md` for workflow examples

