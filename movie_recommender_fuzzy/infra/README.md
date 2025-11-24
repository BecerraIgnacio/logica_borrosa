# Infra Layer

## Propósito

La carpeta `app/infra` implementa la capa de infraestructura del proyecto. Aquí se resuelve **cómo** se almacenan y se recuperan los datos, sin mezclar lógica de negocio ni detalles de interfaz de usuario.

En esta capa viven los repositorios (MovieRepository, SessionRepository, InteractionRepository) y cualquier mecanismo de persistencia (inicialmente, almacenamiento en memoria y lectura de archivos JSON).

## Archivos

* `movie_repository.py`: acceso al catálogo de películas (lectura de `data/movies.json` u otra fuente).
* `interaction_repository.py`: almacenamiento y consulta de interacciones de usuario.
* `session_repository.py`: almacenamiento y consulta de sesiones de recomendación.
* `db_memory.py`: implementación de una "base de datos" en memoria para desarrollo y pruebas.
* `README.md`: este archivo de documentación.

## Responsabilidades

* Proveer una API clara para leer/escribir entidades de dominio (Movie, Session, Interaction).
* Ocultar los detalles concretos de almacenamiento (memoria, archivo, base de datos real, etc.).
* Permitir reemplazar fácilmente la implementación subyacente sin tocar la capa de servicios.

## Diseño recomendado de repositorios

### MovieRepository

Responsabilidades:

* Cargar el catálogo de películas desde `data/movies.json` (u otra fuente).
* Exponer métodos como:

  * `get_all_movies() -> list[Movie]`
  * `get_movie_by_id(movie_id: int) -> Movie | None`
  * `get_random_movies(limit: int, exclude_ids: list[int]) -> list[Movie]`

Notas:

* El parsing de JSON se realiza aquí, transformando dicts en instancias de `Movie`.
* La lógica de selección de películas aleatorias se limita a criterios simples (excluir ya valoradas, tamaño máximo, etc.).

### InteractionRepository

Responsabilidades:

* Registrar cada interacción de usuario con una película.
* Exponer métodos como:

  * `save_interaction(interaction: Interaction) -> None`
  * `get_interactions_by_session(session_id: int) -> list[Interaction]`
  * `get_interactions_by_user(user_id: int) -> list[Interaction]`

Notas:

* En la versión inicial, puede usar listas en memoria.
* Más adelante, se puede migrar a una base de datos relacional o NoSQL sin cambiar la interfaz pública.

### SessionRepository

Responsabilidades:

* Crear, leer y actualizar sesiones de recomendación.
* Exponer métodos como:

  * `create_session(user_id: int) -> Session`
  * `get_session_by_id(session_id: int) -> Session | None`
  * `update_session(session: Session) -> None`

Notas:

* Puede reutilizar estructuras en memoria provistas por `db_memory.py`.
* Debe ser responsable de generar IDs únicos de sesión (aunque la estrategia concreta se pueda delegar).

### db_memory.py

Responsabilidades:

* Proveer estructuras y utilidades para almacenar datos en memoria durante el desarrollo.
* Implementar contenedores simples (diccionarios, listas) para:

  * Películas cargadas.
  * Sesiones activas/completadas.
  * Interacciones registradas.

Ejemplo de estructuras internas (orientativo):

* `MOVIES_BY_ID: dict[int, Movie]`
* `SESSIONS_BY_ID: dict[int, Session]`
* `INTERACTIONS_BY_SESSION: dict[int, list[Interaction]]`

## Dependencias

La capa `infra` puede depender de:

* Clases de dominio definidas en `app/domain` (Movie, Session, Interaction).
* Librerías de la estándar de Python (`json`, `random`, `datetime`, etc.).

No debe depender de:

* `app/services`
* `app/web`

De esta manera, los repositorios pueden reutilizarse en distintos contextos (por ejemplo, scripts de migración o herramientas de administración).

## Evolución futura

Algunas posibles extensiones:

* Reemplazar `db_memory.py` por una base de datos real (SQLite, PostgreSQL, etc.).
* Introducir una capa de mapeo objeto-relacional (ORM) si el proyecto crece.
* Añadir cachés o índices en memoria para mejorar el rendimiento del recomendador.

La interfaz pública de los repositorios debe mantenerse estable para minimizar el impacto de estos cambios en la capa de servicios.
