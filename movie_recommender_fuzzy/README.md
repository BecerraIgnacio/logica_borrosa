# Movie Recommender Fuzzy

Guía funcional de la aplicación y de cómo se aplica la lógica borrosa en las recomendaciones.

## ¿Qué hace?

- Presenta 20 películas (seleccionadas aleatoriamente del top 100 popular) para que las puntúes de 1 a 5 o marques “No la vi”.
- Con esas valoraciones construye tu perfil de gustos: afinidad por géneros y una noción de rating preferido.
- Genera 10 recomendaciones desde un catálogo de ~1000 títulos, ordenadas por relevancia.
- Permite refinar más: en el panel de resultados puedes “dar vuelta” cada tarjeta y calificar qué tan afín te resulta; las recomendaciones se recalculan al vuelo.

## Cómo se usan tus valoraciones

- **Escala 1–5 en el swipe inicial**  
  - 1–2: señal de rechazo al género (afinidad 0 para ese género en ese título).  
  - 3: neutro (no aporta afinidad).  
  - 4–5: preferencia; se promedia por género para subir la afinidad (5 = 1.0).
- **“No la vi”** no modifica el perfil.
- **Feedback en resultados**: al calificar una recomendación se agrega una interacción extra y se reconstruye el perfil para mejorar el ranking siguiente.

## Cómo se calcula la afinidad por género

1. Se normalizan los géneros (minúsculas, sin espacios extra).
2. Para cada género:  
   - promedio de scores de películas con ese género;  
   - promedio ≤ 2 ⇒ afinidad 0;  
   - promedio ≥ 5 ⇒ afinidad 1;  
   - entre 2 y 5 ⇒ afinidad lineal ( (score-2)/3 ).
3. Afinidad de una película candidata: se toma el **mejor** valor de afinidad de los géneros que coinciden contigo y se multiplica por la cobertura (porcentaje de géneros del título que coinciden).

## Motor de relevancia (heurística borrosa simplificada)

- Fórmula actual: `relevancia = 0.90 * afinidad + 0.10 * similitud_rating`  
  - **Afinidad**: el factor dominante (ver cálculo arriba).  
  - **Similitud de rating**: compara el rating del título con tu rating preferido (estimado a partir de lo que calificas 4–5); penaliza diferencias grandes.  
  - **Popularidad**: no participa en el score final (se mantiene en el breakdown como referencia).
- El breakdown que ves al “dar vuelta” una tarjeta muestra estos insumos para transparencia.

## Flujo de la aplicación

1) **Inicio de sesión**: al entrar a “Comenzar sesión” se crean repositorios en memoria y se seleccionan 20 títulos del top 100 (en orden aleatorio sin repetir).  
2) **Swipe de 20 títulos**: puntúas 1–5 o “No la vi”; cada score se guarda como interacción y actualiza el contador de válidas.  
3) **Generación de recomendaciones**: al llegar a 5+ valoraciones válidas se habilita “Ver recomendaciones”. Se calculan afinidades, el perfil y las 10 mejores según relevancia.  
4) **Refinamiento**: en resultados, al calificar una tarjeta se registra la interacción y se recalcula el ranking en vivo.  
5) **Transparencia**: cada tarjeta muestra un breakdown de afinidad, similitud de rating y popularidad normalizada.

## Datos y catálogo

- `data/movies.json` contiene el catálogo (id, título, año, géneros normalizados, rating, popularidad, poster).  
- El loader TMDb (`infra/tmdb_loader.py`) puede regenerar el archivo con top 100 mejor valoradas y hasta 1000 títulos en total.  
- La selección inicial de 20 siempre se toma del top 100 para obtener señal rápida de géneros populares.

## Ejecución rápida

1. Asegúrate de tener `movies.json` generado.  
2. Activa el entorno virtual y dependencias (`Flask`, `requests`).  
3. Levanta la app sin reloader para conservar las interacciones en memoria:  
   ```bash
   FLASK_APP=movie_recommender_fuzzy.web.app FLASK_ENV=production flask run
   ```  
   o  
   ```bash
   TMPDIR=/tmp python -m movie_recommender_fuzzy.web.app
   ```

## Notas

- El estado (sesión, interacciones) vive en memoria; reiniciar el servidor descarta datos.  
- Si ves siempre los mismos 20 títulos, arranca una sesión nueva; la selección es aleatoria dentro del top 100.  
- El sistema prioriza afinidad de géneros. Si calificas varios géneros con 4–5, aparecerán más mezclas; si los puntúas bajo, quedarán fuera del top.
