# Real Estate Data API - MCP Server Documentation

## Overview

This document provides complete API documentation for the Real Estate Data Collection service. The API is designed to integrate with MCP (Model Context Protocol) servers and automation platforms like n8n.

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/properties` | Get properties by ZIP code |
| GET | `/properties/{zip_code}` | Get properties (path parameter) |
| GET | `/properties/{zip_code}/top` | Get top property by investment score |
| GET | `/properties/{zip_code}/filter` | Filter properties by criteria |
| GET | `/properties/{zip_code}/stats` | Get aggregate statistics |

---

## Detailed Endpoint Documentation

### 1. Health Check
**Endpoint:** `GET /health`

**Purpose:** Verify service availability

**Response:**
```json
{
  "status": "healthy",
  "service": "Real Estate Data API"
}
```

---

### 2. Get Properties by ZIP Code
**Endpoint:** `GET /properties`

**Purpose:** Retrieve all properties for a given ZIP code with investment analysis

**Query Parameters:**
- `zip_code` (string, required): ZIP code to search (e.g., "78704")
- `use_sample` (boolean, optional): Use sample data instead of live API (default: false)
- `force_refresh` (boolean, optional): Force API refresh, ignore cache (default: false)
- `timezone` (string, optional): Timezone for response timestamp (default: "UTC")

**Supported Timezones:**
Common timezones: `America/Chicago`, `America/New_York`, `America/Los_Angeles`, `Europe/London`, `Asia/Tokyo`, etc.

**Example Request:**
```
GET /properties?zip_code=78704&timezone=America/Chicago
```

**Response Model:**
```json
{
  "zip_code": "78704",
  "count": 20,
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

**HTTP Status Codes:**
- `200 OK`: Successfully retrieved properties
- `404 Not Found`: No properties found for ZIP code
- `500 Internal Server Error`: Server error

---

### 3. Get Properties (Path Parameter)
**Endpoint:** `GET /properties/{zip_code}`

**Purpose:** Alternative endpoint using ZIP code as path parameter

**Path Parameters:**
- `zip_code` (string, required): ZIP code to search

**Query Parameters:**
- `timezone` (string, optional): Timezone for response timestamp (default: "UTC")

**Example Request:**
```
GET /properties/78704?timezone=America/Denver
```

---

### 4. Get Top Property
**Endpoint:** `GET /properties/{zip_code}/top`

**Purpose:** Get the single property with the highest investment score

**Path Parameters:**
- `zip_code` (string, required): ZIP code to search

**Query Parameters:**
- `timezone` (string, optional): Timezone for response timestamp (default: "UTC")

**Example Request:**
```
GET /properties/78704/top?timezone=America/Chicago
```

**Response Model:**
```json
{
  "property": {
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
    "investment_score": 85.5,
    "price_score": 25,
    "location_score": 22,
    "market_trend_score": 20,
    "amenity_score": 18
  },
  "timestamp": "2024-01-15 14:30:45 CST (UTC-0600)",
  "timezone": "America/Chicago"
}
```

---

### 5. Filter Properties
**Endpoint:** `GET /properties/{zip_code}/filter`

**Purpose:** Get properties filtered by price, bedrooms, investment score, and market days

**Path Parameters:**
- `zip_code` (string, required): ZIP code to search

**Query Parameters:**
- `min_price` (integer, optional): Minimum property price in USD
- `max_price` (integer, optional): Maximum property price in USD
- `min_bedrooms` (integer, optional): Minimum number of bedrooms
- `max_bedrooms` (integer, optional): Maximum number of bedrooms
- `min_score` (float, optional): Minimum investment score (0-100)
- `max_days_on_market` (integer, optional): Maximum days on market
- `timezone` (string, optional): Timezone for response timestamp (default: "UTC")

**Example Request:**
```
GET /properties/78704/filter?min_price=300000&max_price=600000&min_bedrooms=2&min_score=75&timezone=America/Chicago
```

**Response Model:**
Same as Get Properties endpoint, but filtered results

---

### 6. Get Statistics
**Endpoint:** `GET /properties/{zip_code}/stats`

**Purpose:** Get aggregate statistics for all properties in a ZIP code

**Path Parameters:**
- `zip_code` (string, required): ZIP code to analyze

**Query Parameters:**
- `timezone` (string, optional): Timezone for response timestamp (default: "UTC")

**Example Request:**
```
GET /properties/78704/stats?timezone=America/Chicago
```

**Response Model:**
```json
{
  "zip_code": "78704",
  "total_properties": 20,
  "timestamp": "2024-01-15 14:30:45 CST (UTC-0600)",
  "timezone": "America/Chicago",
  "price": {
    "average": 425500.0,
    "min": 250000,
    "max": 800000
  },
  "investment_score": {
    "average": 72.5,
    "min": 35.0,
    "max": 92.0
  },
  "bedrooms": {
    "average": 3.1,
    "min": 1,
    "max": 5
  },
  "square_feet": {
    "average": 2450.75,
    "min": 800,
    "max": 4000
  }
}
```

---

## MCP Integration Schema

### Function Definition for MCP Servers

```json
{
  "name": "get_real_estate_properties",
  "description": "Retrieves real estate properties by ZIP code with investment analysis and amenity distances",
  "inputSchema": {
    "type": "object",
    "properties": {
      "zip_code": {
        "type": "string",
        "description": "ZIP code to search for properties (e.g., '78704')"
      },
      "timezone": {
        "type": "string",
        "description": "Timezone for timestamp display (e.g., 'America/Chicago')",
        "default": "UTC"
      },
      "use_sample": {
        "type": "boolean",
        "description": "Use sample data instead of live API data",
        "default": false
      },
      "force_refresh": {
        "type": "boolean",
        "description": "Force refresh from API, ignore cache",
        "default": false
      }
    },
    "required": ["zip_code"]
  }
}
```

```json
{
  "name": "filter_real_estate_properties",
  "description": "Filters real estate properties by price, bedrooms, and investment score",
  "inputSchema": {
    "type": "object",
    "properties": {
      "zip_code": {
        "type": "string",
        "description": "ZIP code to search for properties"
      },
      "min_price": {
        "type": "integer",
        "description": "Minimum property price in USD"
      },
      "max_price": {
        "type": "integer",
        "description": "Maximum property price in USD"
      },
      "min_bedrooms": {
        "type": "integer",
        "description": "Minimum number of bedrooms"
      },
      "max_bedrooms": {
        "type": "integer",
        "description": "Maximum number of bedrooms"
      },
      "min_score": {
        "type": "number",
        "description": "Minimum investment score (0-100)"
      },
      "max_days_on_market": {
        "type": "integer",
        "description": "Maximum days on market"
      },
      "timezone": {
        "type": "string",
        "description": "Timezone for timestamp display",
        "default": "UTC"
      }
    },
    "required": ["zip_code"]
  }
}
```

```json
{
  "name": "get_real_estate_statistics",
  "description": "Retrieves aggregate statistics for properties in a ZIP code",
  "inputSchema": {
    "type": "object",
    "properties": {
      "zip_code": {
        "type": "string",
        "description": "ZIP code to analyze"
      },
      "timezone": {
        "type": "string",
        "description": "Timezone for timestamp display",
        "default": "UTC"
      }
    },
    "required": ["zip_code"]
  }
}
```

---

## n8n Integration Guide

### Workflow Steps

#### Step 1: HTTP Request Node
Configure an HTTP request node to call the API:

**Configuration:**
- **Method:** GET
- **URL:** `http://localhost:8000/properties?zip_code={{$json.zip_code}}&timezone=America/Chicago`
- **Headers:** 
  - `Content-Type: application/json`
- **Authentication:** None (or configure as needed)

#### Step 2: Filter Properties
Use the response from step 1 and process with a Code node or Filter node.

**Example Code Node (JavaScript):**
```javascript
// Extract properties with investment score > 75
return {
  high_value_properties: $input.item.json.properties.filter(p => p.investment_score > 75)
};
```

#### Step 3: Further Actions
- Send email notifications with top properties
- Store data in database
- Create records in CRM
- Trigger webhooks

### Example n8n HTTP Node Configuration

```json
{
  "operation": "request",
  "method": "GET",
  "url": "http://localhost:8000/properties",
  "queryParameters": {
    "zip_code": "=={{$json.zip_code}}",
    "timezone": "=America/Chicago",
    "use_sample": false,
    "force_refresh": false
  },
  "headers": {
    "User-Agent": "n8n/integration"
  },
  "sendHeaders": true,
  "sendQuery": true,
  "sendBody": false,
  "responseFormat": "json",
  "timeout": 30,
  "allowUnauthorizedCerts": false
}
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

| Status Code | Scenario | Example |
|------------|----------|---------|
| 400 | Invalid query parameter | ZIP code format invalid |
| 404 | Resource not found | No properties found for ZIP code |
| 422 | Validation error | Missing required parameter |
| 500 | Server error | Unexpected internal error |

---

## Field Descriptions

### Property Data Fields

| Field | Type | Description |
|-------|------|-------------|
| address | string | Full property address |
| zip_code | string | ZIP code |
| price | integer | Sale price in USD |
| square_feet | integer | Living area in sq ft |
| bedrooms | integer | Number of bedrooms |
| bathrooms | float | Number of bathrooms |
| price_per_sqft | float | Price divided by square footage |
| days_on_market | integer | Days listed |
| latitude | float | Property latitude |
| longitude | float | Property longitude |
| property_type | string | Type (Single Family, Townhouse, Condo) |
| year_built | integer | Year of construction |
| lot_size | float | Lot size in acres |
| hoa_fees | float | Monthly HOA fees |
| property_tax | integer | Annual property tax |
| nearest_starbucks_distance | float | Distance in miles |
| nearest_heb_distance | float | Distance to grocery store in miles |
| nearest_target_distance | float | Distance to Target in miles |
| investment_score | float | Composite score 0-100 |
| price_score | float | Price component (0-25) |
| location_score | float | Location component (0-25) |
| market_trend_score | float | Market trend component (0-25) |
| amenity_score | float | Amenities component (0-25) |

### Investment Score Calculation

The investment score is calculated from four components (0-100 total):

- **Price Score (0-25):** Lower price per sqft = higher score
- **Location Score (0-25):** Newer properties = higher score
- **Market Trend Score (0-25):** Recent listings or older stable listings = higher score
- **Amenity Score (0-25):** Proximity to Starbucks, grocery stores, and retail = higher score

---

## Rate Limiting & Caching

- **Cache Duration:** Properties are cached for 24 hours per ZIP code
- **Force Refresh:** Use `force_refresh=true` to bypass cache
- **API Limits:** Subject to upstream Zillow API rate limits

---

## Running the API

### Prerequisites
```bash
pip install fastapi uvicorn pytz pydantic requests geopy
```

### Start the Server
```bash
python app.py
```

Server will run on `http://localhost:8000`

### Access Swagger Documentation
Visit: `http://localhost:8000/docs`

### Access ReDoc Documentation
Visit: `http://localhost:8000/redoc`

---

## Example Use Cases

### Use Case 1: Find Top Properties
```
GET /properties/78704/top?timezone=America/Chicago
```

### Use Case 2: Filter by Budget
```
GET /properties/78704/filter?min_price=250000&max_price=400000&timezone=America/Chicago
```

### Use Case 3: Compare Neighborhoods
```
GET /properties/78704/stats?timezone=America/Chicago
GET /properties/78701/stats?timezone=America/Chicago
```

### Use Case 4: High-Score Deals
```
GET /properties/78704/filter?min_score=80&max_days_on_market=60&timezone=America/Chicago
```

---

## Timezone Reference

**Common US Timezones:**
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time  
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `America/Anchorage` - Alaska Time
- `Pacific/Honolulu` - Hawaii Time

**Other Common Timezones:**
- `Europe/London` - GMT/BST
- `Europe/Paris` - CET/CEST
- `Asia/Tokyo` - JST
- `Asia/Shanghai` - CST
- `Australia/Sydney` - AEDT/AEST
- `UTC` - Coordinated Universal Time

---

## Support & Documentation

- **API Documentation:** `http://localhost:8000/docs`
- **Error Logs:** Check application logs for debugging
- **API Health:** `GET /health`

