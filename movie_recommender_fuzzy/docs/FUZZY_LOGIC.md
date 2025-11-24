# Fuzzy Logic

## Propósito

Este documento describe el diseño del sistema de lógica borrosa utilizado en `movie_recommender_fuzzy` para evaluar la relevancia de cada película candidata y generar recomendaciones personalizadas.

El motor difuso se implementará en `app/services/fuzzy_engine.py` y será utilizado por `RecommendationService`.

---

## Objetivo del sistema difuso

Entrada: características de una película candidata en relación con el perfil del usuario.  
Salida: un valor numérico de **Relevancia** en un rango continuo (por ejemplo, [0, 1]) que permita ordenar películas.

Variables de entrada principales:
- Afinidad de género (`Affinity`)
- Popularidad (`Popularity`)
- Similitud de rating (`RatingSimilarity`)

Variable de salida:
- Relevancia (`Relevance`)

---

## Variables de entrada

### 1. Afinidad de género (`Affinity`)

Rango: [0, 1]

Interpretación:
- 0: el usuario tiende a no gustar de este género.
- 1: el usuario tiende a gustar mucho de este género.

Se obtiene a partir de `UserPreferenceProfile.genre_affinities`, promediando la afinidad de los géneros de la película.

Conjuntos lingüísticos propuestos:
- `Low`
- `Medium`
- `High`

Ejemplo de funciones de pertenencia (triangulares/trapezoidales, se puede ajustar):
- `Low`:
  - μ = 1 en x = 0
  - μ = 0 en x ≥ 0.4
- `Medium`:
  - μ = 0 en x ≤ 0.2
  - μ = 1 en x ≈ 0.5
  - μ = 0 en x ≥ 0.8
- `High`:
  - μ = 0 en x ≤ 0.6
  - μ = 1 en x = 1

### 2. Popularidad (`Popularity`)

Rango normalizado: [0, 1]

Interpretación:
- 0: muy poco popular.
- 1: muy popular.

Conjuntos lingüísticos propuestos:
- `Low`
- `Medium`
- `High`

Ejemplo de funciones de pertenencia:
- `Low`: dominante en [0, 0.4]
- `Medium`: pico en torno a 0.5
- `High`: dominante a partir de 0.6–0.7

### 3. Similitud de rating (`RatingSimilarity`)

Rango: [0, 1]

Se calcula comparando el rating de la película con el `preferred_rating` del usuario. Por ejemplo:

- Calcular la diferencia absoluta `diff = |rating_pelicula - preferred_rating|`.
- Mapear esa diferencia a una similitud en [0, 1], donde:
  - `diff = 0` → similitud 1
  - `diff >= max_diff` (por ejemplo, 4 puntos en escala 0–10) → similitud 0.

Conjuntos lingüísticos propuestos:
- `Low`
- `Medium`
- `High`

Ejemplo de funciones de pertenencia:
- `Low`: similitud en [0, 0.3]
- `Medium`: en torno a 0.5
- `High`: a partir de ~0.7

---

## Variable de salida: Relevancia (`Relevance`)

Rango: [0, 1]

Interpretación:
- 0: no recomendable.
- 1: altamente recomendable.

Conjuntos lingüísticos propuestos:
- `VeryLow`
- `Low`
- `Medium`
- `High`
- `VeryHigh`

Las funciones de pertenencia pueden ser trapezoidales/triangulares repartidas a lo largo del rango [0, 1].

---

## Base de reglas difusas

Reglas ejemplo (se pueden ajustar durante la implementación):

1. **Regla 1**  
   SI `Affinity` ES `High` Y `Popularity` ES `High`  
   ENTONCES `Relevance` ES `VeryHigh`.

2. **Regla 2**  
   SI `Affinity` ES `High` Y `RatingSimilarity` ES `High`  
   ENTONCES `Relevance` ES `VeryHigh`.

3. **Regla 3**  
   SI `Affinity` ES `High` Y `Popularity` ES `Medium`  
   ENTONCES `Relevance` ES `High`.

4. **Regla 4**  
   SI `Affinity` ES `Medium` Y `Popularity` ES `High`  
   ENTONCES `Relevance` ES `High`.

5. **Regla 5**  
   SI `Affinity` ES `Medium` Y `RatingSimilarity` ES `Medium`  
   ENTONCES `Relevance` ES `Medium`.

6. **Regla 6**  
   SI `Affinity` ES `Low` Y `Popularity` ES `High`  
   ENTONCES `Relevance` ES `Medium`.

7. **Regla 7**  
   SI `Affinity` ES `Low` Y `Popularity` ES `Low`  
   ENTONCES `Relevance` ES `Low`.

8. **Regla 8**  
   SI `Affinity` ES `Low` Y `RatingSimilarity` ES `Low`  
   ENTONCES `Relevance` ES `VeryLow`.

9. **Regla 9**  
   SI `Affinity` ES `High` Y `Popularity` ES `Low` Y `RatingSimilarity` ES `High`  
   ENTONCES `Relevance` ES `High`.

El conjunto de reglas puede ampliarse o afinarse tras pruebas con datos reales.

---

## Método de inferencia y desfuzzificación

- Tipo de sistema: Mamdani (mínimo/máximo) o similar.
- Operaciones típicas:
  - AND → mínimo (`min(a, b)`).
  - OR → máximo (`max(a, b)`).
- Agregación de reglas: unión (máximo) de las salidas difusas por cada etiqueta de `Relevance`.
- Desfuzzificación: centroide (centro de gravedad) sobre el conjunto agregado de `Relevance`.

Resultado final: un escalar `relevance_score ∈ [0, 1]` por película candidata.

---

## Interfaz prevista de `FuzzyEngine`

Archivo: `app/services/fuzzy_engine.py`

Firma principal sugerida:

```python
def compute_relevance(affinity: float, popularity: float, rating_similarity: float) -> float:
    """Devuelve una puntuación de relevancia en [0, 1] para una película candidata."""
    ...
