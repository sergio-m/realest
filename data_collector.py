"""
Data collection module for real estate properties and nearby amenities.
Collects data from Zillow API and calculates investment metrics.
"""

import requests
import random
import time
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from config import Config
from database import db_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealEstateDataCollector:
    """Collects real estate data and nearby amenities information."""
    
    def __init__(self):
        """Initialize the data collector with API configurations."""
        self.google_api_key = Config.GOOGLE_PLACES_API_KEY
        self.zillow_api_key = Config.ZILLOW_API_KEY
        self.zillow_host = Config.ZILLOW_API_HOST
        self.geolocator = Nominatim(user_agent="realestate_analyzer")

        # Log API key status
        if self.google_api_key:
            logger.info(f"Google Places API key loaded: {self.google_api_key[:10]}...")
        else:
            logger.warning("Google Places API key not configured - will use sample distances")

        # Zillow API configuration
        self.zillow_base_url = f"https://{self.zillow_host}/propertyExtendedSearch"
        self.zillow_headers = {
            "X-RapidAPI-Key": self.zillow_api_key,
            "X-RapidAPI-Host": self.zillow_host
        } 

    def get_zip_code_coordinates(self, zip_code):
        """Get latitude and longitude for a zip code."""
        try:
            location = self.geolocator.geocode(f"{zip_code}, USA")
            if location:
                return location.latitude, location.longitude
            return None, None
        except Exception as e:
            logger.error(f"Error geocoding zip code {zip_code}: {e}")
            return None, None
    
    def find_nearby_places(self, lat, lng, place_type, radius=5000):
        """Find nearby places using Google Places API."""
        if not self.google_api_key:
            logger.warning("Google Places API key not configured")
            return []
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': place_type,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Error finding nearby {place_type}: {e}")
            return []
    
    def calculate_distance_to_nearest(self, property_lat, property_lng, places):
        """Calculate distance to the nearest place from a list of places."""
        if not places:
            return None
        
        min_distance = float('inf')
        property_coords = (property_lat, property_lng)
        
        for place in places:
            place_coords = (
                place['geometry']['location']['lat'],
                place['geometry']['location']['lng']
            )
            distance = geodesic(property_coords, place_coords).miles
            min_distance = min(min_distance, distance)
        
        return round(min_distance, 2) if min_distance != float('inf') else None
    
    def fetch_zillow_properties(self, zip_code, max_results=50):
        """Fetch properties from Zillow API."""
        if not self.zillow_api_key:
            logger.warning("Zillow API key not configured, falling back to sample data")
            return self.generate_sample_properties(zip_code)
        
        try:
            logger.info(f"Fetching properties from Zillow API for zip code: {zip_code}")
            
            # Zillow API parameters
            params = {
                "location": zip_code,
                "status_type": "ForSale",
                "home_type": "Houses,Townhomes,Condos",
                "sort": "Price_High_Low",
                "page": "1"
            }
            
            response = requests.get(
                self.zillow_base_url,
                headers=self.zillow_headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_zillow_response(data, zip_code)
            else:
                logger.error(f"Zillow API error: {response.status_code} - {response.text}")
                logger.info("Falling back to sample data")
                return self.generate_sample_properties(zip_code)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling Zillow API: {e}")
            logger.info("Falling back to sample data")
            return self.generate_sample_properties(zip_code)
        except Exception as e:
            logger.error(f"Unexpected error calling Zillow API: {e}")
            logger.info("Falling back to sample data")
            return self.generate_sample_properties(zip_code)
    
    def parse_zillow_response(self, zillow_data, zip_code):
        """Parse Zillow API response and convert to our property format."""
        properties = []
        
        # Handle different possible response structures
        results = []
        if 'props' in zillow_data:
            results = zillow_data['props']
        elif 'results' in zillow_data:
            results = zillow_data['results']
        elif isinstance(zillow_data, list):
            results = zillow_data
        
        logger.info(f"Processing {len(results)} properties from Zillow")
        
        for prop in results:
            try:
                # Extract basic property information
                property_data = self.extract_property_data(prop, zip_code)
                
                if property_data:
                    # Get nearby amenities
                    property_data = self.add_amenity_distances(property_data)
                    
                    # Calculate investment score
                    property_data['investment_score'] = self.calculate_investment_score(property_data)
                    
                    properties.append(property_data)
                    
            except Exception as e:
                logger.warning(f"Error processing property: {e}")
                continue
        
        logger.info(f"Successfully processed {len(properties)} properties")
        return properties
    
    def extract_property_data(self, prop, zip_code):
        """Extract property data from Zillow property object."""
        try:
            # Handle different possible field names in Zillow response
            address = (prop.get('address') or 
                      prop.get('streetAddress') or 
                      prop.get('full_address') or 
                      'Address Not Available')
            
            price = (prop.get('price') or 
                    prop.get('list_price') or 
                    prop.get('zestimate') or 0)
            
            # Convert price string to number if needed
            if isinstance(price, str):
                price = int(''.join(filter(str.isdigit, price))) if price else 0
            
            square_feet = (prop.get('livingArea') or 
                          prop.get('sqft') or 
                          prop.get('square_feet') or 
                          random.randint(800, 3000))  # fallback
            
            bedrooms = (prop.get('bedrooms') or 
                       prop.get('beds') or 
                       random.randint(1, 4))  # fallback
            
            bathrooms = (prop.get('bathrooms') or 
                        prop.get('baths') or 
                        random.choice([1, 1.5, 2, 2.5, 3]))  # fallback
            
            # Get coordinates
            latitude = prop.get('latitude') or prop.get('lat')
            longitude = prop.get('longitude') or prop.get('lng') or prop.get('lon')
            
            # If no coordinates, try to geocode the address
            if not latitude or not longitude:
                try:
                    location = self.geolocator.geocode(f"{address}, {zip_code}")
                    if location:
                        latitude = location.latitude
                        longitude = location.longitude
                except:
                    # Use zip code center as fallback
                    zip_lat, zip_lng = self.get_zip_code_coordinates(zip_code)
                    latitude = zip_lat + random.uniform(-0.02, 0.02) if zip_lat else None
                    longitude = zip_lng + random.uniform(-0.02, 0.02) if zip_lng else None
            
            # Calculate price per square foot
            price_per_sqft = round(price / square_feet, 2) if square_feet > 0 else 0
            
            # Extract other fields with fallbacks
            property_type = (prop.get('propertyType') or 
                           prop.get('home_type') or 
                           random.choice(['Single Family', 'Townhouse', 'Condo']))
            
            year_built = (prop.get('yearBuilt') or 
                         prop.get('year_built') or 
                         random.randint(1960, 2023))
            
            days_on_market = (prop.get('daysOnZillow') or 
                             prop.get('days_on_market') or 
                             random.randint(1, 120))
            
            lot_size = (prop.get('lotAreaValue') or 
                       prop.get('lot_size') or 
                       round(random.uniform(0.1, 1.5), 2))
            
            # Estimate HOA and property tax if not provided
            hoa_fees = (prop.get('hoaFee') or 
                       random.choice([0, 0, 50, 100, 150, 200]))
            
            property_tax = (prop.get('taxAnnualAmount') or 
                           int(price * 0.015))  # Estimate 1.5% of home value
            
            return {
                'address': address,
                'zip_code': zip_code,
                'price': price,
                'square_feet': square_feet,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'price_per_sqft': price_per_sqft,
                'days_on_market': days_on_market,
                'latitude': latitude,
                'longitude': longitude,
                'property_type': property_type,
                'year_built': year_built,
                'lot_size': lot_size,
                'hoa_fees': hoa_fees,
                'property_tax': property_tax
            }
            
        except Exception as e:
            logger.error(f"Error extracting property data: {e}")
            return None
    
    def add_amenity_distances(self, property_data):
        """Add distances to nearby amenities."""
        lat = property_data.get('latitude')
        lng = property_data.get('longitude')
        
        if not lat or not lng:
            # Use sample distances if no coordinates
            property_data.update({
                'nearest_starbucks_distance': round(random.uniform(0.5, 10), 2),
                'nearest_heb_distance': round(random.uniform(1, 15), 2),
                'nearest_target_distance': round(random.uniform(2, 20), 2)
            })
            return property_data
        
        try:
            if self.google_api_key:
                # Find nearby Starbucks
                starbucks = self.find_nearby_places(lat, lng, "cafe", 5000)
                starbucks_distance = self.calculate_distance_to_nearest(lat, lng, starbucks)
                
                # Find nearby grocery stores (HEB equivalent)
                grocery_stores = self.find_nearby_places(lat, lng, "grocery_or_supermarket", 10000)
                heb_distance = self.calculate_distance_to_nearest(lat, lng, grocery_stores)
                
                # Find nearby department stores (Target equivalent)
                department_stores = self.find_nearby_places(lat, lng, "department_store", 10000)
                target_distance = self.calculate_distance_to_nearest(lat, lng, department_stores)
            else:
                # Generate sample distances
                starbucks_distance = round(random.uniform(0.5, 10), 2)
                heb_distance = round(random.uniform(1, 15), 2)
                target_distance = round(random.uniform(2, 20), 2)
            
            property_data.update({
                'nearest_starbucks_distance': starbucks_distance,
                'nearest_heb_distance': heb_distance,
                'nearest_target_distance': target_distance
            })
            
        except Exception as e:
            logger.error(f"Error calculating amenity distances: {e}")
            # Use sample distances as fallback
            property_data.update({
                'nearest_starbucks_distance': round(random.uniform(0.5, 10), 2),
                'nearest_heb_distance': round(random.uniform(1, 15), 2),
                'nearest_target_distance': round(random.uniform(2, 20), 2)
            })
        
        return property_data
    
    def calculate_investment_score(self, property_data):
        """Calculate investment score based on various factors."""
        # Initialize component scores
        price_score = 0
        location_score = 0
        market_trend_score = 0
        amenity_score = 0

        # Price per square foot factor (lower is better) - Max 25 points
        price_per_sqft = property_data.get('price_per_sqft', 0)
        if price_per_sqft > 0:
            if price_per_sqft < 100:
                price_score = 25
            elif price_per_sqft < 150:
                price_score = 20
            elif price_per_sqft < 200:
                price_score = 15
            elif price_per_sqft < 250:
                price_score = 10
            else:
                price_score = 5

        # Days on market factor (fewer days is better) - Max 25 points
        # Applied a bell curve. Good score is recent in market and many days was well
        days_on_market = property_data.get('days_on_market', 0)
        if days_on_market > 0:
            if days_on_market < 30:
                market_trend_score = 25
            elif days_on_market < 60:
                market_trend_score = 10
            elif days_on_market < 90:
                market_trend_score = 15
            elif days_on_market < 120:
                market_trend_score = 20
            elif days_on_market < 180:
                market_trend_score = 25
            else:
                market_trend_score = 5

        # Nearby amenities factor - Max 25 points
        starbucks_distance = property_data.get('nearest_starbucks_distance')
        if starbucks_distance is not None:
            if starbucks_distance < 1:
                amenity_score += 10
            elif starbucks_distance < 2:
                amenity_score += 7
            elif starbucks_distance < 3:
                amenity_score += 5
            elif starbucks_distance < 5:
                amenity_score += 3

        heb_distance = property_data.get('nearest_heb_distance')
        if heb_distance is not None:
            if heb_distance < 2:
                amenity_score += 10
            elif heb_distance < 3:
                amenity_score += 7
            elif heb_distance < 5:
                amenity_score += 5
            elif heb_distance < 7:
                amenity_score += 3

        target_distance = property_data.get('nearest_target_distance')
        if target_distance is not None:
            if target_distance < 3:
                amenity_score += 5
            elif target_distance < 5:
                amenity_score += 3
            elif target_distance < 7:
                amenity_score += 2

        # Cap amenity score at 25
        amenity_score = min(25, amenity_score)

        # Property age factor (location score based on property condition) - Max 25 points
        year_built = property_data.get('year_built')
        if year_built:
            current_year = 2024
            age = current_year - year_built
            if age < 5:
                location_score = 25  # Brand new
            elif age < 10:
                location_score = 22
            elif age < 20:
                location_score = 18
            elif age < 30:
                location_score = 15
            elif age < 40:
                location_score = 12
            elif age < 50:
                location_score = 10
            else:
                location_score = 5
        else:
            location_score = 15  # Default if year not available

        # Calculate total score
        total_score = price_score + location_score + market_trend_score + amenity_score

        # Store component scores in property_data
        property_data['price_score'] = price_score
        property_data['location_score'] = location_score
        property_data['market_trend_score'] = market_trend_score
        property_data['amenity_score'] = amenity_score

        return max(0, min(100, total_score))  # Ensure score is between 0 and 100
    
    def generate_sample_properties(self, zip_code, count=20):
        """Generate sample property data for demonstration purposes."""
        logger.info(f"Generating {count} sample properties for zip code {zip_code}")
        
        # Get zip code coordinates
        zip_lat, zip_lng = self.get_zip_code_coordinates(zip_code)
        if not zip_lat or not zip_lng:
            logger.error(f"Could not geocode zip code {zip_code}")
            return []
        
        properties = []
        
        # Sample addresses and property types
        street_names = [
            "Main St", "Oak Ave", "Pine Dr", "Maple Ln", "Cedar Ct",
            "Elm St", "Park Ave", "First St", "Second St", "Third St",
            "Washington Ave", "Lincoln Dr", "Jefferson Blvd", "Madison St"
        ]
        
        property_types = ["Single Family", "Townhouse", "Condo", "Duplex"]
        
        for i in range(count):
            # Generate random coordinates near the zip code center
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            property_lat = zip_lat + lat_offset
            property_lng = zip_lng + lng_offset
            
            # Generate property details
            square_feet = random.randint(800, 4000)
            price = random.randint(150000, 800000)
            price_per_sqft = round(price / square_feet, 2)
            
            property_data = {
                'address': f"{random.randint(100, 9999)} {random.choice(street_names)}",
                'zip_code': zip_code,
                'price': price,
                'square_feet': square_feet,
                'bedrooms': random.randint(1, 5),
                'bathrooms': random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4]),
                'price_per_sqft': price_per_sqft,
                'days_on_market': random.randint(1, 200),
                'latitude': property_lat,
                'longitude': property_lng,
                'property_type': random.choice(property_types),
                'year_built': random.randint(1950, 2023),
                'lot_size': round(random.uniform(0.1, 2.0), 2),
                'hoa_fees': random.choice([0, 50, 100, 150, 200, 300]),
                'property_tax': random.randint(2000, 15000)
            }
            
            # Add amenity distances
            property_data = self.add_amenity_distances(property_data)
            
            # Calculate investment score
            property_data['investment_score'] = self.calculate_investment_score(property_data)
            
            properties.append(property_data)
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
        
        logger.info(f"Generated {len(properties)} properties")
        return properties
    
    def collect_real_estate_data(self, zip_code, use_sample_data=False, force_refresh=False):
        """
        Main method to collect real estate data for a zip code.
        
        Args:
            zip_code: The zip code to search
            use_sample_data: Force use of sample data instead of API
            force_refresh: Force API call even if data exists from today
        """
        logger.info(f"Starting data collection for zip code: {zip_code}")
        
        # Check if we should use cached data (unless force_refresh is True)
        if not force_refresh and not use_sample_data:
            # Check if we already have data from today
            if db_manager.is_search_today(zip_code):
                logger.info(f"Found existing search for {zip_code} today, using cached data")
                
                # Get properties from today
                cached_properties = db_manager.get_properties_created_today(zip_code)
                
                if cached_properties:
                    logger.info(f"Using {len(cached_properties)} cached properties from today")
                    return [dict(prop) for prop in cached_properties]
                else:
                    logger.warning("Search exists but no properties found, will fetch new data")
        
        # Proceed with fresh data collection
        if use_sample_data or not self.zillow_api_key:
            logger.info("Using sample data")
            properties = self.generate_sample_properties(zip_code)
        else:
            logger.info("Fetching fresh data from Zillow API")
            properties = self.fetch_zillow_properties(zip_code)
        
        logger.info(f"Data collection completed. Found {len(properties)} properties")
        return properties
    


# Global data collector instance
data_collector = RealEstateDataCollector()