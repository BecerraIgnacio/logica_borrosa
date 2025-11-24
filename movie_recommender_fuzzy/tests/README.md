# Tests

## Propósito

La carpeta `tests` contiene las pruebas automatizadas del proyecto. El objetivo es verificar el comportamiento correcto de la lógica de negocio, especialmente:

* El motor de lógica borrosa (`FuzzyEngine`).
* El servicio de recomendación (`RecommendationService`).
* El flujo de sesiones de valoración (`SessionService`).

Las pruebas ayudan a refactorizar con seguridad y a detectar errores al agregar nuevas funcionalidades.

## Archivos

* `__init__.py`: permite que la carpeta se trate como un paquete Python.
* `test_fuzzy_engine.py`: pruebas unitarias del motor difuso.
* `test_recommendation_service.py`: pruebas del servicio de recomendaciones.
* `test_session_service.py`: pruebas del flujo de sesión (inicio, registro de decisiones, finalización).
* `README.md`: este archivo de documentación.

## Alcance de las pruebas

### `test_fuzzy_engine.py`

Objetivo:

* Verificar que `FuzzyEngine.compute_relevance(...)` produzca valores coherentes para distintas combinaciones de:

  * afinidad de género,
  * popularidad,
  * similitud de rating.

Casos sugeridos:

* Alta afinidad + alta popularidad → relevancia alta.
* Baja afinidad + baja popularidad → relevancia baja.
* Casos intermedios para validar transiciones suaves.

### `test_recommendation_service.py`

Objetivo:

* Verificar que `RecommendationService.recommend_movies(...)` devuelva:

  * exacto `k` resultados (por defecto 5),
  * solo películas no valoradas en la sesión,
  * ordenadas de mayor a menor relevancia.

Casos sugeridos:

* Usuario con fuerte preferencia por uno o dos géneros.
* Catálogo pequeño de prueba y resultados esperados bien conocidos.

### `test_session_service.py`

Objetivo:

* Comprobar que `SessionService`:

  * Cree correctamente una sesión nueva.
  * Seleccione películas no repetidas durante la sesión.
  * Registre decisiones (Like/Dislike/No la vi) de forma consistente.
  * Incremente el contador de valoraciones válidas solo para Like/Dislike.
  * Marque la sesión como completada al llegar a 20 valoraciones válidas.

Casos sugeridos:

* Mezcla de decisiones con "No la vi" que no deben contar al total.
* Sesión que llega exactamente a 20 valoraciones válidas.

## Herramientas recomendadas

* `pytest` como framework de testing.
* Opcionalmente, `pytest-cov` para medir cobertura.

Ejemplo de instalación (posterior, en `requirements.txt`):

```txt
pytest
pytest-cov
```

Ejemplo de ejecución:

```bash
pytest
```

## Buenas prácticas

* Mantener los tests independientes entre sí (no compartir estado global mutable).
* Usar datos pequeños y controlados (catálogos reducidos de películas de prueba).
* Nombrar los tests de forma descriptiva (por ejemplo, `test_relevance_high_affinity_and_popularity`).
* Cubrir tanto casos “normales” como bordes (valores extremos, listas vacías, etc.).
