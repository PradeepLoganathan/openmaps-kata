import requests
import csv

# Overpass API URL for querying OpenStreetMap data
overpass_url = "http://overpass-api.de/api/interpreter"

# Query to fetch POIs (adjust as needed)
overpass_query = """
[out:json];
area["ISO3166-1"="US"][admin_level=2];
node["tourism"~"hotel|museum|attraction"](area);
out center;
"""

# Fetch POI data
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract relevant information
pois = []
for element in data['elements']:
    if element['type'] == 'node':
        poi = {
            'name': element.get('tags', {}).get('name', 'Unknown'),
            'latitude': element['lat'],
            'longitude': element['lon']
        }
        pois.append(poi)

# Write data to CSV
with open('pois.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'latitude', 'longitude']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for poi in pois:
        writer.writerow(poi)
