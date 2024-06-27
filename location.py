import requests
import psycopg2  # Import the PostgreSQL adapter

# Overpass API URL
overpass_url = "http://overpass-api.de/api/interpreter"

# Query to fetch Australian POIs (adjust categories as needed)
overpass_query = """
[out:json][timeout:25];
area["ISO3166-1"="AU"][admin_level=2];  // Filter by Australia
(
  node["amenity"~"school|hospital|restaurant|cafe|bar"](area);
  way["amenity"~"school|hospital|restaurant|cafe|bar"](area);
  relation["amenity"~"school|hospital|restaurant|cafe|bar"](area);
);
out center;
"""

# Fetch POI data
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract relevant information and prepare for Greenplum
pois = []
for element in data['elements']:
    if element['type'] == 'node':
        poi = {
            'name': element.get('tags', {}).get('name', ''),
            'type': element.get('tags', {}).get('amenity', ''),
            'latitude': element['lat'],
            'longitude': element['lon']
        }
        pois.append(poi)

# Greenplum connection parameters (replace with your actual credentials)
conn_string = "dbname=your_database user=your_user password=your_password host=your_host"

# Insert data into Greenplum (assuming you have a table named 'pois_australia')
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as cur:
        for poi in pois:
            cur.execute("INSERT INTO pois_australia (name, type, geom) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))", 
                        (poi['name'], poi['type'], poi['longitude'], poi['latitude']))  # Note: longitude comes before latitude in PostGIS
    conn.commit()
