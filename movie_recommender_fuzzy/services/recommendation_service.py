from __future__ import annotations

from typing import List, Tuple

from movie_recommender_fuzzy.domain.models import Movie
from movie_recommender_fuzzy.domain.profile import UserPreferenceProfile
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository
from movie_recommender_fuzzy.services.fuzzy_engine import FuzzyEngine
from movie_recommender_fuzzy.services.preference_service import PreferenceService


class RecommendationService:
    """Genera recomendaciones de películas usando lógica difusa."""

    def __init__(
        self,
        movie_repository: MovieRepository,
        interaction_repository: InteractionRepository,
        preference_service: PreferenceService,
        fuzzy_engine: FuzzyEngine,
    ):
        self._movie_repository = movie_repository
        self._interaction_repository = interaction_repository
        self._preference_service = preference_service
        self._fuzzy_engine = fuzzy_engine

    def recommend_movies(
        self,
        user_id: int,
        session_id: int,
        k: int = 10,
        include_breakdown: bool = False,
        filters: Optional[dict] = None,
    ) -> List[Tuple[Movie, float] | Tuple[Movie, float, dict]]:
        """Calcula las k mejores películas para el usuario en la sesión dada."""
        rated_ids = set(self._interaction_repository.list_movie_ids_by_session(session_id))
        profile = self._preference_service.build_user_profile(user_id, session_id=session_id)
        catalog = self._movie_repository.list_catalog(limit=1000)
        candidates = [movie for movie in catalog if movie.id not in rated_ids]

        def matches_filters(movie: Movie) -> bool:
            if not filters:
                return True
            genres = [g.strip().lower() for g in filters.get("genres", []) if g]
            duration = filters.get("duration") or ""
            if genres and not any(g in movie.genres for g in genres):
                return False
            if duration and movie.duration_minutes is not None:
                if duration == "short" and movie.duration_minutes >= 100:
                    return False
                if duration == "medium" and not (100 <= movie.duration_minutes <= 140):
                    return False
                if duration == "long" and movie.duration_minutes <= 140:
                    return False
            return True

        candidates = [m for m in candidates if matches_filters(m)]

        scored_with_affinity: List[Tuple[Movie, float, float, dict | None]] = []
        for movie in candidates:
            affinity = self._compute_affinity(movie, profile)
            popularity = self._normalize_popularity(movie.popularity)
            rating_similarity = self._rating_similarity(movie, profile)
            if include_breakdown:
                relevance, detail = self._fuzzy_engine.compute_relevance_with_breakdown(
                    affinity, popularity, rating_similarity
                )
                detail.update(
                    {
                        "affinity": affinity,
                        "popularity_norm": popularity,
                        "rating_similarity": rating_similarity,
                    }
                )
                scored_with_affinity.append((movie, relevance, affinity, detail))
            else:
                relevance = self._fuzzy_engine.compute_relevance(affinity, popularity, rating_similarity)
                scored_with_affinity.append((movie, relevance, affinity, None))

        # Ordenar priorizando afinidad, luego relevancia.
        scored_with_affinity.sort(key=lambda item: (item[2], item[1]), reverse=True)

        selected: List[Tuple[Movie, float] | Tuple[Movie, float, dict]] = []
        for movie, relevance, affinity, detail in scored_with_affinity[:k]:
            entry = (movie, relevance, detail) if include_breakdown else (movie, relevance)
            selected.append(entry)

        return selected

    def _compute_affinity(self, movie: Movie, profile: UserPreferenceProfile) -> float:
        """Calcula afinidad ponderando solo géneros presentes en el perfil (normalizados)."""
        if not movie.genres:
            return 0.0

        normalized = [g.strip().lower() for g in movie.genres if g]
        scored = [(genre, profile.get_genre_affinity(genre)) for genre in normalized]
        overlapping = [score for _g, score in scored if score > 0]
        if not overlapping:
            return 0.0

        best = max(overlapping)
        coverage = len(overlapping) / len(normalized)
        return best * coverage

    def _normalize_popularity(self, popularity: float) -> float:
        """Asegura que la popularidad esté en [0,1], normalizando si viene en 0–100."""
        if popularity > 1:
            return min(1.0, max(0.0, popularity / 100.0))
        return min(1.0, max(0.0, popularity))

    def _rating_similarity(self, movie: Movie, profile: UserPreferenceProfile) -> float:
        """Calcula similitud de rating respecto al rating preferido del usuario."""
        if movie.rating is None or profile.preferred_rating is None:
            return 0.5

        diff = abs(movie.rating - profile.preferred_rating)
        max_diff = 5.0
        similarity = 1 - (diff / max_diff)
        return max(0.0, min(1.0, similarity))
