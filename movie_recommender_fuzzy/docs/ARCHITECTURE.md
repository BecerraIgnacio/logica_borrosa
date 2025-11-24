# Arquitectura del proyecto

## Propósito

Este documento describe la arquitectura general del proyecto `movie_recommender_fuzzy`.
El objetivo es dejar claro:

* Cómo están organizadas las capas.
* Cómo se comunican entre sí.
* Dónde vive cada tipo de lógica (dominio, datos, servicios, web).
* Qué decisiones permiten escalar y modificar el sistema sin romper todo.

---

## Visión general por capas

El proyecto se organiza en capas lógicas:

* **Dominio (`app/domain`)**
  Modelo de negocio puro: entidades (`Movie`, `User`, `Session`, `Interaction`, `UserPreferenceProfile`) y reglas básicas.
  No conoce nada de HTTP, JSON, archivos ni bases de datos.

* **Infraestructura (`app/infra`)**
  Maneja el acceso a datos: lectura de `movies.json`, almacenamiento de sesiones e interacciones (inicialmente en memoria).
  Implementa repositorios que exponen una API limpia hacia los servicios.

* **Servicios (`app/services`)**
  Orquesta casos de uso: sesiones de swipe, construcción de perfil de usuario, motor difuso y recomendaciones.
  Consume repositorios de `infra` y entidades de `domain`.
  No sabe nada de HTML ni rutas HTTP.

* **Web (`app/web`)**
  Capa de presentación: endpoints, templates HTML, archivos estáticos.
  Recibe solicitudes HTTP, llama a servicios y devuelve vistas (o JSON si se extiende a API).

* **Datos (`data`)**
  Archivos de datos crudos (principalmente `movies.json`).
  No contiene código.

* **Tests (`tests`)**
  Pruebas unitarias y de integración ligera para servicios y lógica difusa.

---

## Estructura de carpetas (resumen)

* `app/`

  * `domain/`
  * `infra/`
  * `services/`
  * `web/`
* `data/`
* `docs/`
* `tests/`
* `run.py`
* `requirements.txt`
* `README.md`

Cada subcarpeta tiene su propio `README.md` (o Markdown específico) para documentar decisiones locales.

---

## Flujo principal: sesión de recomendación

1. **Inicio de sesión (web → servicios)**

   * El usuario accede a `/start`.
   * La capa web llama a `SessionService.start_session(user_id)` para crear una sesión nueva.
   * `SessionService` usa `SessionRepository` para persistir la sesión.

2. **Ciclo de swipes**

   * Web llama a `SessionService.get_next_movie(session_id)`.
   * `SessionService` consulta películas desde `MovieRepository` y decide cuál mostrar (evitando repetidas en esa sesión).
   * La web presenta la película en `swipe.html` con botones:

     * Like
     * Dislike
     * No la vi
   * El usuario elige una opción → `POST /swipe`.
   * Web llama a `SessionService.register_decision(session_id, movie_id, decision)`:

     * Se crea una `Interaction` de dominio.
     * `InteractionRepository` la almacena.
     * Si `decision ∈ {LIKE, DISLIKE}`, `valid_ratings_count` aumenta.
     * Si `valid_ratings_count == target_ratings (20)`, la sesión pasa a `COMPLETED`.

3. **Generación de recomendaciones**

   * Al terminar la sesión, la web redirige a `/results`.
   * Web llama a `RecommendationService.recommend_movies(user_id, session_id, k=5)`:

     1. `PreferenceService.build_user_profile(...)` construye `UserPreferenceProfile` usando:

        * Interacciones de la sesión (`InteractionRepository`).
        * Datos de películas (`MovieRepository`).
     2. `RecommendationService` obtiene todas las películas no valoradas en la sesión.
     3. Para cada candidata:

        * Calcula afinidad de género según el perfil.
        * Obtiene popularidad y rating.
        * Calcula similitud de rating vs preferencia del usuario.
        * Llama a `FuzzyEngine.compute_relevance(affinity, popularity, rating_similarity)`.
     4. Ordena por relevancia y devuelve las 5 mejores.

4. **Presentación de resultados**

   * La web recibe la lista de películas recomendadas.
   * Renderiza `results.html` con esas 5 películas.

---

## Diagrama lógico de capas (texto)

* Web (`app/web`)

  * depende de → Services (`app/services`)

    * depende de → Infra (`app/infra`)
    * depende de → Domain (`app/domain`)
  * no depende directamente de Infra

* Infra (`app/infra`)

  * depende de → Domain (`app/domain`)
  * depende de → Data (`data/movies.json`, etc.)

* Domain (`app/domain`)

  * no depende de ninguna otra capa de la app.

---

## Responsabilidades y separación de preocupaciones

* **Domain**

  * Define qué es una película, un usuario, una sesión, una interacción.
  * Puede incluir lógica simple de negocio (por ejemplo, `Session.is_completed()`).

* **Infra**

  * Sabe “dónde” y “cómo” se guardan los datos.
  * Puede cambiar de almacenamiento en memoria a base de datos real sin cambiar la interfaz pública.

* **Services**

  * Implementan el “qué hay que hacer” para cada caso de uso:

    * “Iniciar una sesión”.
    * “Obtener la siguiente película”.
    * “Construir perfil de usuario”.
    * “Calcular relevancia y recomendar”.
  * No se preocupan de cómo se entrega el resultado al usuario (HTML, JSON, CLI).

* **Web**

  * Se encarga de:

    * Recibir solicitudes HTTP.
    * Validar parámetros básicos.
    * Llamar a servicios.
    * Renderizar templates o devolver JSON.

---

## Ciclo de vida de la aplicación

1. **Inicialización**

   * `run.py` importa y lanza la aplicación desde `app/web/app.py`.
   * La app web configura rutas, carga configuración (por ejemplo, ruta a `movies.json`), e inicializa las dependencias (repositorios y servicios).

2. **Carga de datos**

   * Al crear `MovieRepository`, se lee `data/movies.json` y se construye una estructura en memoria (`Movie` por id).

3. **Ejecutando peticiones**

   * Cada petición HTTP se procesa de forma independiente, utilizando las mismas instancias (o factorías) de servicios y repositorios.

---

## Consideraciones para escalar y extender

* **Cambio de almacenamiento**

  * Si se pasa de `db_memory.py` a una base de datos real, solo hay que modificar `app/infra` y la configuración.
  * `app/services` y `app/web` siguen usando las mismas interfaces.

* **Cambio de framework web (Flask → FastAPI)**

  * Se cambia únicamente `app/web` y, eventualmente, la inicialización en `run.py`.
  * La lógica de negocio no se toca.

* **API REST en paralelo a vistas HTML**

  * Se agregan endpoints `/api/...` en `app/web` que reutilizan los mismos servicios.
  * No se duplica lógica.

* **Nuevas funcionalidades (ejemplo: historial de recomendaciones)**

  * Se añadirían nuevas entidades/relaciones en `domain` e infraestructura en `infra`.
  * Nuevos métodos en `services`.
  * Nuevas vistas y/o endpoints en `web`.

---

## Notas futuras sobre Docker (placeholder)

La arquitectura está pensada para poder dockerizar fácilmente el proyecto:

* Un contenedor para la aplicación Python (web + servicios + dominio + infra).
* Opcionalmente, un contenedor adicional para base de datos cuando se deje de usar `db_memory.py`.

Más adelante se podrán agregar:

* `Dockerfile` en la raíz.
* `docker-compose.yml` con servicios de app y base de datos.
