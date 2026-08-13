"""Load the repository-local environment file for direct backend launches.

Process and container environment variables always win.  This keeps Compose and
production configuration explicit while making documented local commands use
the repository root `.env` consistently, regardless of the current directory.
"""

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)
