from __future__ import annotations

import os
from typing import Dict, Iterable, Iterator, Optional

import requests


class TMDbClient:
    """Cliente mínimo para la API de The Movie Database (TMDb)."""

    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("TMDB_API_KEY no definido")
        self.session = session or requests.Session()
        self.base_url = "https://api.themoviedb.org/3"

    def _get(self, path: str, params: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        params = params or {}
        params["api_key"] = self.api_key
        response = self.session.get(f"{self.base_url}{path}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_genres(self, language: str = "en-US") -> Dict[int, str]:
        """Devuelve el catálogo de géneros (id → nombre)."""
        data = self._get("/genre/movie/list", {"language": language})
        return {genre["id"]: genre["name"] for genre in data.get("genres", [])}

    def get_popular(self, pages: int = 5, language: str = "en-US") -> Iterator[Dict[str, object]]:
        """Itera sobre películas populares (por páginas)."""
        for page in range(1, pages + 1):
            data = self._get("/movie/popular", {"page": page, "language": language})
            for item in data.get("results", []):
                yield item

    def get_top_rated(self, pages: int = 5, language: str = "en-US", vote_count_gte: int = 500) -> Iterator[Dict[str, object]]:
        """Itera sobre películas mejor valoradas con umbral de votos para evitar rarezas."""
        for page in range(1, pages + 1):
            data = self._get(
                "/movie/top_rated",
                {"page": page, "language": language, "vote_count.gte": vote_count_gte},
            )
            for item in data.get("results", []):
                yield item

    def discover_popular(
        self,
        pages: int,
        language: str = "en-US",
        sort_by: str = "popularity.desc",
        vote_count_gte: int = 50,
    ) -> Iterator[Dict[str, object]]:
        """Itera sobre resultados de discover ordenados por popularidad."""
        for page in range(1, pages + 1):
            data = self._get(
                "/discover/movie",
                {
                    "page": page,
                    "language": language,
                    "sort_by": sort_by,
                    "vote_count.gte": vote_count_gte,
                },
            )
            for item in data.get("results", []):
                yield item
