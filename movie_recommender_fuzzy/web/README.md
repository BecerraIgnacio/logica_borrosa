# Web Layer

## Propósito

La carpeta `app/web` contiene la capa de presentación del sistema de recomendación. Aquí se define cómo se expone la funcionalidad a través de HTTP y vistas HTML, sin implementar lógica de negocio ni acceso directo a datos.

Esta capa se apoya en los servicios de `app/services` para ejecutar casos de uso como:

* Iniciar una sesión de recomendación.
* Mostrar la siguiente película para evaluar (Like / Dislike / No la vi).
* Presentar los resultados (las 5 películas recomendadas).

## Archivos

* `app.py`: punto de entrada de la aplicación web (creación e inicialización de la app Flask/FastAPI y registro de rutas).
* `routes.py`: definición de endpoints/controladores que conectan HTTP con los servicios.
* `templates/`:

  * `base.html`: layout general (estructura común, cabecera, estilos compartidos).
  * `swipe.html`: vista para mostrar la película actual y los botones de Like/Dislike/No la vi, junto con el progreso (X/20).
  * `results.html`: vista para mostrar las 5 películas recomendadas al finalizar la sesión.
* `static/`:

  * `css/main.css`: estilos básicos de la interfaz.
  * `js/app.js`: lógica JavaScript mínima para mejorar la experiencia (por ejemplo, envío de formularios sin recargar toda la página, animaciones simples, etc.).
* `README.md`: este archivo de documentación.

## Rutas/Endpoints previstos (ejemplo con Flask)

* `GET /` → redirige a `/start`.
* `GET /start` → crea o recupera una sesión activa para el usuario y redirige a `/swipe`.
* `GET /swipe?session_id=...` → obtiene la próxima película a evaluar a través de `SessionService` y renderiza `swipe.html`.
* `POST /swipe` → recibe `session_id`, `movie_id` y `decision` (Like/Dislike/Not_Seen), invoca `SessionService.register_decision(...)` y:

  * si aún no se llegó a las 20 valoraciones válidas, redirige nuevamente a `/swipe`;
  * si la sesión ya se completó, redirige a `/results`.
* `GET /results?session_id=...` → invoca `RecommendationService.recommend_movies(...)` y renderiza `results.html` con las películas recomendadas.

Estas rutas son orientativas y pueden ajustarse según el framework web elegido (Flask/FastAPI) o necesidades futuras.

## Responsabilidades de la capa web

* Recibir solicitudes HTTP y extraer parámetros relevantes (session_id, movie_id, decision, etc.).
* Llamar a los servicios apropiados de la capa de aplicación (`SessionService`, `RecommendationService`).
* Traducir las respuestas de los servicios a:

  * HTML renderizado (templates),
  * o JSON (si en algún momento se expone una API).
* Gestionar el flujo de navegación del usuario (redirecciones entre `/start`, `/swipe` y `/results`).

No debe:

* Implementar lógica de negocio compleja.
* Acceder directamente a archivos de datos o almacenamiento (para eso está `app/infra`).

## Estructura prevista de templates

### `base.html`

* Contiene la estructura general de la página:

  * `<head>` con referencias a `main.css` y cualquier fuente/ícono necesario.
  * `<body>` con un bloque principal para contenido específico de cada vista.
* Define bloques (por ejemplo, `block content`) para que `swipe.html` y `results.html` los rellenen.

### `swipe.html`

* Muestra:

  * Título de la película.
  * Información básica (año, géneros, rating, etc.).
  * Opcionalmente, el póster.
  * Progreso: "Valoraciones válidas: X / 20".
* Incluye botones o formularios para:

  * Like.
  * Dislike.
  * No la vi.
* Cada acción envía un `POST /swipe` con los datos necesarios.

### `results.html`

* Muestra la lista de 5 películas recomendadas, con:

  * Título.
  * Géneros.
  * Rating/popularidad.
  * Opcionalmente, póster.
* Puede ofrecer un botón para iniciar una nueva sesión (`/start`).

## Uso de `static/css` y `static/js`

* `css/main.css`:

  * Definir estilos coherentes para botones de Like/Dislike/No la vi.
  * Layout responsivo mínimo para que la app sea usable en móvil.
  * Estilos generales para títulos, tarjetas de película, etc.

* `js/app.js` (opcional al inicio):

  * Puede manejar confirmaciones, animaciones al hacer swipe/click, o envío de formularios vía AJAX.
  * En una primera versión, puede quedar casi vacío y luego crecer según necesidades.

## Dependencias

La capa `web` puede depender de:

* Framework web elegido (Flask o FastAPI).
* Servicios definidos en `app/services`.
* Templates HTML y archivos estáticos.

No debe depender de:

* Repositorios de `app/infra` directamente.

De esta manera, si cambia la implementación de la capa de servicios o de infraestructura, la capa web solo interactúa con interfaces de alto nivel.

## Notas

* Mantener los controladores/endpoints finos: delegar la lógica al máximo en los servicios.
* Pensar la estructura de templates para poder reutilizar componentes visuales (por ejemplo, una tarjeta de película).
* Si más adelante se expone una API REST/JSON, se pueden añadir rutas paralelas (por ejemplo, `/api/swipe`, `/api/recommendations`) usando los mismos servicios internos.
