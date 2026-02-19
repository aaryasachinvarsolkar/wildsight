from sqlmodel import create_engine, inspect
import os

DB_PATH = os.path.join("backend", "wildsight.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL)

inspector = inspect(engine)
print("Tables:", inspector.get_table_names())

if "environmentalcache" in inspector.get_table_names():
    print("\nColumns in 'environmentalcache':")
    for col in inspector.get_columns("environmentalcache"):
        print(f" - {col['name']} ({col['type']})")
else:
    print("\nERROR: 'environmentalcache' table NOT found!")
