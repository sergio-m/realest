# n8n Integration Guide - Real Estate Data API

## Overview

This guide provides step-by-step instructions to integrate the Real Estate Data API with n8n for automated workflows.

---

## Prerequisites

1. n8n instance running (self-hosted or cloud)
2. Real Estate Data API running on `http://localhost:8000` (or your API endpoint)
3. Basic n8n workflow knowledge

---

## Integration Setup

### Step 1: Create a New Workflow

1. Open n8n
2. Click **"Create new workflow"**
3. Name it: `Real Estate Property Search`

---

### Step 2: Add HTTP Request Node

1. Click **"Add Node"**
2. Search for **"HTTP Request"**
3. Select **"HTTP Request"** node
4. Configure:

**Tab: Request**
- **Method:** GET
- **URL:** `http://localhost:8000/properties`
- **Send Headers:** Toggle ON
- **Send Query:** Toggle ON

**Tab: Headers**
- **Key:** `Content-Type`
- **Value:** `application/json`

**Tab: Queries**
- **Add Query Parameter:**
  - **Name:** `zip_code`
  - **Value:** `={{$json.zip_code}}` (or enter manually: "78704")
  - **Name:** `timezone`
  - **Value:** `America/Chicago`

---

### Step 3: Add Filter Node (Optional)

Add a Code node to filter results:

1. Click **"Add Node"** → **"Code"**
2. Use JavaScript mode:

```javascript
// Filter properties with investment score > 75
const filtered = {
  high_value: input.item.json.properties.filter(p => p.investment_score > 75),
  count: input.item.json.properties.filter(p => p.investment_score > 75).length,
  average_score: (input.item.json.properties.reduce((a, p) => a + p.investment_score, 0) / input.item.json.properties.length).toFixed(2)
};
return filtered;
```

---

### Step 4: Output/Send Notifications

#### Option A: Send Email

1. Click **"Add Node"** → **"Gmail"** (or your email service)
2. Configure authentication
3. Set subject: `High Value Properties Found in {{$json.zip_code}}`
4. Set body to include properties data

#### Option B: Save to Database

1. Click **"Add Node"** → **"MySQL"** (or PostgreSQL, MongoDB)
2. Configure query:

```sql
INSERT INTO properties (address, zip_code, price, investment_score, timestamp)
VALUES ({{ $json.address }}, {{ $json.zip_code }}, {{ $json.price }}, {{ $json.investment_score }}, NOW())
```

#### Option C: Create Airtable Records

1. Click **"Add Node"** → **"Airtable"**
2. Configure fields to map property data

#### Option D: Slack Notification

1. Click **"Add Node"** → **"Slack"**
2. Configure message:

```
🏠 New Properties Found in ZIP {{zip_code}}!

Top Property: {{properties[0].address}}
Investment Score: {{properties[0].investment_score}}/100
Price: ${{properties[0].price}}
Bedrooms: {{properties[0].bedrooms}}
Distance to Starbucks: {{properties[0].nearest_starbucks_distance}} mi
```

---

## Example Workflows

### Workflow 1: Daily Property Alerts

**Nodes:**
1. Schedule (Cron) → Daily at 9 AM
2. HTTP Request → Get properties for specified ZIP
3. Filter → Only high-score properties (>80)
4. Slack → Send notification with top 3 properties

**Cron Expression:** `0 9 * * *` (Daily at 9 AM)

---

### Workflow 2: Multi-ZIP Code Comparison

**Nodes:**
1. Start trigger
2. HTTP Request (Loop over multiple ZIP codes)
   - Use "Batch mode" with array of zip codes
3. Compare results
4. Create comparison table
5. Send email with comparison

**Configuration:**
```javascript
// Compare statistics
const zips = ["78704", "78701", "78702"];
return zips.map(zip => ({
  "zip_code": zip,
  "url": `http://localhost:8000/properties/${zip}/stats?timezone=America/Chicago`
}));
```

---

### Workflow 3: Price Monitoring Alert

**Nodes:**
1. Scheduled trigger (Every 6 hours)
2. HTTP Request → Get properties
3. Filter → Properties < $400,000 AND investment_score > 75
4. Compare with previous run (store in database)
5. Alert if new matching properties found
6. Email/Slack notification

---

### Workflow 4: Lead Generation Pipeline

**Workflow:**
```
Webhook Input (ZIP code from form)
    ↓
Get Properties
    ↓
Filter (High Score + Low Days on Market)
    ↓
Generate Lead Report
    ↓
Store in CRM
    ↓
Send Email to Agent
```

---

## API Endpoint Reference for n8n

### Get Properties
```
Method: GET
URL: http://localhost:8000/properties
Query Parameters:
  - zip_code: 78704
  - timezone: America/Chicago
  - use_sample: false
  - force_refresh: false
```

### Get Top Property
```
Method: GET
URL: http://localhost:8000/properties/{{ $json.zip_code }}/top
Query Parameters:
  - timezone: America/Chicago
```

### Filter Properties
```
Method: GET
URL: http://localhost:8000/properties/{{ $json.zip_code }}/filter
Query Parameters:
  - min_price: 250000
  - max_price: 500000
  - min_bedrooms: 2
  - min_score: 75
  - timezone: America/Chicago
```

### Get Statistics
```
Method: GET
URL: http://localhost:8000/properties/{{ $json.zip_code }}/stats
Query Parameters:
  - timezone: America/Chicago
```

---

## Common n8n Expressions

### Extract Property Details
```
{{ $json.properties[0].address }}
{{ $json.properties[0].price }}
{{ $json.properties[0].investment_score }}
```

### Loop Through Properties
```
{{ $json.properties.map(p => ({
  address: p.address,
  score: p.investment_score,
  price: p.price
})) }}
```

### Format Price
```
{{ '$' + $json.price.toLocaleString() }}
```

### Calculate Average Score
```
{{ ($json.properties.reduce((a, p) => a + p.investment_score, 0) / $json.properties.length).toFixed(1) }}
```

### Format Timestamp with Timezone
```
{{ $json.timestamp }}
```

---

## Authentication

### No Authentication (Default)
The API runs without authentication by default.

### Optional: Add API Key Authentication

**API Side (add to app.py):**
```python
from fastapi import Header, HTTPException

@app.get("/properties")
async def get_properties(
    zip_code: str,
    x_api_key: str = Header(None)
):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code
```

**n8n Side:**
1. In HTTP Request node, go to **Authentication**
2. Select **"Generic Credential Type"**
3. Add custom header:
   - **Name:** `x-api-key`
   - **Value:** Your API key

---

## Error Handling

### Add Error Handler Node

1. Click on HTTP Request node
2. Add **"Error Workflow"** output
3. Connect to notification node

**Example Error Handler Code:**
```javascript
return {
  error: input.item.json.error,
  timestamp: new Date().toISOString(),
  workflow: "Real Estate Search"
};
```

---

## Webhook Integration

### Receive ZIP Code from External Source

1. Add **"Webhook"** node at start
2. Set URL: `http://your-n8n-instance/webhook/properties-search`
3. Configure body mapping:

**Webhook expects:**
```json
{
  "zip_code": "78704",
  "timezone": "America/Chicago"
}
```

---

## Testing

### Manual Test in n8n

1. Click **"Test workflow"**
2. Manually provide input:
```json
{
  "zip_code": "78704"
}
```
3. Verify HTTP request completes
4. Check output data
5. Execute full workflow

---

## Monitoring & Logging

### Enable Detailed Logging

1. In HTTP Request node, enable **"Full Response Data"**
2. In workflow settings, enable **"Save Data"**
3. Monitor execution history

### View API Response
```
{{ JSON.stringify($json, null, 2) }}
```

---

## Performance Optimization

### Batch Processing Multiple ZIP Codes

```javascript
const zipCodes = ["78704", "78701", "78702"];
return zipCodes.map(zip => ({
  json: {
    zip_code: zip,
    timezone: "America/Chicago"
  }
}));
```

**Then:**
1. Add "Loop" node
2. Set batch size

### Caching in n8n

Store results in memory:
```javascript
// Save to execution data
this.saveContextData("properties_" + $json.zip_code, $json);

// Retrieve later
const cached = this.getContextData("properties_" + $json.zip_code);
```

---

## Scheduling & Automation

### Time-Based Triggers

**Daily Search:**
- Cron: `0 9 * * *` (9 AM daily)
- Timezone: America/Chicago

**Weekly Comparison:**
- Cron: `0 8 ? * MON` (8 AM Monday)

**Every 6 Hours:**
- Cron: `0 */6 * * *`

### Event-Based Triggers

- Webhook from external system
- Form submission
- Database change
- Email received

---

## Deployment

### Local Development
```bash
# Start API
python app.py

# API runs on http://localhost:8000

# Start n8n
n8n start

# n8n runs on http://localhost:5678
```

### Production
```bash
# Using Docker
docker run -d -p 8000:8000 realestateapi:latest
docker run -d -p 5678:5678 n8nio/n8n:latest
```

### n8n Cloud
1. Create workflow in n8n cloud
2. Configure API URL: `https://your-api-domain.com`
3. Enable **"Save workflow to DB"** for persistence

---

## Troubleshooting

### API Connection Error
**Solution:**
1. Verify API is running: `http://localhost:8000/health`
2. Check firewall/network settings
3. Verify URL in HTTP Request node

### Empty Response
**Solution:**
1. Check ZIP code is valid
2. Verify use_sample parameter
3. Check API logs for errors

### Timeout Error
**Solution:**
1. Increase HTTP timeout in node settings
2. Check API performance
3. Add caching/results limiting

### Timezone Issues
**Solution:**
1. Specify timezone in query parameter
2. Verify timezone format (e.g., `America/Chicago`)
3. Test with `UTC` first

---

## Support Resources

- n8n Documentation: https://docs.n8n.io/
- Real Estate API Docs: `http://localhost:8000/docs`
- API Status: `http://localhost:8000/health`

