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
    """Motor difuso (Mamdani) para calcular la relevancia de una película."""

    @staticmethod
    def compute_relevance(affinity: float, popularity: float, rating_similarity: float) -> float:
        """Devuelve solo la puntuación de relevancia."""
        score, _ = FuzzyEngine.compute_relevance_with_breakdown(affinity, popularity, rating_similarity)
        return score

    @staticmethod
    def compute_relevance_with_breakdown(
        affinity: float, popularity: float, rating_similarity: float
    ) -> tuple[float, dict]:
        """Motor Mamdani paso a paso: fuzzificación, reglas, agregación y desfuzzificación (centroide)."""
        # 1) Fuzzificación de entradas (triangulares)
        affinity = _clamp_01(affinity)
        popularity = _clamp_01(popularity)
        rating_similarity = _clamp_01(rating_similarity)

        def fuzzify(x: float) -> Dict[str, float]:
            return {
                "low": _triangular(x, 0.0, 0.0, 0.4),
                "med": _triangular(x, 0.2, 0.5, 0.8),
                "high": _triangular(x, 0.6, 1.0, 1.0),
            }

        f_aff = fuzzify(affinity)
        f_pop = fuzzify(popularity)
        f_rat = fuzzify(rating_similarity)

        # 2) Base de reglas (min para AND). Etiquetas de salida: verylow, low, med, high, veryhigh.
        output_strengths: Dict[str, float] = {
            "verylow": 0.0,
            "low": 0.0,
            "med": 0.0,
            "high": 0.0,
            "veryhigh": 0.0,
        }

        def apply(label: str, *vals: float) -> None:
            output_strengths[label] = max(output_strengths[label], min(vals))

        apply("veryhigh", f_aff["high"], f_rat["high"])
        apply("high", f_aff["high"], f_pop["high"])
        apply("high", f_aff["med"], f_rat["high"])
        apply("high", f_aff["high"], f_pop["med"])
        apply("med", f_aff["med"], f_pop["med"])
        apply("med", f_aff["low"], f_pop["high"])
        apply("med", f_aff["high"], f_pop["low"])
        apply("low", f_aff["low"], f_rat["med"])
        apply("low", f_aff["low"], f_rat["low"])
        apply("verylow", f_aff["low"], f_pop["low"], f_rat["low"])

        # 3) Agregación de salidas: conjuntos triangulares para relevancia
        def out_membership(label: str, x: float) -> float:
            if label == "verylow":
                return _triangular(x, 0.0, 0.0, 0.2)
            if label == "low":
                return _triangular(x, 0.1, 0.25, 0.4)
            if label == "med":
                return _triangular(x, 0.35, 0.5, 0.65)
            if label == "high":
                return _triangular(x, 0.6, 0.75, 0.9)
            if label == "veryhigh":
                return _triangular(x, 0.8, 1.0, 1.0)
            return 0.0

        # 4) Desfuzzificación por centroide (muestreado)
        xs = [i / 200 for i in range(0, 201)]  # 0.00 a 1.00 con paso 0.005
        num = 0.0
        den = 0.0
        for x in xs:
            mu = max(output_strengths[label] * out_membership(label, x) for label in output_strengths)
            num += x * mu
            den += mu
        final = num / den if den > 0 else 0.0

        breakdown = {
            "affinity": affinity,
            "rating_similarity": rating_similarity,
            "popularity": popularity,
            "fuzzy_affinity": f_aff,
            "fuzzy_popularity": f_pop,
            "fuzzy_rating": f_rat,
            "output_strengths": output_strengths,
            "final": final,
        }
        return final, breakdown
