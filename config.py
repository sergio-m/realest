"""
Configuration settings for the Real Estate Investment Analysis application.
Contains database connection details, API keys, and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Main configuration class for the application."""

    # Database Configuration
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5433/realestate'
    )

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # API Configuration (using free APIs as much as possible)
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')

    # Application Settings
    PROPERTIES_PER_PAGE = 20
    MAX_SEARCH_RADIUS = 50  # miles

    # Investment Analysis Defaults
    DEFAULT_DOWN_PAYMENT_PERCENT = 20
    DEFAULT_INTEREST_RATE = 7.0
    DEFAULT_LOAN_TERM_YEARS = 30

    # Amenity search radius
    STARBUCKS_SEARCH_RADIUS = 5000  # meters
    HEB_SEARCH_RADIUS = 10000       # meters
    TARGET_SEARCH_RADIUS = 10000    # meters

    # Zillow API
    ZILLOW_API_KEY = os.getenv('ZILLOW_API_KEY', '')
    ZILLOW_API_HOST = os.getenv('ZILLOW_API_HOST', '')

    @staticmethod
    def init_app(app):
        """Placeholder for app-specific initialization."""
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}