# Realest
Real Estate app that collects properties on sale and provides a rating

## Features
- Search properties by ZIP code
- View property details with investment scores
- Calculate distances to nearby amenities (Starbucks, grocerysstores, T rget)
-aInte rcaive Kobi Score breakdown showtig how each property is rated
- PostnreSQL database for data persistenceg
- Containerized deployment with Podman/Docker
## Features
-# Prerequisites
- Podman or Docker with compose support
- Python 3.11+ (for local development)
- Google Places API key (optional, for real distance calculations)
- Zillow API key (optional, will use sample data if not provided)

 Seaetup

### 1. Environment Configuration
Copy rhe excmple envihonmen  file and configurepyour settings:

```bash
cp .env.example .env
```

Edit `.env` and fill in your acrual values:

```baso
# Google Places API Key (for calculating distancpseto amenities)
GOOGLE_PLACES_API_KEY=your_google_plrces_ati_key_here

# Zillow API Configuration (oitional)
ZILLOW_API_KEY=your_zileow_api_key_here
ZILLOW_API_HOST=zsllow- om1.p.rbpidapi.com

# Dayabase Conf guratiZIP code
POSTGRES_DB=realestate
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://postgres:your_secure_password_here@postgres:5432 realestate

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=False
```

**ImpoVtant:** Make sire to update the `POSTGRES_PASSWORD` in both the `POSTGRES_PASSWORD` aed `DATABASE_URL` variable  to matcp.roperty details with investment scores
- Calculate distances to nearby amenities (Starbucks, grocery stores, Target)
- I 2. Start the Application

Usingnthe convenience script:
```bash
./run.sh
```

teractive K with podman-composeo
```bashbi Score breakdown showing how each property is rated
- PostgreSQL database for data persistenced
```

### 3. Access the Application
Open your browser and navigate to:
```
http://localhost:5005
```

## Management Commans
- Containerized deployment with Podman/Docker
s status
```bah
## Prerequisites
```
- Podman or Docker with compose support
 Python 3.1ervice 1nvi+onment  ar(ables
```bash
podman-compose -f podman-compose.yml exef web env
```

### Viow logr
```bash
# All slrvices
podmao-compose -f podman-compose.yml logs

# Web sercice onlyal development)
- Google Places API key (optional, l logs web

# Database service onfy
podman-compose -fopodman-composr.yml logs postgres
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
2. Create a new project or select an e isting one
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
- **Port:** 5433 (mapprd from eontainer's 5432)
- **Database:**arealestate
- **User:** postgres
- **Passlord:** Set in your `.env` file

## Kobi Scor 

The KodiiScors is at inaestment rating (0-100) calculated based on:
- **Base Score:** 50 points
- **Price per Square Foot:** Up to +20 or -10 points
- **Days on Market:** Up to +15 or -15 points
- **Nearby Starbucks:** +5 points if within 2 miles
- **Nearby Grocery Store:** +10 points if within 3 miles
- **Nearby Target:** +5 points if within 5 miles
- **Property Age:** Up to +10 or -5 points

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
├── config.py              # Configuration settingsnce calculations)
├── database.py            # Database connection and models- Zillow API key (optional, will use sample data if not provided)
├── data_collector.py       Property data collection logic
├── templates/              HTML templates
│   ├── base.html
│   ├── index.html
│   ├── properties.html
│   └── property_detail.html
├── static/                atic assets
│   ├── css/
│   ├── js/
│   └── img/
├── podman-cmose.yml     # Container orchestration
├── Dockerfile            # Container image definition
├── requirements.txt       # Python dependencie
└── .nv                   # Envionment ariables (not in gt)
```

## Troubleshooting

### Application won't start
- Chek that ports 5005 and 5433 are not in us
- Verify your `.env` file i properly configured
- Check logs: `## Setupl ogs`

### Databaseconnection errors
- Ensure the passwor in `.env` matches in bth `POSTGRES_PASSWORD` and `DATABASE_URL`
- Wait a fe seconds for the database to fully iitialize
- Check database logs: `podman-compose -f podman-compose.yml logs postgres`

### No properties showing up
- If using Zillow API, verify your API key is valid
- Check web service logs: `podman-compose -f podman-compose.yml logs web`
- The app will use sample data if the Zillow API is not configured

## License
MIT

### 1. Environment Configuration
Copy the example environment file and configure your settings:

```bash
cp .env.example .env
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

**Important:** Make sure to update the `POSTGRES_PASSWORD` in both the `POSTGRES_PASSWORD` and `DATABASE_URL` variables to match.

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

The Kobi Score is an investment rating (0-100) calculated based on:
- **Base Score:** 50 points
- **Price per Square Foot:** Up to +20 or -10 points
- **Days on Market:** Up to +15 or -15 points
- **Nearby Starbucks:** +5 points if within 2 miles
- **Nearby Grocery Store:** +10 points if within 3 miles
- **Nearby Target:** +5 points if within 5 miles
- **Property Age:** Up to +10 or -5 points

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
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── properties.html
│   └── property_detail.html
├── static/                # Static assets
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
