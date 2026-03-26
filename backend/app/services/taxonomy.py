from typing import Dict, Any, Tuple
import requests
import concurrent.futures
from pathlib import Path
import json

class TaxonomyService:
    def __init__(self):
        self.resolve_cache = {}
        self.gbif_base_url = "https://api.gbif.org/v1"
        self.species_db = {}
        self._load_data()

    def _load_data(self):
        try:
            base_dir = Path(__file__).resolve().parent.parent
            data_path = base_dir / "data" / "species_niches.json"
            if data_path.exists():
                with open(data_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        self.species_db[item["species_name"].lower()] = item
        except Exception as e:
            print(f"Error loading species_niches.json: {e}")

    def resolve_name(self, species_name: str, depth: int = 0) -> Tuple[Any, str, Dict]:
        """
        Smart resolution pipeline for biological taxonomy using GBIF.
        """
        if depth > 3:
            return None, species_name, {}
            
        s_norm = species_name.lower().strip()
        if s_norm in self.resolve_cache and depth == 0:
            return self.resolve_cache[s_norm]

        # Hardcoded aliases for iconic species
        iconic_map = {
            "tiger": "Panthera tigris",
            "bengal tiger": "Panthera tigris tigris",
            "asian elephant": "Elephas maximus",
            "indian elephant": "Elephas maximus indicus",
            "elephant": "Elephas maximus",
            "great indian bustard": "Ardeotis nigriceps",
            "lion": "Panthera leo",
            "leopard": "Panthera pardus",
            "snow leopard": "Panthera uncia",
            "one-horned rhino": "Rhinoceros unicornis",
            "rhino": "Rhinoceros unicornis"
        }
        
        if s_norm in iconic_map:
             return self.resolve_name(iconic_map[s_norm], depth + 1)

        candidates = []
        
        # Backbone Match
        try:
            m_res = requests.get(f"{self.gbif_base_url}/species/match", params={"name": species_name, "strict": "false"}, timeout=3.0)
            match = m_res.json()
            if match.get("matchType") in ["EXACT", "FUZZY"] and match.get("confidence", 0) > 80:
                 match["key"] = match.get("usageKey")
                 candidates.append(match)
        except Exception: pass

        def fetch_gbif(query, vernacular=False):
            try:
                params = {"q": query, "limit": 20}
                if vernacular: params["qField"] = "VERNACULAR"
                res = requests.get(f"{self.gbif_base_url}/species/search", params=params, timeout=3.0)
                return res.json().get("results", [])
            except Exception: return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            f1 = executor.submit(fetch_gbif, species_name, True)
            f2 = executor.submit(fetch_gbif, species_name, False)
            f3 = executor.submit(fetch_gbif, f"{species_name} Mammal")
            candidates.extend(f1.result())
            candidates.extend(f2.result())
            candidates.extend(f3.result())

        best_can = None
        best_score = -1
        processed_keys = set()
        
        priority_classes = {359: 100, 212: 80, 358: 60, 131: 30} # Mammalia, Aves, Reptilia, Amphibia
        
        for cand in candidates:
            key = cand.get("key") or cand.get("usageKey")
            if not key or key in processed_keys: continue
            processed_keys.add(key)

            score = 0
            if cand.get("rank") == "SPECIES": score += 50
            elif cand.get("rank") == "GENUS": score += 20
            
            score += priority_classes.get(cand.get("classKey"), 0)
            if cand.get("taxonomicStatus") == "ACCEPTED": score += 10
            
            sc_name = cand.get("scientificName", "").lower()
            ver_name = cand.get("vernacularName", "").lower()
            if s_norm == ver_name or s_norm == sc_name: score += 100
            elif s_norm in ver_name or s_norm in sc_name: score += 20

            if score > best_score:
                best_score = score
                best_can = cand

        # Fallback: If no good match, try stripping author citations (e.g. "(Linnaeus, 1758)") and retry once
        if (not best_can or best_score < 50) and depth == 0:
            import re
            cleaned = re.sub(r'\s*\(.*?\)\s*', ' ', species_name).strip()
            # Also strip trailing years/authors like "L., 1758"
            cleaned = re.sub(r'\s+\w+\.?\s*,\s*\d{4}\s*$', '', cleaned).strip()
            if cleaned != species_name:
                return self.resolve_name(cleaned, depth + 1)

        if best_can and best_score > 0:
            clean_name = best_can.get("canonicalName") or best_can.get("scientificName") or species_name
            meta = {
                "kingdom": best_can.get("kingdom"),
                "class": best_can.get("class"),
                "phylum": best_can.get("phylum"),
                "order": best_can.get("order"),
                "family": best_can.get("family"),
                "genus": best_can.get("genus"),
                "scientificName": best_can.get("scientificName")
            }
            res = (best_can.get("key") or best_can.get("usageKey"), clean_name, meta)
            if depth == 0: self.resolve_cache[s_norm] = res
            return res
            
        return None, species_name, {}

taxonomy_service = TaxonomyService()
