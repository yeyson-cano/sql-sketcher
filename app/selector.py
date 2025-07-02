import math
import random
from typing import List, Dict, Optional


# ---------- UTILIDAD: Cosine Similarity ----------

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


# ---------- SIMULACIÓN DE EMBEDDINGS ----------

def fake_embedding() -> List[float]:
    return [random.uniform(-0.05, 0.05) for _ in range(1536)]


# ---------- REPOSITORIO SIMULADO DE PLANTILLAS ----------

template_repository = [
    {
        "id": "tpl_01",
        "template": "SELECT {{column}} FROM {{table}} WHERE {{column}} > {{value}};",
        "embedding": fake_embedding(),
        "entity_count": 2,
    },
    {
        "id": "tpl_02",
        "template": "SELECT AVG({{column}}) FROM {{table}} GROUP BY {{group_column}};",
        "embedding": fake_embedding(),
        "entity_count": 3,
    },
    {
        "id": "tpl_03",
        "template": "SELECT {{column}} FROM {{table}};",
        "embedding": fake_embedding(),
        "entity_count": 1,
    },
]


# ---------- FUNCIÓN PRINCIPAL DE SELECCIÓN ----------

def select_best_template(
    user_embedding: List[float],
    intent: Dict,
    repository: Optional[List[Dict]] = None
) -> Dict:
    if repository is None:
        repository = template_repository

    results = []

    for tpl in repository:
        cos_sim = cosine_similarity(user_embedding, tpl["embedding"])
        entity_score = len(intent.get("columns", [])) + len(intent.get("conditions", []))
        entity_diff = abs(tpl["entity_count"] - entity_score)

        final_score = cos_sim * 0.7 + (1 - min(entity_diff / 5, 1)) * 0.3

        results.append({
            "template_id": tpl["id"],
            "template": tpl["template"],
            "cosine_similarity": cos_sim,
            "entity_diff": entity_diff,
            "final_score": final_score
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[0] if results else {"error": "No templates available."}
