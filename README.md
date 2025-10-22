# Real Estate Data API - Complete Integration Suite

A production-ready REST API and MCP server for real estate property search, analysis, and investment scoring with timezone support for n8n and other automation platforms.

## 🎯 Features

### Core Functionality
- ✅ **Property Search by ZIP Code** - Find properties with full details
- ✅ **Investment Score Analysis** - Composite scoring based on price, location, market trends, and amenities
- ✅ **Amenity Distance Calculation** - Distances to Starbucks, grocery stores, retail
- ✅ **Advanced Filtering** - Filter by price, bedrooms, investment score, days on market
- ✅ **Statistical Analysis** - Aggregate statistics for market analysis
- ✅ **Smart Caching** - 24-hour cache to reduce API calls

### Integration Support
- ✅ **REST API** - FastAPI with automatic documentation (Swagger/ReDoc)
- ✅ **MCP Server** - Model Context Protocol for AI agents and n8n
- ✅ **Timezone Support** - Display times in user's timezone (not just UTC)
- ✅ **n8n Integration** - Ready-to-use workflows and examples
- ✅ **CORS Enabled** - Works with cross-origin requests

### Developer Tools
- ✅ **OpenAPI/Swagger Documentation** - Auto-generated interactive docs
- ✅ **Postman Collection** - Ready-to-import API collection
- ✅ **Python Examples** - Code examples for all endpoints
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Logging** - Detailed logging for debugging

---

## 📋 What's Included

### Core Files
| File | Purpose |
|------|---------|
| `app.py` | FastAPI REST application (starts on port 8000) |
| `mcp_server.py` | MCP protocol server for AI/automation tools |
| `data_collector.py` | Original data collection logic |
| `config.py` | Configuration settings |
| `database.py` | Database and caching logic |

### Documentation
| File | Purpose |
|------|---------|
| `API_DOCUMENTATION.md` | Complete API reference with MCP schema |
| `N8N_INTEGRATION.md` | n8n setup, workflows, and examples |
| `SETUP_GUIDE.md` | Installation, configuration, deployment |
| `README.md` | This file |

### Integration Tools
| File | Purpose |
|------|---------|
| `examples.py` | Python usage examples for all endpoints |
| `postman_collection.json` | Postman collection for API testing |
| `requirements_api.txt` | Python dependencies |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Start the API
```bash
python app.py
```
Server runs on: `http://localhost:8000`

### 3. Test It
```bash
curl "http://localhost:8000/properties?zip_code=78704&timezone=America/Chicago"
```

### 4. View API Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📡 API Endpoints

All endpoints return responses with timezone-aware timestamps.

### Core Endpoints

#### Get Properties
```
GET /properties?zip_code=78704&timezone=America/Chicago
```
Returns: List of properties with all details and investment scores

#### Get Top Property
```
GET /properties/{zip_code}/top?timezone=America/Chicago
```
Returns: Single property with highest investment score

#### Filter Properties
```
GET /properties/{zip_code}/filter?min_price=300000&max_price=500000&min_score=75&timezone=America/Chicago
```
Returns: Filtered list of properties

#### Get Statistics
```
GET /properties/{zip_code}/stats?timezone=America/Chicago
```
Returns: Aggregate statistics (average price, score, etc.)

#### Health Check
```
GET /health
```
Returns: API health status

---

## 🕐 Timezone Support

The API displays all timestamps in the specified timezone, not just UTC.

**Example Response:**
```json
{
  "timestamp": "2024-01-15 14:30:45 CST (UTC-0600)",
  "timezone": "America/Chicago"
}
```

**Supported Timezones:**
```
America/New_York          America/Chicago          America/Denver
America/Los_Angeles       America/Anchorage        Pacific/Honolulu
Europe/London             Europe/Paris             Asia/Tokyo
Asia/Shanghai             Australia/Sydney         UTC
... and many more IANA timezone formats
```

---

## 🔗 Integration Guides

### n8n Integration
See `N8N_INTEGRATION.md` for:
- HTTP Request node configuration
- Workflow examples
- Scheduling and triggers
- Error handling
- Filtering and processing

**Quick Example:**
```
HTTP Request Node:
URL: http://localhost:8000/properties
Query: zip_code={{$json.zip_code}}&timezone=America/Chicago
```

### MCP Server Integration
See `API_DOCUMENTATION.md` MCP section for:
- Tool definitions
- JSON-RPC protocol
- Parameter schemas
- Integration with AI agents

**Available Tools:**
1. `get_properties` - Get properties by ZIP
2. `get_top_property` - Get best property
3. `filter_properties` - Filter by criteria
4. `get_statistics` - Get statistics
5. `compare_zip_codes` - Compare multiple ZIPs

### Python Integration
See `examples.py` for code examples:
```python
from data_collector import data_collector

properties = data_collector.collect_real_estate_data("78704")
high_score = [p for p in properties if p['investment_score'] > 80]
```

---

## 📊 API Response Example

```json
{
  "zip_code": "78704",
  "count": 1,
  "timestamp": "2024-01-15 14:30:45 CST (UTC-0600)",
  "timezone": "America/Chicago",
  "properties": [
    {
      "address": "4521 Oak Ave",
      "zip_code": "78704",
      "price": 450000,
      "square_feet": 2500,
      "bedrooms": 3,
      "bathrooms": 2.5,
      "price_per_sqft": 180.0,
      "days_on_market": 45,
      "latitude": 30.2672,
      "longitude": -97.7431,
      "property_type": "Single Family",
      "year_built": 2015,
      "lot_size": 0.35,
      "hoa_fees": 0,
      "property_tax": 6750,
      "nearest_starbucks_distance": 0.8,
      "nearest_heb_distance": 1.2,
      "nearest_target_distance": 2.1,
      "investment_score": 78.5,
      "price_score": 20,
      "location_score": 22,
      "market_trend_score": 15,
      "amenity_score": 21
    }
  ]
}
```

---

## 🏗️ Investment Score Breakdown

The investment score (0-100) is calculated from:

| Component | Max Points | Factors |
|-----------|-----------|---------|
| **Price Score** | 25 | Lower price per sqft = higher score |
| **Location Score** | 25 | Newer properties = higher score |
| **Market Trend Score** | 25 | Recent listings or stable older listings = higher score |
| **Amenity Score** | 25 | Proximity to shops, cafes, stores = higher score |

---

## 📚 Documentation Files

### Complete API Reference
See `API_DOCUMENTATION.md` for:
- Detailed endpoint documentation
- Request/response examples
- Error codes and handling
- Timezone reference
- Rate limiting info

### n8n Integration Guide
See `N8N_INTEGRATION.md` for:
- Step-by-step setup
- Pre-built workflow examples
- Configuration for each node type
- Scheduling and automation
- Error handling patterns

### Setup & Deployment
See `SETUP_GUIDE.md` for:
- Installation instructions
- Configuration guide
- Docker deployment
- Production considerations
- Debugging tips

---

## 🧪 Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get properties
curl "http://localhost:8000/properties?zip_code=78704&timezone=America/Chicago"

# Filter properties
curl "http://localhost:8000/properties/78704/filter?min_price=300000&max_price=500000"
```

### Using Python
```bash
python examples.py
```

### Using Postman
1. Import `postman_collection.json` into Postman
2. Set variable: `base_url = http://localhost:8000`
3. Run requests

### Interactive API Docs
1. Start API: `python app.py`
2. Open: `http://localhost:8000/docs`
3. Try endpoints directly in browser

---

## 🔧 Configuration

### Environment Variables
```bash
export ZILLOW_API_KEY="your_key"
export GOOGLE_PLACES_API_KEY="your_key"
export ZILLOW_API_HOST="zillow56.p.rapidapi.com"
```

### config.py
```python
class Config:
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
    ZILLOW_API_HOST = os.getenv("ZILLOW_API_HOST", "zillow56.p.rapidapi.com")
```

---

## 🚢 Deployment

### Local Development
```bash
python app.py
```

### Docker
```bash
docker build -t realestateapi .
docker run -p 8000:8000 realestateapi
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 🔍 Monitoring & Debugging

### Check API Health
```bash
curl http://localhost:8000/health
```

### View API Logs
```bash
tail -f api.log
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Endpoint Performance
```bash
time curl "http://localhost:8000/properties?zip_code=78704"
```

---

## 🤝 Integration Workflows

### Example 1: Daily Property Alerts
```
Schedule (9 AM) 
  → Get Properties (ZIP: 78704)
  → Filter (Score > 75)
  → Slack Notification
```

### Example 2: Price Monitoring
```
Schedule (Every 6 Hours)
  → Get Properties
  → Compare with Previous
  → Alert if New Matches
  → Email to Agent
```

### Example 3: Lead Generation
```
Webhook (Form Input)
  → Get Properties
  → Filter & Score
  → Create in CRM
  → Send Report Email
```

---

## 📋 Query Parameters Reference

### All Endpoints
| Parameter | Type | Description |
|-----------|------|-------------|
| `zip_code` | string | ZIP code (required) |
| `timezone` | string | Timezone for timestamp (default: UTC) |

### Get Properties
| Parameter | Type | Description |
|-----------|------|-------------|
| `use_sample` | boolean | Use sample data |
| `force_refresh` | boolean | Bypass cache |

### Filter Endpoint
| Parameter | Type | Description |
|-----------|------|-------------|
| `min_price` | integer | Minimum price |
| `max_price` | integer | Maximum price |
| `min_bedrooms` | integer | Min bedrooms |
| `max_bedrooms` | integer | Max bedrooms |
| `min_score` | float | Min investment score |
| `max_days_on_market` | integer | Max days on market |

---

## 🎓 Learning Resources

1. **FastAPI Documentation:** https://fastapi.tiangolo.com/
2. **n8n Documentation:** https://docs.n8n.io/
3. **MCP Specification:** [Model Context Protocol](https://modelcontextprotocol.io/)
4. **REST API Best Practices:** https://restfulapi.net/

---

## 🐛 Troubleshooting

### API Won't Start
```bash
# Check port 8000 is free
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Try different port
python app.py --port 8001
```

### No Properties Found
```bash
# Try with sample data
?use_sample=true

# Verify ZIP code
curl "http://localhost:8000/properties?zip_code=78704&use_sample=true"
```

### Timezone Not Working
```bash
# Verify timezone format (use IANA standard)
?timezone=America/Chicago  # ✓ Correct
?timezone=CST              # ✗ Wrong

# List all valid timezones
python -c "import pytz; print(pytz.all_timezones)"
```

### n8n Connection Issues
```bash
# Verify API is running
curl http://localhost:8000/health

# Check n8n can reach API
# Add http://localhost:8000/health to n8n HTTP node
# Check response
```

---

## 📝 API Field Descriptions

### Property Data Fields
- **address** - Full property address
- **price** - Sale price in USD
- **square_feet** - Living area in sq ft
- **bedrooms/bathrooms** - Number of beds/baths
- **price_per_sqft** - Price divided by square footage
- **investment_score** - Composite score (0-100)
- **days_on_market** - Days listed
- **latitude/longitude** - GPS coordinates
- **property_type** - Single Family, Townhouse, Condo, etc.
- **year_built** - Year of construction
- **nearest_*_distance** - Distances in miles to amenities
- **score components** - Breakdown of investment score

---

## 📞 Support

### API Documentation
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **OpenAPI Spec:** http://localhost:8000/openapi.json

### Files
- API Reference: `API_DOCUMENTATION.md`
- n8n Guide: `N8N_INTEGRATION.md`
- Setup Guide: `SETUP_GUIDE.md`
- Code Examples: `examples.py`
- Postman: `postman_collection.json`

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 📄 License

[Add your license here]

---

## 🎉 Quick Reference

### Start API
```bash
python app.py
```

### View Docs
```
http://localhost:8000/docs
```

### Example Request
```bash
curl "http://localhost:8000/properties?zip_code=78704&timezone=America/Chicago"
```

### Run Examples
```bash
python examples.py
```

### Import to Postman
1. Import `postman_collection.json`
2. Set `base_url` to `http://localhost:8000`

### Use in n8n
1. Add HTTP Request node
2. URL: `http://localhost:8000/properties`
3. Query: `zip_code={{$json.zip_code}}&timezone=America/Chicago`

---

**Created:** 2024
**API Version:** 1.0.0
**Status:** Production Ready ✅

