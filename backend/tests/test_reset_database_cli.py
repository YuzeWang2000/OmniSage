import os
import sqlite3
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reset_database.py"


def run_reset(database: Path, data_dir: Path, *args: str, app_env: str = "test"):
    env = os.environ.copy()
    env.update(
        DATABASE_URL=f"sqlite:///{database}",
        DATA_DIR=str(data_dir),
        APP_ENV=app_env,
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=SCRIPT.parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def table_names(database: Path) -> set[str]:
    with sqlite3.connect(database) as connection:
        return {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def test_reset_dry_run_does_not_modify_database(tmp_path):
    database = tmp_path / "dry-run.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sentinel(value TEXT)")
    result = run_reset(database, tmp_path, "--dry-run")
    assert result.returncode == 0
    assert table_names(database) == {"sentinel"}


def test_sqlite_backup_reset_and_restore(tmp_path):
    database = tmp_path / "restore.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sentinel(value TEXT)")
        connection.execute("INSERT INTO sentinel VALUES ('preserved')")
    reset = run_reset(database, tmp_path, "--database-only", "--backup", "--yes")
    assert reset.returncode == 0
    assert "provider_connections" in table_names(database)
    backup = next(tmp_path.glob("restore.*.bak"))
    restore = run_reset(database, tmp_path, "--restore-from", str(backup), "--yes")
    assert restore.returncode == 0
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT value FROM sentinel").fetchone() == ("preserved",)


def test_production_reset_requires_verified_backup_and_confirmation(tmp_path):
    database = tmp_path / "production.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sentinel(value TEXT)")
    result = run_reset(database, tmp_path, "--database-only", "--yes", app_env="production")
    assert result.returncode == 2
    assert "Production reset requires" in result.stderr
    assert table_names(database) == {"sentinel"}
