"""
Main Flask application for Real Estate Investment Analysis.
Provides web interface for searching and analyzing real estate properties.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import logging
from config import Config
from database import db_manager
from data_collector import data_collector
import folium
from folium import plugins
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    if not db_manager.connect():
        app.logger.error("❌ Could not connect to DB at startup")
    else:
        try:
            db_manager.create_tables()
        except Exception as e:
            app.logger.warning(f"⚠️ Table creation skipped/failed: {e}")
    
    # # Initialize database
    # if not db_manager.connect():
    #     logger.error("Failed to connect to database")
    #     return None
    
    # if not db_manager.create_tables():
    #     logger.error("Failed to create database tables")
    #     return None
    
    @app.route('/')
    def index():
        """Home page with search form."""
        return render_template('index.html')
    
    @app.route('/search', methods=['GET', 'POST'])
    def search_properties():
        """Search for properties by zip code."""
        # Redirect GET requests to home page
        if request.method == 'GET':
            return redirect(url_for('index'))
        zip_code = request.form.get('zip_code', '').strip()
        force_refresh = request.form.get('force_refresh', False)  # Optional checkbox
        
        if not zip_code:
            flash('Please enter a zip code', 'error')
            return redirect(url_for('index'))
        
        # Validate zip code format (basic validation)
        if not zip_code.isdigit() or len(zip_code) != 5:
            flash('Please enter a valid 5-digit zip code', 'error')
            return redirect(url_for('index'))
        
        try:
            # Check for existing data first
            existing_properties = []
            search_message = ""
            
            if not force_refresh:
                # Check if we have data from today
                if db_manager.is_search_today(zip_code):
                    existing_properties = db_manager.get_properties_created_today(zip_code)
                    if existing_properties:
                        last_search = db_manager.get_last_search_info(zip_code)
                        search_time = last_search['search_date'].strftime('%I:%M %p') if last_search else 'earlier'
                        search_message = f"Using cached data from today ({search_time})"
                        flash(search_message, 'info')
            
            if not existing_properties:
                # Collect new data
                logger.info(f"Collecting fresh data for {zip_code}...")
                properties_data = data_collector.collect_real_estate_data(
                    zip_code, 
                    force_refresh=force_refresh
                )
                
                if not properties_data:
                    flash(f'No properties found for zip code {zip_code}', 'warning')
                    return render_template('no_results.html', zip_code=zip_code)
                
                # Clear old properties for this zip code (optional)
                # db_manager.clear_old_properties(zip_code)
                
                # Store properties in database
                for property_data in properties_data:
                    db_manager.insert_property(property_data)
                
                # Get the newly inserted properties
                properties = db_manager.get_properties_by_zip(zip_code)
                search_message = f"Fetched {len(properties)} fresh properties"
                flash(search_message, 'success')
            else:
                properties = existing_properties
            
            # Calculate market statistics
            market_stats = db_manager.get_market_stats(zip_code)
            
            # Record the search (only if it's a new search)
            if not existing_properties:
                db_manager.record_search(
                    zip_code,
                    len(properties),
                    market_stats.get('avg_price', 0),
                    market_stats.get('avg_price_per_sqft', 0)
                )
            
            return render_template('properties.html', 
                                properties=properties, 
                                zip_code=zip_code,
                                market_stats=market_stats,
                                search_message=search_message)
            
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            flash('An error occurred while searching for properties', 'error')
            return redirect(url_for('index'))
        
    @app.route('/property/<int:property_id>')
    def property_detail(property_id):
        """Show detailed information for a specific property."""
        try:
            property_data = db_manager.get_property_by_id(property_id)
            
            if not property_data:
                flash('Property not found', 'error')
                return redirect(url_for('index'))
            
            # Calculate mortgage information
            mortgage_info = calculate_mortgage_info(property_data)
            
            return render_template('property_detail.html', 
                                property=property_data,
                                mortgage_info=mortgage_info)
            
        except Exception as e:
            logger.error(f"Error retrieving property details: {e}")
            flash('An error occurred while retrieving property details', 'error')
            return redirect(url_for('index'))
    
    @app.route('/map/<zip_code>')
    def map_view(zip_code):
        """Display properties on an interactive map."""
        try:
            properties = db_manager.get_properties_by_zip(zip_code)
            
            if not properties:
                flash(f'No properties found for zip code {zip_code}', 'warning')
                return redirect(url_for('index'))
            

            # Filter only properties that have valid coordinates
            valid_props = [p for p in properties if p.get('latitude') and p.get('longitude')]

            if not valid_props:
                logger.error("No valid coordinates available for map")
                flash('No valid location data available for map view', 'error')
                return redirect(url_for('index'))

            # Use first valid property as map center
            lat = float(valid_props[0]['latitude'])
            lng = float(valid_props[0]['longitude'])

            
            # Create folium map
            property_map = folium.Map(
                location=[lat, lng],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Add markers for each property
            for prop in valid_props:
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>{prop['address']}</h4>
                    <p><strong>Price:</strong> ${prop['price']:,.0f}</p>
                    <p><strong>Sq Ft:</strong> {prop['square_feet']:,}</p>
                    <p><strong>Price/Sq Ft:</strong> ${prop['price_per_sqft']:.2f}</p>
                    <p><strong>Kobi Score:</strong> {prop['investment_score']:.1f}/100</p>
                    <a href="/property/{prop['id']}" target="_blank">View Details</a>
                </div>
                """
                
                # Color code markers based on investment score
                if prop['investment_score'] >= 70:
                    color = 'green'
                elif prop['investment_score'] >= 50:
                    color = 'orange'
                else:
                    color = 'red'
                
                folium.Marker(
                    location=[prop['latitude'], prop['longitude']],
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{prop['address']} - ${prop['price']:,.0f}",
                    icon=folium.Icon(color=color, icon='home')
                ).add_to(property_map)
            
            # Add a marker cluster for better performance with many properties
            marker_cluster = plugins.MarkerCluster().add_to(property_map)
            
            # Convert map to HTML
            map_html = property_map._repr_html_()
            
            return render_template('map.html', 
                                 map_html=map_html, 
                                 zip_code=zip_code,
                                 property_count=len(properties))
            
        except Exception as e:
            logger.error(f"Error creating map view: {e}")
            flash('An error occurred while creating the map', 'error')
            return redirect(url_for('index'))

    
    @app.route('/analytics/<zip_code>')
    def analytics(zip_code):
        """Display analytics and investment insights for a zip code."""
        try:
            properties = db_manager.get_properties_by_zip(zip_code)
            market_stats = db_manager.get_market_stats(zip_code)
            
            if not properties:
                flash(f'No properties found for zip code {zip_code}', 'warning')
                return redirect(url_for('index'))
            
            # Calculate additional analytics
            analytics_data = calculate_analytics(properties)
            
            return render_template('analytics.html',
                                 zip_code=zip_code,
                                 market_stats=market_stats,
                                 analytics=analytics_data,
                                 properties=properties)
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            flash('An error occurred while generating analytics', 'error')
            return redirect(url_for('index'))
    
    @app.route('/api/properties/<zip_code>')
    def api_properties(zip_code):
        """API endpoint to get properties data as JSON."""
        try:
            properties = db_manager.get_properties_by_zip(zip_code)
            
            # Convert to JSON-serializable format
            properties_json = []
            for prop in properties:
                prop_dict = dict(prop)
                # Convert Decimal objects to float
                for key, value in prop_dict.items():
                    if hasattr(value, '__float__'):
                        prop_dict[key] = float(value)
                properties_json.append(prop_dict)
            
            return jsonify({
                'success': True,
                'properties': properties_json,
                'count': len(properties_json)
            })
            
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    return app

def calculate_mortgage_info(property_data):
    """Calculate mortgage payment information for a property."""
    price = float(property_data['price'])
    down_payment_percent = Config.DEFAULT_DOWN_PAYMENT_PERCENT
    interest_rate = Config.DEFAULT_INTEREST_RATE / 100
    loan_term_years = Config.DEFAULT_LOAN_TERM_YEARS
    
    down_payment = price * (down_payment_percent / 100)
    loan_amount = price - down_payment
    
    # Calculate monthly payment using mortgage formula
    monthly_rate = interest_rate / 12
    num_payments = loan_term_years * 12
    
    if monthly_rate > 0:
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / ((1 + monthly_rate) ** num_payments - 1)
    else:
        monthly_payment = loan_amount / num_payments
    
    # Estimate property tax and insurance
    annual_property_tax = float(property_data.get('property_tax', price * 0.015))
    annual_insurance = price * 0.005  # Estimate 0.5% of home value
    monthly_property_tax = annual_property_tax / 12
    monthly_insurance = annual_insurance / 12
    
    # HOA fees
    monthly_hoa = float(property_data.get('hoa_fees', 0))
    
    total_monthly_payment = monthly_payment + monthly_property_tax + monthly_insurance + monthly_hoa
    
    return {
        'price': price,
        'down_payment': down_payment,
        'loan_amount': loan_amount,
        'monthly_payment': monthly_payment,
        'monthly_property_tax': monthly_property_tax,
        'monthly_insurance': monthly_insurance,
        'monthly_hoa': monthly_hoa,
        'total_monthly_payment': total_monthly_payment,
        'interest_rate': Config.DEFAULT_INTEREST_RATE,
        'loan_term_years': loan_term_years
    }

def calculate_analytics(properties):
    """Calculate analytics data for a list of properties."""
    if not properties:
        return {}
    
    # Price distribution
    prices = [float(p['price']) for p in properties]
    price_ranges = {
        'under_200k': len([p for p in prices if p < 200000]),
        '200k_400k': len([p for p in prices if 200000 <= p < 400000]),
        '400k_600k': len([p for p in prices if 400000 <= p < 600000]),
        'over_600k': len([p for p in prices if p >= 600000])
    }
    
    # Property type distribution
    property_types = {}
    for prop in properties:
        prop_type = prop['property_type']
        property_types[prop_type] = property_types.get(prop_type, 0) + 1
    
    # Investment score distribution
    scores = [float(p['investment_score']) for p in properties]
    score_ranges = {
        'excellent': len([s for s in scores if s >= 80]),
        'good': len([s for s in scores if 60 <= s < 80]),
        'fair': len([s for s in scores if 40 <= s < 60]),
        'poor': len([s for s in scores if s < 40])
    }
    
    # Top 5 properties by investment score
    top_properties = sorted(properties, key=lambda x: float(x['investment_score']), reverse=True)[:5]
    
    return {
        'price_ranges': price_ranges,
        'property_types': property_types,
        'score_ranges': score_ranges,
        'top_properties': top_properties,
        'total_properties': len(properties)
    }

if __name__ == '__main__':
    app = create_app()
    if app:
        app.run(debug=True, host='0.0.0.0', port=5005)
    else:
        logger.error("Failed to create application")