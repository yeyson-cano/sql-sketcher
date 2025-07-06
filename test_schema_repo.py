# test_schema_repo.py

from app.schema_repository import SchemaRepository
import pprint

# Cambia esto según tu entorno
db_type = "postgresql"  # o "sqlite"
db_config = {
    # Si usas PostgreSQL local con Laragon
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "",
    "dbname": "spider_test"
}

# Para SQLite, sería por ejemplo:
# db_type = "sqlite"
# db_config = {"path": "path/a/alguna/base.sqlite"}

repo = SchemaRepository(db_type, db_config)

print("Tablas encontradas:")
pprint.pprint(repo.get_tables())

print("\nColumnas por tabla:")
pprint.pprint(repo.get_schema_dict()["columns"])

print("\nLlaves foráneas:")
pprint.pprint(repo.get_foreign_keys())

repo.close()
