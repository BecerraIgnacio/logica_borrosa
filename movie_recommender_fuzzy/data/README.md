# Data

## Propósito

La carpeta `data` almacena los archivos de datos utilizados por el sistema de recomendación. El archivo principal es `movies.json`, que contiene el catálogo de películas a partir del cual se realizan las valoraciones y recomendaciones.

Esta carpeta no debe contener código, solo fuentes de datos (JSON, CSV, etc.).

## Archivos

* `movies.json`: catálogo de películas disponible para el recomendador.
* `README.md`: este archivo de documentación.

## Formato de `movies.json`

`movies.json` debe ser un arreglo JSON de objetos, donde cada objeto representa una película. Un esquema recomendado por película es:

* `id` (int): identificador único de la película.
* `title` (string): título de la película.
* `year` (int): año de estreno.
* `genres` (array de string): lista de géneros (por ejemplo, ["Action", "Sci-Fi"]).
* `duration_minutes` (int, opcional): duración aproximada en minutos.
* `popularity` (number): medida normalizada de popularidad (por ejemplo, entre 0 y 1, o entre 0 y 100).
* `rating` (number, opcional): puntuación global (por ejemplo, promedio de usuarios en escala 0–10).
* `poster_url` (string, opcional): URL del póster para mostrar en la interfaz web.

Ejemplo mínimo de `movies.json`:

```json
[
  {
    "id": 1,
    "title": "Inception",
    "year": 2010,
    "genres": ["Action", "Sci-Fi"],
    "duration_minutes": 148,
    "popularity": 0.95,
    "rating": 8.8,
    "poster_url": "https://example.com/inception.jpg"
  },
  {
    "id": 2,
    "title": "The Matrix",
    "year": 1999,
    "genres": ["Action", "Sci-Fi"],
    "duration_minutes": 136,
    "popularity": 0.90,
    "rating": 8.7,
    "poster_url": "https://example.com/matrix.jpg"
  }
]
```

## Recomendaciones para poblar `movies.json`

* Incluir al menos 40–50 películas para que el sistema de recomendación tenga suficiente variedad.
* Asegurarse de que los géneros estén normalizados (por ejemplo, siempre "Action" en lugar de mezclar "Acción" y "Action").
* Mantener `popularity` en una escala consistente (por ejemplo, 0–1) para facilitar el uso en el motor difuso.
* Rellenar `rating` cuando sea posible; si falta, el sistema puede ignorarlo o asumir un valor neutro.

## Uso dentro del proyecto

* `MovieRepository` será responsable de leer `movies.json`, parsear su contenido y transformarlo en instancias de `Movie`.
* Ninguna otra capa debe leer directamente este archivo; todas las consultas al catálogo de películas deben pasar por los repositorios de infraestructura.

## Notas

* Si en el futuro se migra a una base de datos, `movies.json` puede mantenerse como fuente de datos de ejemplo o como dataset inicial (seed).
* Para entornos de desarrollo y pruebas, se pueden crear variantes como `movies_dev.json` o `movies_small.json`, siempre documentadas en este directorio o en la documentación de arquitectura.
