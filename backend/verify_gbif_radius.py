from app.services.ingest_gbif import gbif_service

# Test coordinates (Bandipur National Park, India)
lat = 11.66
lon = 76.62

print(f"Testing GBIF radius search at {lat}, {lon}...")
species = gbif_service.fetch_species_near_location(lat, lon, radius_km=50)

print(f"Found {len(species)} species.")
for s in species[:5]:
    print(f"- {s['name']} at {s['lat']}, {s['lon']}")
