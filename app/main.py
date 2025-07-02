# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from app.parser import parse_intent
from app.embedding import get_embedding
from app.selector import select_best_template
from app.assembler import assemble_query
from app.complex_assembler import apply_complex_assembly
from app.validator import validate_sql
from app.schema_repository import SchemaRepository

# Configuración para base de datos (aquí: PostgreSQL, pero puede adaptarse)
db_config = {
    "dbname": "spider_test",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": 5432
}

app = FastAPI(title="SQL Sketcher API")

class QueryRequest(BaseModel):
    query: str
    db_id: Optional[str] = None  # Para usar con datasets como Spider

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    # 1. Recuperar esquema desde PostgreSQL
    schema_repo = SchemaRepository.from_postgres_config(db_config)
    schema_dict = schema_repo.get_schema_dict()["columns"]
    db_info = schema_repo.get_db_info()  # Incluye tipo (sqlite/postgresql) y config

    # 2. Parsear intención con ayuda del esquema
    intent = await parse_intent(request.query, schema=schema_dict)

    # 3. Obtener embedding semántico
    embedding = await get_embedding(request.query)

    # 4. Seleccionar plantilla base
    selected = select_best_template(embedding, intent)

    # 5. Ensamblar la estructura simple con placeholders
    assembled = assemble_query(selected["template"], intent)

    # 6. Agregar cláusulas JOIN, GROUP BY, etc.
    enriched = apply_complex_assembly(assembled["query"], intent, schema_repo)

    # 7. Validar sintaxis SQL con EXPLAIN
    validation_result = validate_sql(enriched["query"], db_info)

    # 8. Armar respuesta final
    return {
        "status": "parsed",
        "input": request.query,
        "intent": intent,
        "embedding_preview": embedding[:5],
        "selected_template": selected,
        "final_query": enriched["query"],
        "missing_fields": assembled["missing_fields"],
        "enrichment_notes": enriched["notes"],
        "validation": validation_result  # Aquí va el resultado del validador
    }
