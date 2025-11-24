from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from movie_recommender_fuzzy.infra.tmdb_client import TMDbClient


def _extract_year(release_date: str) -> int:
    if not release_date:
        return 0
    try:
        return int(release_date.split("-")[0])
    except (ValueError, IndexError):
        return 0


def _map_tmdb_item(item: Dict[str, object], genre_map: Dict[int, str], is_top: bool) -> Dict[str, object]:
    genre_ids = item.get("genre_ids") or []
    genres = [genre_map.get(gid, str(gid)) for gid in genre_ids]
    return {
        "id": int(item["id"]),
        "title": str(item.get("title") or item.get("name") or ""),
        "year": _extract_year(str(item.get("release_date", ""))),
        "genres": genres,
        "duration_minutes": None,
        "popularity": float(item.get("popularity", 0.0)),
        "rating": float(item["vote_average"]) if item.get("vote_average") is not None else None,
        "poster_url": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else None,
        "is_top_100": is_top,
    }


def fetch_catalog(
    api_key: str,
    total: int = 1000,
    top_limit: int = 100,
    language: str = "en-US",
    vote_count_gte: int = 500,
) -> List[Dict[str, object]]:
    """Obtiene catálogo (top valoradas + resto por rating) desde TMDb."""
    client = TMDbClient(api_key=api_key)
    genre_map = client.get_genres(language=language)

    movies: List[Dict[str, object]] = []
    seen_ids: Set[int] = set()

    # Top mejor valoradas (con mínimo de votos para evitar ruido)
    top_pages = math.ceil(top_limit / 20)
    for item in client.get_top_rated(pages=top_pages, language=language, vote_count_gte=vote_count_gte):
        tmdb_id = int(item["id"])
        if tmdb_id in seen_ids:
            continue
        movies.append(_map_tmdb_item(item, genre_map, is_top=True))
        seen_ids.add(tmdb_id)
        if len(movies) >= top_limit:
            break

    # Resto del catálogo por rating (no solo lo más reciente)
    remaining = max(total - len(movies), 0)
    discover_pages = math.ceil(remaining / 20)
    if discover_pages > 0:
        for item in client.discover_popular(
            pages=discover_pages,
            language=language,
            vote_count_gte=vote_count_gte,
            sort_by="vote_average.desc",
        ):
            tmdb_id = int(item["id"])
            if tmdb_id in seen_ids:
                continue
            movies.append(_map_tmdb_item(item, genre_map, is_top=False))
            seen_ids.add(tmdb_id)
            if len(movies) >= total:
                break

    return movies


def save_catalog_to_file(
    target_path: Path,
    api_key: Optional[str] = None,
    total: int = 1000,
    top_limit: int = 100,
    language: str = "en-US",
    vote_count_gte: int = 50,
) -> None:
    """Descarga y guarda el catálogo en un archivo JSON."""
    key = api_key or os.getenv("TMDB_API_KEY")
    if not key:
        raise ValueError("TMDB_API_KEY no definido y no se proporcionó api_key")

    movies = fetch_catalog(
        api_key=key,
        total=total,
        top_limit=top_limit,
        language=language,
        vote_count_gte=vote_count_gte,
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(movies, indent=2), encoding="utf-8")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Descarga catálogo de películas desde TMDb.")
    parser.add_argument("--api-key", dest="api_key", default=os.getenv("TMDB_API_KEY"), help="API Key de TMDb")
    parser.add_argument("--total", type=int, default=1000, help="Cantidad total de películas a descargar")
    parser.add_argument("--top-limit", type=int, default=100, help="Cantidad de películas top populares")
    parser.add_argument("--language", default="en-US", help="Idioma de los resultados")
    parser.add_argument("--vote-count-gte", type=int, default=50, help="Votos mínimos para discover")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "data" / "movies.json"),
        help="Ruta del archivo de salida",
    )

    args = parser.parse_args()
    if not args.api_key:
        raise SystemExit("TMDB_API_KEY no definido. Usa --api-key o exporta la variable de entorno.")

    save_catalog_to_file(
        target_path=Path(args.output),
        api_key=args.api_key,
        total=args.total,
        top_limit=args.top_limit,
        language=args.language,
        vote_count_gte=args.vote_count_gte,
    )
    print(f"Catálogo guardado en {args.output}")


if __name__ == "__main__":
    main()
