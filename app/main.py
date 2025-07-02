# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.parser import parse_intent  # 👈 Importamos el parser
from app.embedding import get_embedding  # 👈 Importamos la función de embedding

app = FastAPI(title="SQL Sketcher API")

class QueryRequest(BaseModel):
    query: str
    db_id: Optional[str] = None  # Preparado para usar Spider

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    intent = await parse_intent(request.query)

    try:
        embedding = await get_embedding(request.query)
    except Exception as e:
        embedding = {"error": str(e)}

    return {
        "status": "parsed",
        "input": request.query,
        "intent": intent,
        "embedding": embedding
    }

