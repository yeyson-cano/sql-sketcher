# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.parser import parse_intent  # 👈 Importamos el parser

app = FastAPI(title="SQL Sketcher API")

class QueryRequest(BaseModel):
    query: str
    db_id: Optional[str] = None  # Preparado para usar Spider

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    # Llamada al parser de intención
    intent = await parse_intent(request.query)

    return {
        "status": "parsed",
        "input": request.query,
        "intent": intent
    }
