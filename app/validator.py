# app/validator.py

import psycopg2
from psycopg2 import sql, OperationalError

def validate_sql(query: str, db_config: dict) -> dict:
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Construimos una consulta segura con EXPLAIN
        cur.execute(sql.SQL("EXPLAIN {}").format(sql.SQL(query)))
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
