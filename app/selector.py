from typing import List, Dict, Optional, Any
import json
import os
import math

# ------------------ UTILS ------------------

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

# ------------------ CARGA DE PLANTILLAS ------------------

def load_template_repository(template_path: str = "app/templates.json") -> List[Dict[str, Any]]:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found at: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------------ CÁLCULO DE PUNTAJE ------------------

def count_matching_entities(template_str: str, intent: Dict) -> int:
    score = 0
    if "{{table}}" in template_str and intent.get("tables"):
        score += 1
    if "{{column}}" in template_str and intent.get("columns"):
        score += 1
    if "{{value}}" in template_str and intent.get("conditions"):
        score += 1
    if "{{group_column}}" in template_str and intent.get("group_by"):
        score += 1
    return score

# ------------------ SELECCIÓN DE PLANTILLA ------------------

def select_best_template(
    user_embedding: List[float],
    intent: Dict,
    repository: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    repo = repository if repository is not None else load_template_repository()

    results = []

    for tpl in repo:
        cos_sim = cosine_similarity(user_embedding, tpl["embedding"])
        match_score = count_matching_entities(tpl["template"], intent)

        # Puntaje final: mezcla de coseno (70%) y coincidencia de entidades (30%)
        final_score = cos_sim * 0.7 + (match_score / 4) * 0.3  # 4 es el total posible

        results.append({
            "template_id": tpl["template_id"],
            "template": tpl["template"],
            "cosine_similarity": cos_sim,
            "entity_match_score": match_score,
            "final_score": final_score
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[0] if results else {"error": "No templates available."}
