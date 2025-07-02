# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SQL Sketcher API")

class QueryRequest(BaseModel):
    query: str
    db_id: Optional[str] = None  # Usado para pruebas con el dataset Spider

@app.post("/generate-sql")
async def generate_sql(request: QueryRequest):
    # Por ahora es solo un prototipo que responde algo fijo
    return {
        "status": "ok",
        "input": request.query,
        "db": request.db_id,
        "sql": "SELECT * FROM dummy_table WHERE condition = true;"
    }
