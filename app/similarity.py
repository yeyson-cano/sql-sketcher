# app/similarity.py

from typing import List
from math import sqrt

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if len(vec1) != len(vec2):
        raise ValueError("Vector lengths do not match")

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sqrt(sum(a * a for a in vec1))
    norm2 = sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)
