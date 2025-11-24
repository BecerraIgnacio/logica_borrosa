from __future__ import annotations

import random
from typing import Optional

from movie_recommender_fuzzy.domain.models import Interaction, Movie, Session
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository
from movie_recommender_fuzzy.infra.session_repository import SessionRepository


class SessionService:
    """Gestiona el ciclo de vida de una sesión de valoración."""

    def __init__(
        self,
        session_repository: SessionRepository,
        interaction_repository: InteractionRepository,
        movie_repository: MovieRepository,
    ):
        self._session_repository = session_repository
        self._interaction_repository = interaction_repository
        self._movie_repository = movie_repository

    def start_session(self, user_id: int, target_ratings: int = 20) -> Session:
        """Crea una nueva sesión para el usuario."""
        return self._session_repository.create(user_id=user_id, target_ratings=target_ratings)

    def get_next_movie(self, session_id: int, filters: Optional[dict] = None) -> Optional[Movie]:
        """Obtiene la siguiente película no valorada en la sesión desde el pool top 100."""
        session = self._session_repository.get(session_id)
        if session is None or session.is_completed():
            return None

        rated_ids = set(self._interaction_repository.list_movie_ids_by_session(session_id))
        candidates = self._movie_repository.list_top_excluding(rated_ids, limit=100)

        if filters:
            genres = [g.strip().lower() for g in filters.get("genres", []) if g]
            duration = filters.get("duration") or ""

            def match_genres(movie: Movie) -> bool:
                if not genres:
                    return True
                return any(g in movie.genres for g in genres)

            def match_duration(movie: Movie) -> bool:
                if not duration:
                    return True
                if movie.duration_minutes is None:
                    return False
                if duration == "short":
                    return movie.duration_minutes < 100
                if duration == "medium":
                    return 100 <= movie.duration_minutes <= 140
                if duration == "long":
                    return movie.duration_minutes > 140
                return True

            candidates = [m for m in candidates if match_genres(m) and match_duration(m)]

        if not candidates:
            return None
        return random.choice(candidates)

    def register_decision(
        self, session_id: int, movie_id: int, decision: str, score: Optional[int] = None
    ) -> Optional[Interaction]:
        """Registra la decisión del usuario y actualiza el estado de la sesión."""
        session = self._session_repository.get(session_id)
        if session is None or session.is_completed():
            return None

        movie = self._movie_repository.get(movie_id)
        if movie is None:
            return None

        interaction = Interaction(
            id=self._interaction_repository.next_id(),
            user_id=session.user_id,
            movie_id=movie_id,
            session_id=session_id,
            decision=decision,
            score=score,
        )
        self._interaction_repository.add(interaction)

        if interaction.is_valid_rating():
            session.increment_valid_ratings()
            if session.is_completed():
                session.mark_completed()

        self._session_repository.update(session)
        return interaction
