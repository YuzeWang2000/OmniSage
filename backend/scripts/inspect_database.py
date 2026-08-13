from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import inspect
from app.database import engine
for table in inspect(engine).get_table_names(): print(table)

