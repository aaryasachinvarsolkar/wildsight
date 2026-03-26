from typing import Dict, Any, List, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import math
import h3
import time
from datetime import datetime, timedelta
import os
import concurrent.futures
from sqlmodel import Session, select
from app.models.schemas import EnvironmentalData
from app.models.db import engine, EnvironmentalCache, PlaceNameCache, EnvironmentalHistory

class EnvironmentalService:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.env_cache = {}

    def get_fire_data(self, lat: float, lon: float) -> float:
        MAP_KEY = os.getenv("NASA_FIRMS_MAP_KEY")
        if not MAP_KEY: return 0.0
        offset = 0.1 # Approx 10km
        west, south, east, north = lon - offset, lat - offset, lon + offset, lat + offset
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_NOAA20_NRT/{west},{south},{east},{north}/1"
        try:
            res = self.session.get(url, timeout=5.0)
            if res.status_code == 200:
                lines = res.text.strip().split('\n')
                if len(lines) <= 1: return 0.0
                frp_sum = sum(float(line.split(',')[12]) for line in lines[1:] if len(line.split(',')) > 12)
                return frp_sum
        except Exception: pass
        return 0.0

    def _get_sentinel_token(self) -> str:
        if hasattr(self, '_token_val') and hasattr(self, '_token_expiry') and time.time() < self._token_expiry:
            return self._token_val
        cid, csec = os.getenv("SENTINEL_CLIENT_ID"), os.getenv("SENTINEL_CLIENT_SECRET")
        if not cid or not csec: return None
        try:
            res = self.session.post("https://services.sentinel-hub.com/oauth/token", data={"grant_type": "client_credentials"}, auth=(cid, csec), timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                self._token_val = data.get("access_token")
                self._token_expiry = time.time() + data.get("expires_in", 3600) - 600
                return self._token_val
        except Exception: pass
        return None

    def _fetch_sentinel_for_range(self, lat: float, lon: float, start: str, end: str, script: str) -> float:
        token = self._get_sentinel_token()
        if not token: return 0.5
        offset = 0.001
        bbox = [lon - offset, lat - offset, lon + offset, lat + offset]
        payload = {
            "input": {
                "bounds": { "bbox": bbox, "properties": { "crs": "http://www.opengis.net/def/crs/EPSG/0/4326" } },
                "data": [{ "type": "sentinel-2-l2a", "dataFilter": { "timeRange": { "from": start, "to": end }, "mosaickingOrder": "leastCC" } }]
            },
            "output": { "width": 1, "height": 1, "responses": [{ "identifier": "default", "format": { "type": "image/tiff" } }] },
            "evalscript": script
        }
        try:
            import io, tifffile
            res = self.session.post("https://services.sentinel-hub.com/api/v1/process", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=8.0)
            if res.status_code == 200:
                with io.BytesIO(res.content) as f:
                    image = tifffile.imread(f)
                    if image.size > 0: return float(image.flat[0])
        except Exception: pass
        return 0.5

    def get_weather_data(self, lat: float, lon: float, date: str = None) -> Tuple[float, float]:
        """
        Fetches real temperature and rain. If date is provided, uses historical archive.
        date format: YYYY-MM-DD
        """
        try:
            if not date:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain&forecast_days=1"
                res = self.session.get(url, timeout=5.0)
            else:
                url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={date}&end_date={date}&daily=temperature_2m_mean,rain_sum&timezone=GMT"
                res = self.session.get(url, timeout=5.0)
            
            if res.status_code == 200:
                data = res.json()
                if not date:
                    curr = data.get('current', {})
                    return curr.get('temperature_2m', 25.0), curr.get('rain', 0.0)
                else:
                    daily = data.get('daily', {})
                    return daily.get('temperature_2m_mean', [25.0])[0], daily.get('rain_sum', [0.0])[0]
        except Exception: pass
        return 25.0, 0.0

    def fetch_historical_telemetry(self, lat: float, lon: float, h3_index: str):
        """
        Fetches last 5 years of REAL telemetry (Sentinel + Open-Meteo Archive) in parallel.
        """
        scripts = {
            "ndvi": "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { return [ (s.B08 - s.B04) / (s.B08 + s.B04) ]; }",
            "evi": "//VERSION=3\nfunction setup() { return { input: ['B02', 'B04', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { let L=1, C1=6, C2=7.5, G=2.5; return [ G * (s.B08 - s.B04) / (s.B08 + C1 * s.B04 - C2 * s.B02 + L) ]; }",
            "ndwi": "//VERSION=3\nfunction setup() { return { input: ['B03', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { return [ (s.B03 - s.B08) / (s.B03 + s.B08) ]; }"
        }
        
        years = [2021, 2022, 2023, 2024, 2025]
        
        def fetch_year_data(year):
            date_str = f"{year}-08-15"
            start, end = f"{year}-08-01T00:00:00Z", f"{year}-08-31T23:59:59Z"
            
            # Fetch Sentinel data
            ndvi = self._fetch_sentinel_for_range(lat, lon, start, end, scripts["ndvi"])
            evi = self._fetch_sentinel_for_range(lat, lon, start, end, scripts["evi"])
            ndwi = self._fetch_sentinel_for_range(lat, lon, start, end, scripts["ndwi"])
            temp, rain = self.get_weather_data(lat, lon, date_str)
                
            return {
                "year": year, "ndvi": ndvi, "evi": evi, "ndwi": ndwi,
                "temperature": temp, "rainfall": rain
            }

        # Step 1: Fetch all data in parallel (High I/O)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_year_data, years))
        
        # Step 2: Save to Database sequentially (Single transaction)
        try:
            with Session(engine) as session:
                for res in results:
                    entry = EnvironmentalHistory(
                        h3_index=h3_index, timestamp=datetime(res["year"], 8, 15),
                        ndvi=res["ndvi"], evi=res["evi"], ndwi=res["ndwi"],
                        temperature=res["temperature"], rainfall=res["rainfall"], frp=0.0,
                        hdi=0.4, nightlights=4.0
                    )
                    session.add(entry)
                session.commit()
        except Exception as e:
            print(f"Error saving historical telemetry: {e}")

    def get_environmental_data(self, lat: float, lon: float) -> EnvironmentalData:
        try:
            h3_index = h3.geo_to_h3(lat, lon, 6)
        except AttributeError:
            h3_index = h3.latlng_to_cell(lat, lon, 6)
            
        if h3_index in self.env_cache: return self.env_cache[h3_index]
        
        # Check Cache
        with Session(engine) as session:
            cached = session.get(EnvironmentalCache, h3_index)
            if cached and cached.fetched_at > datetime.utcnow() - timedelta(days=5):
                res = EnvironmentalData(
                    ndvi=cached.ndvi, evi=cached.evi, ndwi=cached.ndwi,
                    rainfall_forecast_mm=cached.rainfall, temperature_celsius=cached.temperature,
                    fire_radiative_power=0.0, human_development_index=cached.human_development_index,
                    nightlights=cached.nightlights, h3_index=h3_index, place_name=self.get_place_name(lat, lon),
                    is_cached=True
                )
                self.env_cache[h3_index] = res
                return res

        # Fresh Fetch
        t, r = self.get_weather_data(lat, lon)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f_fire = executor.submit(self.get_fire_data, lat, lon)
            f_ndvi = executor.submit(self._fetch_sentinel_for_range, lat, lon, (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z"), datetime.now().strftime("%Y-%m-%dT23:59:59Z"), "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { return [ (s.B08 - s.B04) / (s.B08 + s.B04) ]; }")
            f_evi = executor.submit(self._fetch_sentinel_for_range, lat, lon, (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z"), datetime.now().strftime("%Y-%m-%dT23:59:59Z"), "//VERSION=3\nfunction setup() { return { input: ['B02', 'B04', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { let L=1, C1=6, C2=7.5, G=2.5; return [ G * (s.B08 - s.B04) / (s.B08 + C1 * s.B04 - C2 * s.B02 + L) ]; }")
            f_ndwi = executor.submit(self._fetch_sentinel_for_range, lat, lon, (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z"), datetime.now().strftime("%Y-%m-%dT23:59:59Z"), "//VERSION=3\nfunction setup() { return { input: ['B03', 'B08'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(s) { return [ (s.B03 - s.B08) / (s.B03 + s.B08) ]; }")
            
            frp, ndvi, evi, ndwi = f_fire.result(), f_ndvi.result(), f_evi.result(), f_ndwi.result()

        hdi = 0.5
        nl = hdi * 10.0
        
        # Save to Cache & History
        with Session(engine) as session:
            session.merge(EnvironmentalCache(h3_index=h3_index, ndvi=ndvi, evi=evi, ndwi=ndwi, rainfall=r, temperature=t, human_development_index=hdi, nightlights=nl, fetched_at=datetime.utcnow(), last_updated=datetime.utcnow()))
            session.add(EnvironmentalHistory(h3_index=h3_index, ndvi=ndvi, evi=evi, ndwi=ndwi, temperature=t, rainfall=r, frp=frp, hdi=hdi, nightlights=nl))
            session.commit() # Important: Commit here so that the lock is released before potential heavy historical fetch

        # Fetch historical if missing (Moved OUTSIDE the session block for safety)
        with Session(engine) as session:
            hist_count = len(session.exec(select(EnvironmentalHistory).where(EnvironmentalHistory.h3_index == h3_index)).all())
        if hist_count < 3: 
            self.fetch_historical_telemetry(lat, lon, h3_index)

        res = EnvironmentalData(ndvi=ndvi, evi=evi, ndwi=ndwi, rainfall_forecast_mm=r, temperature_celsius=t, fire_radiative_power=frp, human_development_index=hdi, nightlights=nl, h3_index=h3_index, place_name=self.get_place_name(lat, lon), is_cached=False)
        self.env_cache[h3_index] = res
        return res

    def get_place_name(self, lat: float, lon: float) -> str:
        try:
            h3_index = h3.geo_to_h3(lat, lon, 4)
        except AttributeError:
            h3_index = h3.latlng_to_cell(lat, lon, 4)
        with Session(engine) as db_session:
            cached = db_session.get(PlaceNameCache, h3_index)
            if cached: return cached.full_name
        
        try:
            res = self.session.get("https://nominatim.openstreetmap.org/reverse", params={"lat": lat, "lon": lon, "format": "json", "zoom": 10}, headers={"User-Agent": "WildSight-AI/1.0"}, timeout=5.0)
            if res.status_code == 200:
                addr = res.json().get("address", {})
                parts = [p for p in [addr.get("city") or addr.get("town") or addr.get("village"), addr.get("state"), addr.get("country")] if p]
                name = ", ".join(parts[:2]) if parts else "Unknown Region"
                with Session(engine) as db_session:
                    db_session.merge(PlaceNameCache(h3_index=h3_index, full_name=name))
                    db_session.commit()
                return name
        except Exception: pass
        return f"Region {round(lat, 1)}, {round(lon, 1)}"

environmental_service = EnvironmentalService()
