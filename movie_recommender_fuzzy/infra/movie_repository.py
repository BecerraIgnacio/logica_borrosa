from __future__ import annotations

from typing import Iterable, List, Set

from movie_recommender_fuzzy.domain.models import Movie
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB


class MovieRepository:
    """Repositorio de películas sobre almacenamiento en memoria."""

    def __init__(self, db: InMemoryDB):
        self._db = db

    def add_movies(self, movies: Iterable[Movie]) -> None:
        """Carga un conjunto de películas en el almacenamiento."""
        for movie in movies:
            self._db.movies[movie.id] = movie

    def add_movie(self, movie: Movie) -> None:
        """Agrega o reemplaza una película."""
        self._db.movies[movie.id] = movie

    def get(self, movie_id: int) -> Optional[Movie]:
        """Obtiene una película por su identificador."""
        return self._db.movies.get(movie_id)

    def list_all(self) -> List[Movie]:
        """Devuelve todas las películas conocidas."""
        return list(self._db.movies.values())

    def list_catalog(self, limit: int = 1000) -> List[Movie]:
        """Devuelve el catálogo principal limitado a las más populares."""
        ordered = sorted(self._db.movies.values(), key=lambda movie: movie.popularity, reverse=True)
        return ordered[:limit]

    def list_top_popular(self, limit: int = 100) -> List[Movie]:
        """Devuelve el pool de las películas más populares (top 100 por defecto)."""
        flagged = sorted(
            (movie for movie in self._db.movies.values() if movie.is_top_100),
            key=lambda movie: movie.popularity,
            reverse=True,
        )
        if len(flagged) >= limit:
            return flagged[:limit]

        remaining_slots = limit - len(flagged)
        others = sorted(
            (movie for movie in self._db.movies.values() if not movie.is_top_100),
            key=lambda movie: movie.popularity,
            reverse=True,
        )
        combined = flagged + others
        return combined[:limit]

    def list_excluding(self, excluded_ids: Set[int]) -> List[Movie]:
        """Devuelve películas cuyo id no se encuentra en el conjunto dado."""
        return [movie for movie_id, movie in self._db.movies.items() if movie_id not in excluded_ids]

    def list_top_excluding(self, excluded_ids: Set[int], limit: int = 100) -> List[Movie]:
        """Devuelve las más populares excluyendo ids dados."""
        return [movie for movie in self.list_top_popular(limit=limit) if movie.id not in excluded_ids]
