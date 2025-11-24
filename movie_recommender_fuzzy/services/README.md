# Services Layer

## Propósito

La carpeta `app/services` implementa la lógica de aplicación del sistema de recomendación. Esta capa orquesta el uso de las entidades de dominio y los repositorios de infraestructura para resolver casos de uso concretos:

* Manejar la sesión de "swipes" (Like / Dislike / No la vi).
* Construir el perfil de preferencias del usuario a partir de sus interacciones.
* Evaluar películas candidatas mediante lógica borrosa.
* Generar la lista final de películas recomendadas.

Los servicios no conocen detalles de la web (HTTP, templates) ni de la persistencia concreta (archivos, memoria, base de datos); solo dependen de interfaces/repositores y del modelo de dominio.

## Archivos

* `session_service.py`: coordina el flujo de una sesión de valoración (20 valoraciones válidas).
* `preference_service.py`: construye el `UserPreferenceProfile` a partir de las interacciones y las películas.
* `fuzzy_engine.py`: encapsula el motor de lógica borrosa utilizado para calcular la relevancia de las películas.
* `recommendation_service.py`: genera recomendaciones finales combinando el perfil de usuario, el catálogo de películas y el motor difuso.
* `README.md`: este archivo de documentación.

## Descripción de servicios

### SessionService (`session_service.py`)

Responsabilidades principales:

* Iniciar una nueva sesión de recomendación para un usuario.
* Obtener la siguiente película a mostrar durante la sesión.
* Registrar la decisión del usuario (Like / Dislike / No la vi).
* Llevar el conteo de valoraciones válidas hasta alcanzar el objetivo (20 por defecto).
* Marcar la sesión como completada cuando se llega al número requerido de valoraciones.

Dependencias típicas:

* `MovieRepository` (para obtener películas disponibles).
* `SessionRepository` (para crear/actualizar sesiones).
* `InteractionRepository` (para guardar interacciones).

Métodos sugeridos:

* `start_session(user_id: int) -> Session`
* `get_next_movie(session_id: int) -> Movie`
* `register_decision(session_id: int, movie_id: int, decision: str) -> None`

### PreferenceService (`preference_service.py`)

Responsabilidades principales:

* Construir un `UserPreferenceProfile` usando las interacciones de una sesión.
* Calcular afinidad por género a partir de likes y dislikes.
* Estimar un `preferred_rating` (rating promedio de películas con Like), si el dato está disponible.

Dependencias típicas:

* `InteractionRepository` (para obtener interacciones de la sesión/usuario).
* `MovieRepository` (para mapear `movie_id` a `Movie` y conocer sus géneros y ratings).

Método sugerido:

* `build_user_profile(user_id: int, session_id: int) -> UserPreferenceProfile`

### FuzzyEngine (`fuzzy_engine.py`)

Responsabilidades principales:

* Definir las variables lingüísticas de entrada y salida del sistema difuso.
* Implementar las funciones de pertenencia (afinidad de género, popularidad, similitud de rating, relevancia).
* Aplicar las reglas difusas (Mamdani u otro enfoque definido).
* Realizar la desfuzzificación para obtener un valor numérico de relevancia en [0, 1] (o escala similar).

Dependencias típicas:

* Puede usar librerías numéricas como `numpy`.
* No debe depender de repositorios ni de la web.

Método central sugerido:

* `compute_relevance(affinity: float, popularity: float, rating_similarity: float) -> float`

Otros métodos internos (no imprescindibles, pero recomendados):

* `compute_affinity_membership(raw_affinity: float) -> dict`
* `compute_popularity_membership(popularity: float) -> dict`
* `compute_rating_similarity_membership(similarity: float) -> dict`

### RecommendationService (`recommendation_service.py`)

Responsabilidades principales:

* Construir el perfil de usuario mediante `PreferenceService`.
* Seleccionar las películas candidatas (no valoradas en la sesión actual).
* Calcular, para cada candidata, su relevancia usando `FuzzyEngine`.
* Ordenar las películas por relevancia y devolver las `k` mejores.

Dependencias típicas:

* `MovieRepository`
* `InteractionRepository`
* `PreferenceService`
* `FuzzyEngine`

Método sugerido:

* `recommend_movies(user_id: int, session_id: int, k: int = 5) -> list[Movie]`

## Flujo típico entre servicios

1. `SessionService.start_session(user_id)` crea una sesión y la guarda en `SessionRepository`.
2. Durante la sesión, `SessionService.get_next_movie(session_id)` selecciona películas a mostrar (basado en `MovieRepository` y en las interacciones previas).
3. Cada vez que el usuario elige Like/Dislike/No la vi, `SessionService.register_decision(...)` registra una `Interaction` y actualiza el estado de la sesión.
4. Cuando la sesión se completa (20 valoraciones válidas), la capa web invoca `RecommendationService.recommend_movies(...)`.
5. `RecommendationService` llama a `PreferenceService.build_user_profile(...)` para obtener el perfil.
6. Para cada película candidata, `RecommendationService` calcula afinidad de género, popularidad, similitud de rating y llama a `FuzzyEngine.compute_relevance(...)`.
7. `RecommendationService` devuelve las 5 películas con mayor relevancia.

## Dependencias

La capa `services` puede depender de:

* Modelo de dominio (`app/domain`).
* Repositorios de infraestructura (`app/infra`).
* Librerías estándar y, opcionalmente, `numpy` u otras utilidades numéricas para el motor difuso.

No debe depender de:

* `app/web` (endpoints, HTTP, templates).

Esto permite que los servicios se puedan probar fácilmente mediante tests unitarios y reutilizar en otros contextos (scripts, CLIs, etc.).

## Notas

* Mantener los servicios relativamente finos: cada servicio debe tener una responsabilidad clara.
* Evitar que la lógica difusa se desparrame por varias capas; debe estar centralizada en `FuzzyEngine`.
* Diseñar las interfaces de servicios pensando en tests: métodos puros en lo posible y uso explícito de dependencias (inyección de repositorios/motores en el constructor o en parámetros).
