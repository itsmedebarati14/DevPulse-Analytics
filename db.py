import sqlite3
import pandas as pd
import logging
from typing import Optional, Tuple, List, Any

from config import get_db_path


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# ============================================================
# Database Connection
# ============================================================

def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    """

    conn = sqlite3.connect(get_db_path())

    # Allows SQLite rows to be accessed by column name
    conn.row_factory = sqlite3.Row

    # Enable foreign-key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# Execute SQL Schema Script
# ============================================================

def execute_script(file_path: str) -> None:
    """
    Executes the complete SQLite SQL schema file.
    """

    conn = get_connection()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn.executescript(sql_script)
        conn.commit()

        logging.info(
            f"Successfully executed SQL script: {file_path}"
        )

    except Exception as e:
        conn.rollback()

        logging.error(
            f"Failed to execute SQL script {file_path}: {e}"
        )

        raise

    finally:
        conn.close()


# ============================================================
# Run SELECT Queries
# ============================================================

def run_query(
    sql: str,
    params: Optional[Tuple[Any, ...]] = None
) -> pd.DataFrame:
    """
    Executes a SQL query and returns the result as a Pandas DataFrame.
    """

    conn = get_connection()

    try:
        return pd.read_sql_query(
            sql,
            conn,
            params=params or ()
        )

    finally:
        conn.close()


# ============================================================
# Run INSERT / UPDATE / DELETE Queries
# ============================================================

def execute_query(
    sql: str,
    params: Optional[Tuple[Any, ...]] = None
) -> None:
    """
    Executes INSERT, UPDATE or DELETE SQL.
    """

    conn = get_connection()

    try:
        conn.execute(sql, params or ())
        conn.commit()

    except Exception as e:
        conn.rollback()
        logging.error(f"SQL execution failed: {e}")
        raise

    finally:
        conn.close()


# ============================================================
# Bulk Insert
# ============================================================

def bulk_insert(
    table: str,
    columns: List[str],
    rows: List[Tuple[Any, ...]],
    batch_size: int = 1000
) -> None:
    """
    Inserts records into SQLite in batches.
    """

    if not rows:
        return

    conn = get_connection()

    try:
        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join(columns)

        sql = (
            f"INSERT INTO {table} "
            f"({col_names}) "
            f"VALUES ({placeholders})"
        )

        for i in range(0, len(rows), batch_size):

            batch = rows[i:i + batch_size]

            conn.executemany(sql, batch)

        conn.commit()

        logging.info(
            f"Inserted {len(rows)} rows into {table}."
        )

    except Exception as e:

        conn.rollback()

        logging.error(
            f"Bulk insert failed for {table}: {e}"
        )

        raise

    finally:
        conn.close()


# ============================================================
# Check Whether Table Exists
# ============================================================

def table_exists(table_name: str) -> bool:
    """
    Checks whether a table exists in the SQLite database.
    """

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name=?
            """,
            (table_name,)
        )

        return cursor.fetchone() is not None

    finally:
        conn.close()


# ============================================================
# Get Database Statistics
# ============================================================

def get_table_count(table_name: str) -> int:
    """
    Returns the number of records in a table.
    """

    conn = get_connection()

    try:

        cursor = conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        )

        result = cursor.fetchone()

        return result[0] if result else 0

    finally:
        conn.close()