# app/template_repository.py

import json
import os
from typing import List, Dict, Any
from app.embedding import get_embedding
from app.similarity import cosine_similarity

TEMPLATE_FILE = "app/templates.json"

# Plantillas base
RAW_TEMPLATES = [
    {"id": "tpl_01", "template": "SELECT {{column}} FROM {{table}};"},
    {"id": "tpl_02", "template": "SELECT {{column}} FROM {{table}} WHERE {{column}} = {{value}};"},
    {"id": "tpl_03", "template": "SELECT AVG({{column}}) FROM {{table}};"},
    {"id": "tpl_04", "template": "SELECT {{column}} FROM {{table}} ORDER BY {{column}};"},
    {"id": "tpl_05", "template": "SELECT {{column}} FROM {{table}} LIMIT {{value}};"},
    {"id": "tpl_06", "template": "SELECT {{group_column}}, AVG({{column}}) FROM {{table}} GROUP BY {{group_column}};"},
    {"id": "tpl_07", "template": "SELECT {{group_column}}, AVG({{column}}) FROM {{table}} GROUP BY {{group_column}} HAVING AVG({{column}}) > {{value}};"},
    {"id": "tpl_08", "template": "SELECT {{column}} FROM {{table1}} JOIN {{table2}} ON {{table1}}.{{col1}} = {{table2}}.{{col2}};"},
    {"id": "tpl_09", "template": "SELECT COUNT({{column}}) FROM {{table}};"},
    {"id": "tpl_10", "template": "SELECT MAX({{column}}) FROM {{table}} WHERE {{column}} < {{value}};"}
]

async def generate_template_embeddings():
    templates_with_embeddings = []

    for tpl in RAW_TEMPLATES:
        embedding = await get_embedding(tpl["template"])
        templates_with_embeddings.append({
            "template_id": tpl["id"],
            "template": tpl["template"],
            "embedding": embedding
        })

    with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(templates_with_embeddings, f, indent=2)

    print(f"✅ Guardado en {TEMPLATE_FILE}")


def load_templates() -> List[Dict[str, Any]]:
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Archivo de plantillas no encontrado: {TEMPLATE_FILE}")
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_best_template(user_embedding: List[float], intent: Dict) -> Dict:
    templates = load_templates()
    best_tpl = None
    best_score = -1

    for tpl in templates:
        score = cosine_similarity(user_embedding, tpl["embedding"])
        if score > best_score:
            best_score = score
            best_tpl = tpl

    if best_tpl is None:
        return {"error": "No template matched."}

    return {
        "template_id": best_tpl["template_id"],
        "template": best_tpl["template"],
        "cosine_similarity": best_score
    }
