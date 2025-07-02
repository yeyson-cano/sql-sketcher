# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.parser import parse_intent  # 👈 Importamos el parser
from app.embedding import get_embedding  # 👈 Importamos la función de embedding
from app.selector import select_best_template  # 👈 Importamos el selector de plantillas
from app.assembler import assemble_query  # 👈 Importamos el ensamblador de consultas

app = FastAPI(title="SQL Sketcher API")

class QueryRequest(BaseModel):
    query: str
    db_id: Optional[str] = None  # Preparado para usar Spider

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    intent = await parse_intent(request.query)
    embedding = await get_embedding(request.query)
    selected = select_best_template(embedding, intent)
    assembled = assemble_query(selected["template"], intent)

    return {
        "status": "parsed",
        "input": request.query,
        "intent": intent,
        "embedding_preview": embedding[:5],
        "selected_template": selected,
        "final_query": assembled["query"],
        "missing_fields": assembled["missing_fields"]
    }

