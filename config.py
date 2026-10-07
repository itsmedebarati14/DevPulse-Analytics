import os

# ============================================================
# DevPulse Analytics - SQLite Configuration
# ============================================================

# SQLite database file.
# It will be created automatically in the project folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "devpulse.db")

# Random seed for reproducible synthetic data
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))


def get_db_path() -> str:
    """
    Returns the absolute path of the SQLite database.
    """
    return DB_PATH