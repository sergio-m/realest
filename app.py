"""
FastAPI application for Real Estate Data Collector.
Provides REST API endpoints for property data with timezone support.
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import pytz
import logging

from data_collector import data_collector
from database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real Estate Data API",
    description="API for collecting and analyzing real estate properties and investment metrics",
    version="1.0.0"
)

# Add CORS middleware for n8n and other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    try:
        db_manager.connect()
        db_manager.create_tables()
        logger.info("Database initialized on startup")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    try:
        db_manager.disconnect()
        logger.info("Database connection closed on shutdown")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


class PropertyData(BaseModel):
    """Property data model with all details."""
    address: str = Field(..., description="Property address")
    zip_code: str = Field(..., description="ZIP code")
    price: int = Field(..., description="Property price in USD")
    square_feet: int = Field(..., description="Property square footage")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: float = Field(..., description="Number of bathrooms")
    price_per_sqft: float = Field(..., description="Price per square foot")
    days_on_market: int = Field(..., description="Days on market")
    latitude: float = Field(..., description="Property latitude")
    longitude: float = Field(..., description="Property longitude")
    property_type: str = Field(..., description="Type of property")
    year_built: int = Field(..., description="Year property was built")
    lot_size: float = Field(..., description="Lot size in acres")
    hoa_fees: float = Field(..., description="Monthly HOA fees")
    property_tax: int = Field(..., description="Annual property tax")
    nearest_starbucks_distance: Optional[float] = Field(None, description="Distance to nearest Starbucks in miles")
    nearest_heb_distance: Optional[float] = Field(None, description="Distance to nearest grocery store in miles")
    nearest_target_distance: Optional[float] = Field(None, description="Distance to nearest Target in miles")
    investment_score: float = Field(..., description="Investment score (0-100)")
    price_score: Optional[float] = Field(None, description="Price component score")
    location_score: Optional[float] = Field(None, description="Location component score")
    market_trend_score: Optional[float] = Field(None, description="Market trend component score")
    amenity_score: Optional[float] = Field(None, description="Amenity component score")


class PropertiesResponse(BaseModel):
    """Response model for property list."""
    zip_code: str = Field(..., description="ZIP code searched")
    count: int = Field(..., description="Number of properties returned")
    timestamp: str = Field(..., description="Timestamp with timezone")
    timezone: str = Field(..., description="Timezone of timestamp")
    properties: List[PropertyData] = Field(..., description="List of properties")


class SinglePropertyResponse(BaseModel):
    """Response model for single property."""
    property: PropertyData = Field(..., description="Property data")
    timestamp: str = Field(..., description="Timestamp with timezone")
    timezone: str = Field(..., description="Timezone of timestamp")


def get_timezone_aware_timestamp(tz_str: str = "UTC") -> tuple:
    """Get current timestamp with timezone info."""
    try:
        tz = pytz.timezone(tz_str)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.UTC
    
    now = datetime.now(tz)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)")
    return timestamp_str, tz_str


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Real Estate Data API"
    }


@app.get(
    "/properties",
    response_model=PropertiesResponse,
    tags=["Properties"],
    summary="Get properties by ZIP code",
    description="Fetch a list of properties for a given ZIP code with investment analysis"
)
async def get_properties(
    zip_code: str = Query(..., description="ZIP code to search (e.g., 78704)"),
    use_sample: bool = Query(False, description="Use sample data instead of live API"),
    force_refresh: bool = Query(False, description="Force refresh from API (ignore cache)"),
    timezone: str = Query("UTC", description="Timezone for timestamp (e.g., America/Chicago)")
):
    """
    Get properties for a ZIP code.
    
    **Parameters:**
    - `zip_code`: The ZIP code to search (required)
    - `use_sample`: Whether to use sample data (default: false)
    - `force_refresh`: Force API refresh, skip cache (default: false)
    - `timezone`: Timezone for response timestamp (default: UTC)
    
    **Returns:**
    - List of properties with investment scores and amenity distances
    - Timestamp with specified timezone
    """
    try:
        logger.info(f"Fetching properties for zip code: {zip_code}")
        properties = data_collector.collect_real_estate_data(
            zip_code,
            use_sample_data=use_sample,
            force_refresh=force_refresh
        )
        
        if not properties:
            raise HTTPException(
                status_code=404,
                detail=f"No properties found for ZIP code: {zip_code}"
            )
        
        timestamp, tz = get_timezone_aware_timestamp(timezone)
        
        return PropertiesResponse(
            zip_code=zip_code,
            count=len(properties),
            timestamp=timestamp,
            timezone=tz,
            properties=properties
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching properties: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching properties: {str(e)}"
        )


@app.get(
    "/properties/{zip_code}",
    response_model=PropertiesResponse,
    tags=["Properties"],
    summary="Get properties by ZIP code (path parameter)",
    description="Alternative endpoint to fetch properties using ZIP code as path parameter"
)
async def get_properties_by_zip(
    zip_code: str = Path(..., description="ZIP code to search"),
    timezone: str = Query("UTC", description="Timezone for timestamp")
):
    """
    Get properties using ZIP code as path parameter.
    Equivalent to GET /properties?zip_code=<zip_code>
    """
    return await get_properties(zip_code, timezone=timezone)


@app.get(
    "/properties/{zip_code}/top",
    response_model=SinglePropertyResponse,
    tags=["Properties"],
    summary="Get top property by investment score",
    description="Get the property with the highest investment score for a ZIP code"
)
async def get_top_property(
    zip_code: str = Path(..., description="ZIP code to search"),
    timezone: str = Query("UTC", description="Timezone for timestamp")
):
    """
    Get the property with the best investment score for a ZIP code.
    """
    """
    Get the property with the best investment score for a ZIP code.
    """
    try:
        properties = data_collector.collect_real_estate_data(zip_code)
        
        if not properties:
            raise HTTPException(
                status_code=404,
                detail=f"No properties found for ZIP code: {zip_code}"
            )
        
        top_property = max(properties, key=lambda x: x.get('investment_score', 0))
        timestamp, tz = get_timezone_aware_timestamp(timezone)
        
        return SinglePropertyResponse(
            property=top_property,
            timestamp=timestamp,
            timezone=tz
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching top property: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching top property: {str(e)}"
        )


@app.get(
    "/properties/{zip_code}/filter",
    response_model=PropertiesResponse,
    tags=["Properties"],
    summary="Filter properties by criteria",
    description="Get properties filtered by price, bedrooms, and other criteria"
)
async def filter_properties(
    zip_code: str = Path(..., description="ZIP code to search"),
    min_price: Optional[int] = Query(None, description="Minimum property price"),
    max_price: Optional[int] = Query(None, description="Maximum property price"),
    min_bedrooms: Optional[int] = Query(None, description="Minimum bedrooms"),
    max_bedrooms: Optional[int] = Query(None, description="Maximum bedrooms"),
    min_score: Optional[float] = Query(None, description="Minimum investment score (0-100)"),
    max_days_on_market: Optional[int] = Query(None, description="Maximum days on market"),
    timezone: str = Query("UTC", description="Timezone for timestamp")
):
    """
    Filter properties by various criteria.
    """
    try:
        properties = data_collector.collect_real_estate_data(zip_code)
        
        if not properties:
            raise HTTPException(
                status_code=404,
                detail=f"No properties found for ZIP code: {zip_code}"
            )
        
        # Apply filters
        filtered = properties
        if min_price:
            filtered = [p for p in filtered if p.get('price', 0) >= min_price]
        if max_price:
            filtered = [p for p in filtered if p.get('price', 0) <= max_price]
        if min_bedrooms:
            filtered = [p for p in filtered if p.get('bedrooms', 0) >= min_bedrooms]
        if max_bedrooms:
            filtered = [p for p in filtered if p.get('bedrooms', 0) <= max_bedrooms]
        if min_score:
            filtered = [p for p in filtered if p.get('investment_score', 0) >= min_score]
        if max_days_on_market:
            filtered = [p for p in filtered if p.get('days_on_market', 0) <= max_days_on_market]
        
        timestamp, tz = get_timezone_aware_timestamp(timezone)
        
        return PropertiesResponse(
            zip_code=zip_code,
            count=len(filtered),
            timestamp=timestamp,
            timezone=tz,
            properties=filtered
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering properties: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error filtering properties: {str(e)}"
        )


@app.get(
    "/properties/{zip_code}/stats",
    tags=["Statistics"],
    summary="Get statistics for properties in ZIP code",
    description="Get aggregate statistics for properties in a ZIP code"
)
async def get_stats(
    zip_code: str = Path(..., description="ZIP code to analyze"),
    timezone: str = Query("UTC", description="Timezone for timestamp")
):
    """
    Get statistics for all properties in a ZIP code.
    """
    """
    Get statistics for all properties in a ZIP code.
    """
    try:
        properties = data_collector.collect_real_estate_data(zip_code)
        
        if not properties:
            raise HTTPException(
                status_code=404,
                detail=f"No properties found for ZIP code: {zip_code}"
            )
        
        prices = [p.get('price', 0) for p in properties]
        scores = [p.get('investment_score', 0) for p in properties]
        bedrooms = [p.get('bedrooms', 0) for p in properties]
        sqfts = [p.get('square_feet', 0) for p in properties]
        
        timestamp, tz = get_timezone_aware_timestamp(timezone)
        
        return {
            "zip_code": zip_code,
            "total_properties": len(properties),
            "timestamp": timestamp,
            "timezone": tz,
            "price": {
                "average": round(sum(prices) / len(prices), 2) if prices else 0,
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
            },
            "investment_score": {
                "average": round(sum(scores) / len(scores), 2) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
            },
            "bedrooms": {
                "average": round(sum(bedrooms) / len(bedrooms), 2) if bedrooms else 0,
                "min": min(bedrooms) if bedrooms else 0,
                "max": max(bedrooms) if bedrooms else 0,
            },
            "square_feet": {
                "average": round(sum(sqfts) / len(sqfts), 2) if sqfts else 0,
                "min": min(sqfts) if sqfts else 0,
                "max": max(sqfts) if sqfts else 0,
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
