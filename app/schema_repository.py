import sqlite3
import psycopg2
from psycopg2 import sql as pg_sql
from typing import List, Dict, Union, Optional

class SchemaRepository:
    def __init__(self, db_type: str, db_config: dict):
        self.db_type = db_type.lower()
        self.db_config = db_config
        self.schema = {
            "tables": [],
            "columns": {},
            "foreign_keys": []
        }

        self.conn: Optional[Union[sqlite3.Connection, psycopg2.extensions.connection]] = None
        self._connect()
        self._load_schema()

    def _connect(self):
        if self.db_type == "sqlite":
            self.conn = sqlite3.connect(self.db_config["path"])
        elif self.db_type == "postgresql":
            self.conn = psycopg2.connect(**self.db_config)
        else:
            raise ValueError("Unsupported DB type: must be 'sqlite' or 'postgresql'.")

    def _load_schema(self):
        if self.db_type == "sqlite":
            self._load_sqlite_schema()
        elif self.db_type == "postgresql":
            self._load_postgres_schema()

    def _load_sqlite_schema(self):
        assert self.conn is not None
        cursor = self.conn.cursor()

        # Obtener tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.schema["tables"] = tables

        # Obtener columnas y claves foráneas
        for table in tables:
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns = cursor.fetchall()
            self.schema["columns"][table] = [col[1] for col in columns]

            cursor.execute(f"PRAGMA foreign_key_list('{table}')")
            fks = cursor.fetchall()
            for fk in fks:
                self.schema["foreign_keys"].append({
                    "from_table": table,
                    "from_column": fk[3],
                    "to_table": fk[2],
                    "to_column": fk[4]
                })

    def _load_postgres_schema(self):
        assert self.conn is not None
        cursor = self.conn.cursor()

        # Tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        self.schema["tables"] = tables

        # Columnas
        for table in tables:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """)
            cols = cursor.fetchall()
            self.schema["columns"][table] = [col[0] for col in cols]

        # Claves foráneas
        cursor.execute("""
            SELECT
                tc.table_name AS from_table,
                kcu.column_name AS from_column,
                ccu.table_name AS to_table,
                ccu.column_name AS to_column
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY';
        """)
        fks = cursor.fetchall()
        for row in fks:
            self.schema["foreign_keys"].append({
                "from_table": row[0],
                "from_column": row[1],
                "to_table": row[2],
                "to_column": row[3]
            })

    def get_tables(self) -> List[str]:
        return self.schema["tables"]

    def get_columns(self, table: str) -> List[str]:
        return self.schema["columns"].get(table, [])

    def get_foreign_keys(self) -> List[Dict[str, str]]:
        return self.schema["foreign_keys"]

    def get_schema_dict(self) -> Dict:
        return self.schema

    def get_db_info(self) -> Dict:
        """Devuelve info de conexión para pasar al validador"""
        return {
            "type": self.db_type,
            **self.db_config
        }

    def close(self):
        if self.conn:
            self.conn.close()

    # 👇 Métodos de clase añadidos
    @classmethod
    def from_postgres_config(cls, config: dict) -> "SchemaRepository":
        return cls(db_type="postgresql", db_config=config)

    @classmethod
    def from_sqlite_path(cls, path: str) -> "SchemaRepository":
        return cls(db_type="sqlite", db_config={"path": path})
