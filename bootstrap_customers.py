"""
bootstrap_customers.py
Run once at startup (or from a Flask CLI command) to
  • create the customers table if it doesn't exist
  • load / update rows from customers.json
"""
import json
from pathlib import Path

from app.customers.services import save_config

dir_path = Path(__file__).with_name("customer_configs")
json_files = list(dir_path.glob("*.json"))
print(f"Found {len(json_files)} JSON files in {dir_path}")

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        print(f"Skipping {json_file}: expected a JSON object, got {type(data).__name__}")
        continue

    # Save the configuration to the database
    try:
        save_config(data)
        print(f"Inserted/Updated customer config: {data.get('name', 'Unnamed')} from {json_file}")
    except Exception as e:
        print(f"Error saving config for {data.get('name', 'Unnamed')}: {e}")