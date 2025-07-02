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

# Configuración para base de datos (PostgreSQL por defecto)
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
    db_id: Optional[str] = None  # Preparado para compatibilidad futura

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    # 1. Cargar esquema de la base de datos
    schema_repo = SchemaRepository.from_postgres_config(db_config)
    schema_dict = schema_repo.get_schema_dict()["columns"]
    db_info = schema_repo.get_db_info()

    # 2. Extraer intención semántica con ayuda del esquema
    intent = await parse_intent(request.query, schema=schema_dict)

    # 3. Generar embedding de la consulta
    embedding = await get_embedding(request.query)

    # 4. Seleccionar plantilla ideal
    selected = select_best_template(embedding, intent)

    # 5. Ensamblar consulta parcial
    assembled = assemble_query(selected["template"], intent)

    # 6. Refinar placeholders incompletos con ayuda del LLM
    enriched = await apply_complex_assembly(
        assembled["query"],
        intent,
        request.query,
        schema_repo
    )

    # 7. Validación sintáctica usando PostgreSQL (EXPLAIN)
    validation_result = validate_sql(enriched["query"], db_info)

    # 8. Respuesta final
    return {
        "status": "parsed",
        "input": request.query,
        "intent": intent,
        "embedding_preview": embedding[:5],
        "selected_template": selected,
        "final_query": enriched["query"],
        "missing_fields": assembled["missing_fields"],
        "enrichment_notes": enriched["notes"],
        "validation": validation_result
    }
