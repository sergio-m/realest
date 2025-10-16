"""
Database management module for the Real Estate Investment Analysis application.
Handles database connections, table creation, and data operations.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, date
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and CRUD operations."""

    def __init__(self, database_url=None):
        self.database_url = database_url or Config.DATABASE_URL
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to DB: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logger.info("Connection closed")

    def create_tables(self):
        try:
            cur = self.connection.cursor()
            with open("init.sql", "r") as f:
                cur.execute(f.read())
            self.connection.commit()
            logger.info("Tables created successfully (or already exist)")
        except psycopg2.errors.DuplicateTable:
            # Don’t crash if tables exist already
            self.connection.rollback()
            logger.info("Tables already exist – skipping")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
        finally:
            cur.close()

    def insert_property(self, data):
        """Insert property data into DB."""
        try:
            cur = self.connection.cursor()
            query = """
                INSERT INTO properties (
                    address, zip_code, price, square_feet, bedrooms, bathrooms,
                    price_per_sqft, days_on_market, latitude, longitude,
                    property_type, year_built, lot_size, hoa_fees, property_tax,
                    nearest_starbucks_distance, nearest_heb_distance,
                    nearest_target_distance, investment_score,
                    price_score, location_score, market_trend_score, amenity_score
                ) VALUES (
                    %(address)s, %(zip_code)s, %(price)s, %(square_feet)s,
                    %(bedrooms)s, %(bathrooms)s, %(price_per_sqft)s,
                    %(days_on_market)s, %(latitude)s, %(longitude)s,
                    %(property_type)s, %(year_built)s, %(lot_size)s,
                    %(hoa_fees)s, %(property_tax)s, %(nearest_starbucks_distance)s,
                    %(nearest_heb_distance)s, %(nearest_target_distance)s,
                    %(investment_score)s, %(price_score)s, %(location_score)s,
                    %(market_trend_score)s, %(amenity_score)s
                ) RETURNING id;
            """
            cur.execute(query, data)
            pid = cur.fetchone()["id"]
            self.connection.commit()
            return pid
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            self.connection.rollback()
            return None
        finally:
            cur.close()

    def get_properties_by_zip(self, zip_code):
        try:
            cur = self.connection.cursor()
            cur.execute(
                "SELECT * FROM properties WHERE zip_code=%s ORDER BY investment_score DESC",
                (zip_code,)
            )
            return cur.fetchall()
        except Exception as e:
            logger.error(f"get_properties_by_zip failed: {e}")
            return []
        finally:
            cur.close()

    def get_property_by_id(self, pid):
        try:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM properties WHERE id=%s", (pid,))
            return cur.fetchone()
        except Exception as e:
            logger.error(f"get_property_by_id failed: {e}")
            return None
        finally:
            cur.close()

    def get_market_stats(self, zip_code):
        try:
            cur = self.connection.cursor()
            cur.execute("""
                SELECT COUNT(*) as total_properties,
                       AVG(price) as avg_price,
                       AVG(price_per_sqft) as avg_price_per_sqft,
                       AVG(days_on_market) as avg_days_on_market,
                       AVG(investment_score) as avg_investment_score
                FROM properties
                WHERE zip_code = %s;
            """, (zip_code,))
            return cur.fetchone()
        except Exception as e:
            logger.error(f"get_market_stats failed: {e}")
            return {}
        finally:
            cur.close()

    def record_search(self, zip_code, properties_found, avg_price, avg_price_per_sqft):
        """Record a search in the searches table."""
        try:
            cur = self.connection.cursor()
            
            insert_query = """
                INSERT INTO searches (zip_code, properties_found, avg_price, avg_price_per_sqft)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            
            cur.execute(insert_query, (zip_code, properties_found, avg_price, avg_price_per_sqft))
            search_id = cur.fetchone()['id']
            self.connection.commit()
            
            logger.info(f"Search recorded with ID: {search_id}")
            return search_id
            
        except Exception as e:
            logger.error(f"Error recording search: {e}")
            self.connection.rollback()
            return None
        finally:
            cur.close()

    def _ensure_connection(self):
        """Ensure DB connection is alive, reconnect if needed."""
        if self.connection is None or self.connection.closed != 0:
            self.connect()

    def check_recent_search(self, zip_code, hours_threshold=24):
        """Check if there's a recent search for this zip code within the threshold."""
        try:
            self._ensure_connection()
            cur = self.connection.cursor()
            
            query = """
                SELECT id, search_date, properties_found 
                FROM searches 
                WHERE zip_code = %s 
                AND search_date >= NOW() - INTERVAL '%s hours'
                ORDER BY search_date DESC 
                LIMIT 1
            """
            
            cur.execute(query, (zip_code, hours_threshold))
            recent_search = cur.fetchone()
            
            if recent_search:
                logger.info(f"Found recent search for {zip_code} from {recent_search['search_date']}")
                return recent_search
            else:
                logger.info(f"No recent search found for {zip_code} within {hours_threshold} hours")
                return None
                
        except Exception as e:
            logger.error(f"Error checking recent search: {e}")
            return None
        finally:
            cur.close()

    def is_search_today(self, zip_code):
        """Check if there's already a search for this zip code today."""
        cur = None
        try:
            self._ensure_connection()
            cur = self.connection.cursor()
            
            query = """
                SELECT COUNT(*) as search_count
                FROM searches 
                WHERE zip_code = %s 
                AND DATE(search_date) = CURRENT_DATE
            """
            
            cur.execute(query, (zip_code,))
            result = cur.fetchone()
            
            search_count = result['search_count'] if result else 0
            
            if search_count > 0:
                logger.info(f"Found {search_count} search(es) for {zip_code} today")
                return True
            else:
                logger.info(f"No searches found for {zip_code} today")
                return False
                
        except Exception as e:
            logger.error(f"Error checking today's searches: {e}")
            return False
        finally:
            cur.close()

    def get_last_search_info(self, zip_code):
        """Get information about the last search for a zip code."""
        try:
            cur = self.connection.cursor()
            
            query = """
                SELECT search_date, properties_found, avg_price, avg_price_per_sqft
                FROM searches 
                WHERE zip_code = %s 
                ORDER BY search_date DESC 
                LIMIT 1
            """
            
            cur.execute(query, (zip_code,))
            return cur.fetchone()
                
        except Exception as e:
            logger.error(f"Error getting last search info: {e}")
            return None
        finally:
            cur.close()

    def clear_old_properties(self, zip_code):
        """Clear old properties for a zip code before inserting new ones."""
        try:
            cur = self.connection.cursor()
            
            # Delete properties older than today for this zip code
            delete_query = """
                DELETE FROM properties 
                WHERE zip_code = %s 
                AND DATE(created_at) < CURRENT_DATE
            """
            
            cur.execute(delete_query, (zip_code,))
            deleted_count = cur.rowcount
            self.connection.commit()
            
            logger.info(f"Cleared {deleted_count} old properties for zip code {zip_code}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing old properties: {e}")
            self.connection.rollback()
            return 0
        finally:
            cur.close()

    def get_properties_created_today(self, zip_code):
        """Get properties that were created today for a specific zip code."""
        try:
            cur = self.connection.cursor()
            
            query = """
                SELECT * FROM properties 
                WHERE zip_code = %s 
                AND DATE(created_at) = CURRENT_DATE
                ORDER BY investment_score DESC
            """
            
            cur.execute(query, (zip_code,))
            properties = cur.fetchall()
            
            logger.info(f"Found {len(properties)} properties created today for zip code {zip_code}")
            return properties
                
        except Exception as e:
            logger.error(f"Error getting today's properties: {e}")
            return []
        finally:
            cur.close()

db_manager = DatabaseManager()