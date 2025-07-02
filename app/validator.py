# app/validator.py

import psycopg2
import sqlite3
from psycopg2 import sql as pg_sql
from typing import Dict, Any


def validate_sql(query: str, db_config: Dict[str, Any]) -> Dict:
    db_type = db_config.get("type", "postgresql").lower()

    if db_type == "postgresql":
        return validate_postgres_sql(query, db_config)
    elif db_type == "sqlite":
        return validate_sqlite_sql(query, db_config)
    else:
        return {
            "valid": False,
            "explain_output": [],
            "error": f"Unsupported database type: {db_type}"
        }


def validate_postgres_sql(query: str, config: Dict[str, Any]) -> Dict:
    try:
        conn = psycopg2.connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config.get("port", 5432)
        )
        cur = conn.cursor()
        cur.execute(pg_sql.SQL("EXPLAIN {}").format(pg_sql.SQL(query)))
        result = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "valid": True,
            "explain_output": [row[0] for row in result],
            "error": None
        }

    except Exception as e:
        return {
            "valid": False,
            "explain_output": [],
            "error": str(e)
        }


def validate_sqlite_sql(query: str, config: Dict[str, Any]) -> Dict:
    try:
        conn = sqlite3.connect(config["path"])
        cur = conn.cursor()
        cur.execute("EXPLAIN " + query)
        result = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "valid": True,
            "explain_output": [str(row) for row in result],
            "error": None
        }

    except Exception as e:
        return {
            "valid": False,
            "explain_output": [],
            "error": str(e)
        }
