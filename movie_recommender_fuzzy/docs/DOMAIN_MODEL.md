# Domain Model

## Propósito

Este documento describe el modelo de dominio del sistema `movie_recommender_fuzzy`. Su objetivo es dejar claramente definidas las entidades principales, sus atributos y las relaciones entre ellas, como base para la implementación en `app/domain`.

Las entidades clave son:

* `Movie`
* `User`
* `Session`
* `Interaction`
* `UserPreferenceProfile`

---

## Entidades y atributos

### Movie

Representa una película disponible en el catálogo.

Atributos sugeridos:

* `id: int` — Identificador único de la película.
* `title: str` — Título de la película.
* `year: int` — Año de estreno.
* `genres: list[str]` — Lista de géneros (por ejemplo, `"Action"`, `"Drama"`).
* `duration_minutes: int | None` — Duración aproximada en minutos.
* `popularity: float` — Medida normalizada de popularidad (0–1 o 0–100, pero consistente).
* `rating: float | None` — Puntuación global (escala, por ejemplo, 0–10).
* `poster_url: str | None` — URL opcional del póster.

Responsabilidades clave:

* Encapsular la información de una película.
* Servir como referencia en interacciones y recomendaciones.

---

### User

Representa a un usuario del sistema (real o anónimo).

Atributos sugeridos:

* `id: int` — Identificador único de usuario.
* `name: str | None` — Nombre del usuario (opcional para este ejercicio).

Responsabilidades clave:

* Ser el sujeto sobre el cual se construye un perfil de preferencias.
* Ser dueño de una o más sesiones de recomendación.

---

### Session

Representa una sesión de recomendación tipo "swipe" donde el usuario valora películas.

Atributos sugeridos:

* `id: int` — Identificador único de sesión.
* `user_id: int` — Usuario dueño de la sesión.
* `started_at: datetime` — Fecha/hora de inicio.
* `finished_at: datetime | None` — Fecha/hora de finalización (si aplica).
* `target_ratings: int` — Número objetivo de valoraciones válidas (por defecto, 20).
* `valid_ratings_count: int` — Cantidad de valoraciones válidas registradas (Like/Dislike).
* `status: str` — Estado de la sesión (por ejemplo: `"ACTIVE"`, `"COMPLETED"`).

Métodos de dominio sugeridos:

* `is_completed() -> bool` — Devuelve `True` si `valid_ratings_count >= target_ratings`.
* `increment_valid_ratings() -> None` — Incrementa el contador de valoraciones válidas.
* `mark_completed() -> None` — Actualiza `status` y `finished_at`.

Responsabilidades clave:

* Controlar el ciclo de vida de una sesión de recomendaciones.
* Llevar el conteo de valoraciones válidas.

---

### Interaction

Representa la valoración de una película por parte de un usuario dentro de una sesión.

Atributos sugeridos:

* `id: int` — Identificador único de interacción.
* `user_id: int` — Usuario que realiza la valoración.
* `movie_id: int` — Película valorada.
* `session_id: int` — Sesión en la que ocurre la interacción.
* `decision: str` — Decisión del usuario (`"LIKE"`, `"DISLIKE"`, `"NOT_SEEN"`).
* `timestamp: datetime` — Fecha/hora en la que se registró la interacción.

Métodos de dominio sugeridos:

* `is_valid_rating() -> bool` — Devuelve `True` si `decision` es `LIKE` o `DISLIKE`.

Responsabilidades clave:

* Registrar la preferencia del usuario sobre una película específica.
* Servir como insumo para construir el perfil de usuario.

---

### UserPreferenceProfile

Representa el perfil de preferencias del usuario derivado de sus interacciones.

Atributos sugeridos:

* `user_id: int` — Usuario al que pertenece el perfil.
* `genre_affinities: dict[str, float]` — Afinidad por género en [0, 1].
* `preferred_rating: float | None` — Rating promedio de películas marcadas `LIKE`.

Métodos sugeridos:

* `get_genre_affinity(genre: str) -> float` — Devuelve la afinidad para un género (0 si no existe información).
* `update_from_interactions(interactions: list[Interaction], movies_by_id: dict[int, Movie]) -> None` — Calcula/actualiza afinidades y rating preferido a partir de las interacciones.

Responsabilidades clave:

* Concentrar información derivada de las interacciones.
* Servir de insumo directo al motor de recomendación difuso.

---

## Relaciones entre entidades

Resumen de relaciones (lógicas, expresadas mediante IDs):

* `User` 1 ── * `Session`

  * Un usuario puede tener múltiples sesiones.
  * Una sesión pertenece a un único usuario.

* `Session` 1 ── * `Interaction`

  * Una sesión contiene múltiples interacciones (una por valoración registrada).
  * Cada interacción pertenece a una única sesión.

* `User` 1 ── * `Interaction`

  * Un usuario puede tener múltiples interacciones.
  * Cada interacción se asocia a un usuario.

* `Movie` 1 ── * `Interaction`

  * Una película puede aparecer en muchas interacciones (de distintos usuarios o sesiones).
  * Cada interacción hace referencia a una única película.

* `User` 1 ── 1 `UserPreferenceProfile`

  * Cada usuario tiene, conceptualmente, un perfil de preferencias (al menos derivado de su sesión activa o más reciente).

Estas relaciones se implementan mediante atributos ID (`user_id`, `session_id`, `movie_id`), mientras que la navegación entre objetos (por ejemplo, obtener todas las interacciones de una sesión) se delega a repositorios en la capa de infraestructura.

---

## Diagrama de texto del modelo

Representación simplificada en texto:

* `User(id)`

  * tiene muchas → `Session(id, user_id)`
  * tiene muchas → `Interaction(id, user_id, movie_id, session_id, decision)`
  * tiene una → `UserPreferenceProfile(user_id, genre_affinities, preferred_rating)`

* `Session(id, user_id, ...)`

  * tiene muchas → `Interaction(id, user_id, movie_id, session_id, decision)`

* `Movie(id, title, ...)`

  * es referenciada por muchas → `Interaction(movie_id)`

---

## Notas de implementación

* El modelo de dominio no debe incluir lógica de acceso a datos (lectura de JSON, consultas SQL, etc.).
* La construcción de `UserPreferenceProfile` a partir de interacciones puede implementarse como método en la propia clase o delegarse a un servicio (`PreferenceService`), pero la representación final del perfil vive aquí.
* El motor de lógica borrosa **no** forma parte del dominio; se implementa en `FuzzyEngine` dentro de `app/services`.
* Los tipos y firmas aquí propuestos son guía; pueden ajustarse levemente durante la implementación siempre que se mantenga la intención del modelo.
