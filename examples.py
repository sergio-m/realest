"""
Examples demonstrating how to use the Real Estate Data API.
Run the API first with: python app.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Example 1: Get all properties in a ZIP code
print("=" * 60)
print("Example 1: Get all properties in a ZIP code")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/properties",
    params={
        "zip_code": "78704",
        "timezone": "America/Chicago"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['count']} properties in {data['zip_code']}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Timezone: {data['timezone']}\n")
    
    # Show first property
    if data['properties']:
        prop = data['properties'][0]
        print(f"First property:")
        print(f"  Address: {prop['address']}")
        print(f"  Price: ${prop['price']:,}")
        print(f"  Bedrooms: {prop['bedrooms']}")
        print(f"  Investment Score: {prop['investment_score']}/100\n")
else:
    print(f"Error: {response.status_code}")

# Example 2: Get top property by investment score
print("=" * 60)
print("Example 2: Get top property by investment score")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/properties/78704/top",
    params={"timezone": "America/New_York"}
)

if response.status_code == 200:
    data = response.json()
    prop = data['property']
    print(f"Top property found at: {data['timestamp']}")
    print(f"Address: {prop['address']}")
    print(f"Price: ${prop['price']:,}")
    print(f"Investment Score: {prop['investment_score']}/100")
    print(f"  - Price Score: {prop['price_score']}")
    print(f"  - Location Score: {prop['location_score']}")
    print(f"  - Market Trend Score: {prop['market_trend_score']}")
    print(f"  - Amenity Score: {prop['amenity_score']}")
    print(f"Nearest Starbucks: {prop['nearest_starbucks_distance']} miles\n")
else:
    print(f"Error: {response.status_code}")

# Example 3: Filter properties by criteria
print("=" * 60)
print("Example 3: Filter properties by criteria")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/properties/78704/filter",
    params={
        "min_price": 300000,
        "max_price": 500000,
        "min_bedrooms": 2,
        "min_score": 75,
        "timezone": "America/Chicago"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Filtered results: {data['count']} properties match criteria")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Criteria:")
    print(f"  Price: $300,000 - $500,000")
    print(f"  Min Bedrooms: 2")
    print(f"  Min Investment Score: 75\n")
    
    # Show filtered properties
    for prop in data['properties'][:3]:  # Show first 3
        print(f"  - {prop['address']}: ${prop['price']:,} ({prop['investment_score']}/100)")
    print()
else:
    print(f"Error: {response.status_code}")

# Example 4: Get statistics for a ZIP code
print("=" * 60)
print("Example 4: Get statistics for a ZIP code")
print("=" * 60)

response = requests.get(
    f"{BASE_URL}/properties/78704/stats",
    params={"timezone": "America/Chicago"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Statistics for ZIP {data['zip_code']}")
    print(f"Total Properties: {data['total_properties']}")
    print(f"\nPrice Statistics:")
    print(f"  Average: ${data['price']['average']:,.2f}")
    print(f"  Range: ${data['price']['min']:,} - ${data['price']['max']:,}")
    print(f"\nInvestment Score Statistics:")
    print(f"  Average: {data['investment_score']['average']}/100")
    print(f"  Range: {data['investment_score']['min']} - {data['investment_score']['max']}")
    print(f"\nBedroom Statistics:")
    print(f"  Average: {data['bedrooms']['average']}")
    print(f"  Range: {int(data['bedrooms']['min'])} - {int(data['bedrooms']['max'])}")
    print(f"\nSquare Footage Statistics:")
    print(f"  Average: {data['square_feet']['average']:,.0f} sqft")
    print(f"  Range: {int(data['square_feet']['min'])} - {int(data['square_feet']['max'])} sqft\n")
else:
    print(f"Error: {response.status_code}")

# Example 5: Using different timezones
print("=" * 60)
print("Example 5: Same data with different timezones")
print("=" * 60)

timezones = ["UTC", "America/Chicago", "America/Los_Angeles", "Europe/London"]

for tz in timezones:
    response = requests.get(
        f"{BASE_URL}/properties/78704/stats",
        params={"timezone": tz}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Timezone: {data['timezone']}")
        print(f"Timestamp: {data['timestamp']}\n")

# Example 6: Health check
print("=" * 60)
print("Example 6: Health check")
print("=" * 60)

response = requests.get(f"{BASE_URL}/health")
if response.status_code == 200:
    data = response.json()
    print(f"API Status: {data['status']}")
    print(f"Service: {data['service']}\n")
else:
    print(f"API is not responding")

# Example 7: Using with multiple ZIP codes (for n8n workflow)
print("=" * 60)
print("Example 7: Multiple ZIP code analysis")
print("=" * 60)

zip_codes = ["78704", "78701", "78702"]
comparison = {}

for zip_code in zip_codes:
    response = requests.get(
        f"{BASE_URL}/properties/{zip_code}/stats",
        params={"timezone": "America/Chicago"}
    )
    if response.status_code == 200:
        data = response.json()
        comparison[zip_code] = {
            "avg_price": data['price']['average'],
            "avg_score": data['investment_score']['average'],
            "total_properties": data['total_properties']
        }

print("Comparison of ZIP Codes:")
print(f"{'ZIP Code':<10} {'Avg Price':<15} {'Avg Score':<12} {'Properties':<12}")
print("-" * 50)
for zip_code, stats in comparison.items():
    print(f"{zip_code:<10} ${stats['avg_price']:>13,.0f} {stats['avg_score']:>11.1f} {stats['total_properties']:>11}")

print("\n" + "=" * 60)
print("All examples completed successfully!")
print("=" * 60)
