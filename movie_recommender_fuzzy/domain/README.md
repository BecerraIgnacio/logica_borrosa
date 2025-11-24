# Domain Layer

## Propósito

La carpeta `app/domain` contiene el modelo de dominio del sistema de recomendación de películas. Aquí se definen las entidades centrales y sus reglas básicas, independientes de cualquier framework web, base de datos o detalles de infraestructura.

El objetivo es que todo el resto del sistema (infraestructura, servicios, capa web) dependa de estas clases, y no al revés.

## Archivos

* `models.py`: define las entidades principales del dominio.
* `profile.py`: define el perfil de preferencias del usuario y la lógica para construirlo a partir de interacciones.
* `README.md`: documentación de esta capa.

## Entidades principales

### Movie

Representa una película del catálogo.

Atributos típicos:

* `id`: identificador único.
* `title`: título.
* `year`: año de estreno.
* `genres`: lista de géneros.
* `duration_minutes`: duración aproximada.
* `popularity`: medida normalizada de popularidad.
* `rating`: puntuación global (por ejemplo, promedio de usuarios).
* `poster_url`: URL opcional del póster.

Responsabilidades:

* Encapsular la información básica de una película.
* Servir como unidad de referencia en interacciones y recomendaciones.

### User

Representa a un usuario del sistema (real o anónimo).

Atributos típicos:

* `id`
* `name` (opcional)

Responsabilidades:

* Ser la entidad sobre la que se construye el perfil de preferencias.
* Asociar sesiones e interacciones.

### Session

Representa una sesión de "swipe" (ciclo de 20 valoraciones).

Atributos típicos:

* `id`
* `user_id`
* `started_at`, `finished_at`
* `target_ratings` (por defecto 20)
* `valid_ratings_count` (cantidad de Like/Dislike registrados)
* `status` (por ejemplo: `ACTIVE`, `COMPLETED`)

Responsabilidades:

* Controlar el avance de la sesión.
* Indicar si se alcanzó el número objetivo de valoraciones válidas.
* Marcar inicio y fin de cada sesión de recomendación.

### Interaction

Representa la valoración de una película por parte de un usuario en el contexto de una sesión.

Atributos típicos:

* `id`
* `user_id`
* `movie_id`
* `session_id`
* `decision` (`LIKE`, `DISLIKE`, `NOT_SEEN`)
* `timestamp`

Responsabilidades:

* Registrar la decisión del usuario sobre una película concreta.
* Servir como insumo para construir el perfil de preferencias.

### UserPreferenceProfile (en `profile.py`)

Representa el perfil de preferencias del usuario derivado de sus interacciones.

Atributos típicos:

* `user_id`
* `genre_affinities`: diccionario género → afinidad (0–1).
* `preferred_rating`: rating promedio de películas marcadas `LIKE` (opcional).

Responsabilidades:

* Calcular afinidades por género a partir de likes/dislikes.
* Proveer métodos para consultar afinidad por género (por ejemplo, `get_genre_affinity(genre)`).
* Servir como puente entre los datos crudos de interacción y el motor de recomendación.

## Relaciones

* Un `User` puede tener múltiples `Session`.
* Una `Session` contiene múltiples `Interaction`.
* Cada `Interaction` vincula un `User` con una `Movie`.
* Un `UserPreferenceProfile` se construye a partir de las `Interaction` de un usuario (habitualmente de la sesión más reciente).

Las relaciones se representan mediante identificadores (`user_id`, `movie_id`, `session_id`); la recuperación de colecciones (por ejemplo, todas las interacciones de una sesión) se delega a los repositorios en la capa de infraestructura.

## Dependencias

La capa de dominio:

* No debe importar nada de `app.infra`, `app.services` ni `app.web`.
* Puede usar únicamente:

  * Tipos básicos de Python.
  * `datetime` para marcas de tiempo.
  * Tipos de anotación de `typing`.

Esto permite reutilizar el dominio en otros contextos (script de consola, tests, otra app web, etc.).

## Notas

* Mantener las clases simples y enfocadas en la lógica de negocio, sin detalles técnicos de almacenamiento o transporte.
* La lógica de recomendación difusa no debe vivir aquí, sino en servicios especializados.
* Métodos auxiliares como `Session.is_completed()` o `Interaction.is_valid_rating()` son bienvenidos siempre que sean puros (sin efectos externos).
