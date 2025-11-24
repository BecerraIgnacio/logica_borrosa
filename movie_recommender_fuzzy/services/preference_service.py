from __future__ import annotations

from typing import Dict, List, Optional

from movie_recommender_fuzzy.domain.models import Interaction, Movie
from movie_recommender_fuzzy.domain.profile import UserPreferenceProfile
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository


class PreferenceService:
    """Construye perfiles de preferencias a partir de interacciones."""

    def __init__(
        self,
        interaction_repository: InteractionRepository,
        movie_repository: MovieRepository,
    ):
        self._interaction_repository = interaction_repository
        self._movie_repository = movie_repository

    def build_user_profile(self, user_id: int, session_id: Optional[int] = None) -> UserPreferenceProfile:
        """Genera un perfil de preferencias usando las interacciones disponibles."""
        interactions: List[Interaction]
        if session_id is not None:
            interactions = self._interaction_repository.list_by_session(session_id)
        else:
            interactions = self._interaction_repository.list_by_user(user_id)

        movies_by_id: Dict[int, Movie] = {movie.id: movie for movie in self._movie_repository.list_all()}
        profile = UserPreferenceProfile(user_id=user_id)
        profile.update_from_interactions(interactions, movies_by_id)
        return profile
