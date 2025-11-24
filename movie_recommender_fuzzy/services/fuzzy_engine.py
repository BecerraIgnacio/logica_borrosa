from __future__ import annotations

from typing import Dict


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _triangular(x: float, a: float, b: float, c: float) -> float:
    # Maneja triángulos degenerados para hombros izquierdo/derecho.
    if a == b:
        if x <= b:
            return 1.0
        if x >= c:
            return 0.0
        return (c - x) / (c - b)
    if b == c:
        if x >= b:
            return 1.0
        if x <= a:
            return 0.0
        return (x - a) / (b - a)

    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


class FuzzyEngine:
    """Motor difuso simple para calcular la relevancia de una película."""

    @staticmethod
    def compute_relevance(affinity: float, popularity: float, rating_similarity: float) -> float:
        """Devuelve solo la puntuación de relevancia."""
        score, _ = FuzzyEngine.compute_relevance_with_breakdown(affinity, popularity, rating_similarity)
        return score

    @staticmethod
    def compute_relevance_with_breakdown(
        affinity: float, popularity: float, rating_similarity: float
    ) -> tuple[float, dict]:
        """Devuelve una puntuación de relevancia en [0, 1]."""
        affinity = _clamp_01(affinity)
        popularity = _clamp_01(popularity)
        rating_similarity = _clamp_01(rating_similarity)

        # Heurística simple: afinidad domina.
        base = 0.90 * affinity + 0.10 * rating_similarity

        final = _clamp_01(base)
        breakdown = {
            "affinity": affinity,
            "rating_similarity": rating_similarity,
            "popularity": popularity,
            "weight_affinity": 0.80,
            "weight_rating": 0.15,
            "weight_popularity": 0.05,
            "penalty": 1.0,
            "weighted_sum": base,
            "final": final,
        }
        return final, breakdown
