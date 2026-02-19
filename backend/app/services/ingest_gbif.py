import requests
import random
from typing import List, Tuple, Dict

GBIF_API_URL = "https://api.gbif.org/v1/occurrence/search"

class GBIFService:
    def fetch_species_occurrences(self, species_name: str, limit: int = 100) -> List[Tuple[float, float, str]]:
        """
        Fetches recent occurrences of a species.
        Returns List of (lat, lon, zone_id)
        """
        params = {
            "scientificName": species_name,
            "hasCoordinate": "true",
            "limit": limit,
            "year": "2020,2025" # Recent years only as requested
        }
        
        try:
            res = requests.get(GBIF_API_URL, params=params, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                
                points = []
                for r in results:
                    lat = r.get("decimalLatitude")
                    lon = r.get("decimalLongitude")
                    date = r.get("eventDate", "unknown")
                    if lat and lon:
                        points.append((float(lat), float(lon), f"zone_{date}"))
                
                print(f"GBIF: Found {len(points)} occurrences for {species_name}")
                return points
            else:
                print(f"GBIF API Error: {res.status_code}")
            
        except Exception as e:
            print(f"GBIF Error: {e}")
            
        return []

    def fetch_species_near_location(self, lat: float, lon: float, radius_km: int = 50, limit: int = 20) -> List[Dict]:
        """
        Fetches threatened species found near a location using a Bounding Box.
        GBIF API 'decimalLatitude' supports ranges like 'min,max'.
        """
        # 1 degree lat is approx 111km. 50km is approx 0.45 degrees.
        delta = 0.5 # Safety margin
        min_lat = max(-90, lat - delta)
        max_lat = min(90, lat + delta)
        min_lon = max(-180, lon - delta)
        max_lon = min(180, lon + delta)
        
        params = {
            "decimalLatitude": f"{min_lat},{max_lat}",
            "decimalLongitude": f"{min_lon},{max_lon}",
            "hasCoordinate": "true",
            "limit": limit * 2, # Fetch more to filter duplicates
            "year": "2022,2026"
        }
        
        try:
            res = requests.get(GBIF_API_URL, params=params, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                
                species_found = []
                seen = set()
                
                # Priority: Filter for animals first if possible, but for now just unique names
                for r in results:
                    s_name = r.get("scientificName")
                    
                    # Basic Cleanup: remove author names if possible, but keep simple
                    if s_name and s_name not in seen:
                        # Optional: filter out common low-value entries if needed
                        species_found.append({
                            "name": s_name,
                            "lat": r.get("decimalLatitude"),
                            "lon": r.get("decimalLongitude")
                        })
                        seen.add(s_name)
                        
                        if len(species_found) >= limit:
                            break
                            
                print(f"GBIF: Found {len(species_found)} unique species near {lat}, {lon}")
                return species_found
            else:
                print(f"GBIF API Error: {res.status_code}")
        except Exception as e:
            print(f"GBIF Radius Error: {e}")
            
        return []

gbif_service = GBIFService()
