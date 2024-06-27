import requests
import psycopg2

# Greenplum connection parameters
conn_string = "dbname=urban_insights user=gpadmin host=172.19.180.141"

# Overpass API URL
overpass_url = "http://overpass-api.de/api/interpreter"

# Function to fetch and insert POIs for a given area
def fetch_and_insert_pois(area_name, area_query):
    overpass_query = f"""
    [out:json][timeout:25];
    area[name="{area_name}"];
    (
      node["amenity"~"school|hospital|restaurant|cafe|bar"](area);
      way["amenity"~"school|hospital|restaurant|cafe|bar"](area);
      relation["amenity"~"school|hospital|restaurant|cafe|bar"](area);
    );
    out center;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cur:
            for element in data['elements']:
                if element['type'] == 'node':
                    name = element.get('tags', {}).get('name', '')
                    poi_type = element.get('tags', {}).get('amenity', '')
                    longitude = element['lon']
                    latitude = element['lat']
                    cur.execute("INSERT INTO pois (name, type, geom) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))", 
                                (name, poi_type, longitude, latitude))
                elif element['type'] == 'way':
                    name = element.get('tags', {}).get('name', '')
                    poi_type = element.get('tags', {}).get('amenity', '')
                    center = element['center']
                    longitude = center['lon']
                    latitude = center['lat']
                    cur.execute("INSERT INTO pois (name, type, geom) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))", 
                                (name, poi_type, longitude, latitude))
                elif element['type'] == 'relation':
                    name = element.get('tags', {}).get('name', '')
                    poi_type = element.get('tags', {}).get('amenity', '')
                    center = element['center']
                    longitude = center['lon']
                    latitude = center['lat']
                    cur.execute("INSERT INTO pois (name, type, geom) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))", 
                                (name, poi_type, longitude, latitude))
            conn.commit()

# List of cities to fetch data for
cities = [
    ("Brisbane", "Brisbane, Queensland, Australia"),
    ("Sydney", "Sydney, New South Wales, Australia"),
    # ...add more cities as needed
]

# Fetch and insert for each city
for city_name, area_query in cities:
    fetch_and_insert_pois(city_name, area_query)

print("POI data loaded successfully!")
