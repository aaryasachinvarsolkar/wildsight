from app.services.taxonomy import taxonomy_service

name = "Panthera tigris (Linnaeus, 1758)"
key, clean_name, meta = taxonomy_service.resolve_name(name)
print(f"Key: {key}")
print(f"Clean Name: {clean_name}")
print(f"Meta: {meta}")
