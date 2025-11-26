# Movie Recommender Fuzzy

Recomienda películas con un flujo tipo “swipe” y lógica borrosa para priorizar lo que realmente te gusta.

## Cómo funciona (en 1 minuto)
1) Configura filtros opcionales (géneros/duración).  
2) Califica 20 películas (1–5 o “No la vi”).  
3) Con esas valoraciones se arma tu perfil: afinidad por géneros y rating preferido.  
4) Obtienes 10 recomendaciones ordenadas por relevancia.  
5) Si quieres, “das vuelta” una tarjeta y calificas qué tan afín te resultó para refinar al instante.

## Qué considera la recomendación
- **Afinidad de géneros**: domina el score. Se calcula con tus notas 1–5 por género (1–2 rechaza, 3 neutro, 4–5 gusta).  
- **Similitud de rating**: qué tan cerca está el rating de la película de tu rating preferido.  
- Fórmula simple: `relevancia = 0.90 * afinidad + 0.10 * similitud_rating`.

## Flujo en la web
- Inicio → Filtros → 20 swipes (aleatorios del top 100) → “Ver recomendaciones” (a los 5+ válidas) → Ajuste en tarjetas.  
- Cada tarjeta muestra un breakdown de afinidad, similitud y popularidad (solo informativa).

## Datos
- Catálogo en `data/movies.json` (id, título, año, géneros normalizados, rating, popularidad, poster).  
- Se puede regenerar con TMDb usando `infra/tmdb_loader.py` (necesita API key).

## Ejecutar
```bash
source .venv/bin/activate
FLASK_APP=movie_recommender_fuzzy.web.app FLASK_ENV=production flask run
# o: TMPDIR=/tmp python -m movie_recommender_fuzzy.web.app
```

## Notas
- Estado en memoria: reiniciar el server borra la sesión.  
- Si quieres ver otras 20 iniciales, inicia una sesión nueva (la selección es aleatoria dentro del top 100).  
- Filtros aplican tanto al pool inicial como a las recomendaciones.  
