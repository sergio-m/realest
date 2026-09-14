# Realest
Real Estate app that collects properties on sale and provides a rating.

## Features
- Search properties by ZIP code
- View property details with investment scores
- Calculate distances to nearby amenities (Starbucks, grocery stores, Target)
- Interactive Kobi Score breakdown showing how each property is rated
- Sortable, filterable property tables and analytics dashboard
- PostgreSQL database for data persistence
- Containerized deployment with Podman/Docker

## Prerequisites
- Podman or Docker with compose support
- Python 3.11+ (for local development)
- Google Places API key (optional, for real distance calculations)
- Zillow API key (optional, will use sample data if not provided)

## Setup

### 1. Environment Configuration
Copy the example environment file and configure your settings:

```bash
cp dot.env.example .env
```

Edit `.env` and fill in your actual values:

```bash
# Google Places API Key (for calculating distances to amenities)
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Zillow API Configuration (optional)
ZILLOW_API_KEY=your_zillow_api_key_here
ZILLOW_API_HOST=zillow-com1.p.rapidapi.com

# Database Configuration
POSTGRES_DB=realestate
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@postgres:5432/realestate

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=False
```

**Important:** `.env` is gitignored and should never be committed. Make sure to update the `POSTGRES_PASSWORD` in both the `POSTGRES_PASSWORD` and `DATABASE_URL` variables to match, and pick your own `SECRET_KEY` rather than using the placeholder.

### 2. Start the Application

Using the convenience script:
```bash
./run.sh
```

Or manually with podman-compose:
```bash
podman-compose -f podman-compose.yml up --build -d
```

### 3. Access the Application
Open your browser and navigate to:
```
http://localhost:5005
```

## Management Commands

### Check services status
```bash
podman-compose -f podman-compose.yml ps
```

### Check service environment variables
```bash
podman-compose -f podman-compose.yml exec web env
```

### View logs
```bash
# All services
podman-compose -f podman-compose.yml logs

# Web service only
podman-compose -f podman-compose.yml logs web

# Database service only
podman-compose -f podman-compose.yml logs postgres
```

### Stop services
```bash
podman-compose -f podman-compose.yml down
```

### Rebuild and restart
```bash
podman-compose -f podman-compose.yml down
podman-compose -f podman-compose.yml up --build -d
```

## API Keys

### Google Places API
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the "Places API"
4. Create credentials (API Key)
5. Copy the API key to your `.env` file

### Zillow API (Optional)
1. Go to [RapidAPI Zillow](https://rapidapi.com/s.mahmoud97/api/zillow-com1)
2. Subscribe to the API (free tier available)
3. Copy your API key to your `.env` file

**Note:** If you don't provide a Zillow API key, the application will generate sample property data for demonstration purposes.

## Database

The application uses PostgreSQL 17 for data persistence. The database is automatically initialized on first run with the required schema.

- **Host:** localhost
- **Port:** 5433 (mapped from container's 5432)
- **Database:** realestate
- **User:** postgres
- **Password:** Set in your `.env` file

## Kobi Score

The Kobi Score is an investment rating (0-100) made up of four components, each worth up to 25 points:

### Price Score (0-25 points)
Lower price per square foot scores higher:
- < $100/sqft: 25 points
- $100-150/sqft: 20 points
- $150-200/sqft: 15 points
- $200-250/sqft: 10 points
- $250+/sqft: 5 points

### Market Trend Score (0-25 points)
Based on days on market (bell-shaped curve — very fresh or long-stale listings score highest, mid-range listings score lowest):
- < 30 days: 25 points
- 30-60 days: 10 points
- 60-90 days: 15 points
- 90-120 days: 20 points
- 120-180 days: 25 points
- 180+ days: 5 points

### Amenity Score (0-25 points)
Based on distance to nearby amenities (capped at 25 total):
- Starbucks: up to 10 points
- HEB (grocery): up to 10 points
- Target: up to 5 points

### Location Score (0-25 points)
Based on property age:
- < 5 years: 25 points
- 5-10 years: 22 points
- 10-20 years: 18 points
- 20-30 years: 15 points
- 30-40 years: 12 points
- 40-50 years: 10 points
- 50+ years: 5 points

Hover over any Kobi Score to see the detailed breakdown!

## Development

### Local Development (without containers)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Project Structure
```
realest/
├── app.py                 # Flask application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and models
├── data_collector.py      # Property data collection logic
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── properties.html
│   └── property_detail.html
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── img/
├── podman-compose.yml     # Container orchestration
├── Dockerfile             # Container image definition
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in git)
```

## Troubleshooting

### Application won't start
- Check that ports 5005 and 5433 are not in use
- Verify your `.env` file is properly configured
- Check logs: `podman-compose -f podman-compose.yml logs`

### Database connection errors
- Ensure the password in `.env` matches in both `POSTGRES_PASSWORD` and `DATABASE_URL`
- Wait a few seconds for the database to fully initialize
- Check database logs: `podman-compose -f podman-compose.yml logs postgres`

### No properties showing up
- If using Zillow API, verify your API key is valid
- Check web service logs: `podman-compose -f podman-compose.yml logs web`
- The app will use sample data if the Zillow API is not configured

## License
MIT
