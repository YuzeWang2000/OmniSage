"""Explicit, guarded database reset tool. File data is opt-in and path checked."""
from __future__ import annotations

import argparse
import sqlite3
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import settings
from app.database import Base, engine
from app import models as _models  # noqa: F401  Ensures SQLAlchemy metadata is populated.


BACKEND = Path(__file__).resolve().parents[1]
WORKSPACE = BACKEND.parent.resolve()
CONTROLLED = {
    "uploads": Path(settings.UPLOAD_DIR).resolve(),
    "vector": Path(settings.VECTOR_DB_PATH).resolve(),
    "wiki": (Path(settings.DATA_DIR) / "wiki_data").resolve(),
}


def safe_data_path(path: Path) -> Path:
    resolved = path.resolve()
    forbidden = {Path(resolved.anchor), Path.home().resolve(), WORKSPACE, BACKEND}
    if resolved in forbidden or not resolved.is_relative_to(Path(settings.DATA_DIR).resolve()):
        raise ValueError(f"unsafe data path: {resolved}")
    return resolved


def sqlite_path() -> Path | None:
    if engine.url.get_backend_name() != "sqlite" or not engine.url.database:
        return None
    path = Path(engine.url.database)
    return (BACKEND / path).resolve() if not path.is_absolute() else path.resolve()


def verified_sqlite_backup(path: Path) -> bool:
    try:
        with sqlite3.connect(path) as connection:
            return connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    except (OSError, sqlite3.DatabaseError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--database-only", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--restore-from", type=Path)
    parser.add_argument("--include-vector-data", action="store_true")
    parser.add_argument("--include-uploads", action="store_true")
    parser.add_argument("--include-wiki", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--production-confirm", action="store_true")
    args = parser.parse_args(argv)
    db_file = sqlite_path()
    if args.restore_from:
        source = args.restore_from.resolve()
        if db_file is None:
            print("--restore-from is only implemented for SQLite", file=sys.stderr); return 2
        if not args.yes:
            print("Refusing restore without --yes", file=sys.stderr); return 2
        if source.parent != db_file.parent or source == db_file or not source.is_file():
            print("Refusing restore from an untrusted backup path", file=sys.stderr); return 2
        if not verified_sqlite_backup(source):
            print("Refusing restore from an invalid SQLite backup", file=sys.stderr); return 2
        if settings.APP_ENV == "production" and not args.production_confirm:
            print("Production restore requires --production-confirm", file=sys.stderr); return 2
        db_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, db_file)
        print(f"SQLite database restored from: {source}"); return 0
    targets = ["known SQLAlchemy tables"]
    for flag, key in ((args.include_vector_data,"vector"),(args.include_uploads,"uploads"),(args.include_wiki,"wiki")):
        if flag: targets.append(str(safe_data_path(CONTROLLED[key])))
    print("Targets:"); [print(f"- {target}") for target in targets]
    if args.dry_run or not any((args.database_only,args.include_vector_data,args.include_uploads,args.include_wiki)):
        print("Dry run: no changes made"); return 0
    if not args.yes:
        if not sys.stdin.isatty(): print("Refusing reset without --yes", file=sys.stderr); return 2
        if input("Type RESET to continue: ") != "RESET": return 2
    backup = None
    if settings.APP_ENV == "production" and not (args.production_confirm and args.backup):
        print("Production reset requires --backup and --production-confirm", file=sys.stderr); return 2
    if args.backup and db_file is None:
        print("--backup is only implemented for SQLite; use mysqldump and verify it before MySQL reset", file=sys.stderr)
        return 2
    if args.backup and db_file and db_file.exists():
        backup = db_file.with_suffix(f".{datetime.now():%Y%m%d%H%M%S}.bak")
        shutil.copy2(db_file, backup)
        if not verified_sqlite_backup(backup):
            print("Backup integrity verification failed; reset aborted", file=sys.stderr); return 2
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    for flag,key in ((args.include_vector_data,"vector"),(args.include_uploads,"uploads"),(args.include_wiki,"wiki")):
        target=safe_data_path(CONTROLLED[key])
        if flag and target.exists(): shutil.rmtree(target)
    print("Database reset complete"); print(f"Backup: {backup or 'none'}"); return 0


if __name__ == "__main__": raise SystemExit(main())
