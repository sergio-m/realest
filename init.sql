-- SQL schema for real estate investment analysis app

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    price DECIMAL(12,2),
    square_feet INT,
    bedrooms INT,
    bathrooms DECIMAL(3,1),
    price_per_sqft DECIMAL(8,2),
    days_on_market INT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    property_type VARCHAR(50),
    year_built INT,
    lot_size DECIMAL(10,2),
    hoa_fees DECIMAL(8,2),
    property_tax DECIMAL(10,2),
    nearest_starbucks_distance DECIMAL(8,2),
    nearest_heb_distance DECIMAL(8,2),
    nearest_target_distance DECIMAL(8,2),
    investment_score DECIMAL(5,2),
    price_score DECIMAL(5,2) DEFAULT 0,
    location_score DECIMAL(5,2) DEFAULT 0,
    market_trend_score DECIMAL(5,2) DEFAULT 0,
    amenity_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS searches (
    id SERIAL PRIMARY KEY,
    zip_code VARCHAR(10) NOT NULL,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    properties_found INT DEFAULT 0,
    avg_price DECIMAL(12,2),
    avg_price_per_sqft DECIMAL(8,2)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_properties_zip_code ON properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_investment_score ON properties(investment_score DESC);