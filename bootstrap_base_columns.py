"""
bootstrap_base_columns.py
Run once at startup (or from a Flask CLI command) to
  • create the base_columns table if it doesn't exist
  • load / update rows from base_columns.json
"""
import json
from pathlib import Path

from sqlalchemy.orm import Session
from app.models import Base                         # the shared DeclarativeBase
from app.models.database_handler import DatabaseHandler
from app.models.base_column_model import BaseColumn

# ── 1. Ensure the table exists ──────────────────────────────────────────────
engine = DatabaseHandler().engine
Base.metadata.create_all(bind=engine, checkfirst=True)

# ── 2. Load JSON and upsert rows, preserving order ─────────────────────────
json_path = Path(__file__).with_name("base_columns.json")
data = json.loads(json_path.read_text(encoding="utf-8"))["base_columns"]

db: Session = DatabaseHandler().session
try:
    for position, (k, v) in enumerate(data.items(), start=1):
        db.merge(
            BaseColumn(
                key=k,
                name=v["name"],
                dtype=v["dtype"],
                length=v.get("length"),
                decimals=v.get("decimals"),
                order=position,              # 💡 the new ordering column
            )
        )
    db.commit()
    
# check if the table has been populated
    if db.query(BaseColumn).count() == 0:
        raise ValueError("No base columns were created. Check your JSON file.")
    print(f"Base columns successfully loaded from {json_path}")
finally:
    db.close()
