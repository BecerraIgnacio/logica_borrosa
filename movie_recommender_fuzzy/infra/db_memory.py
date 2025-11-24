from __future__ import annotations

from dataclasses import dataclass, field

from movie_recommender_fuzzy.domain.models import Interaction, Movie, Session


@dataclass
class InMemoryDB:
    """Almacenamiento simple en memoria para entidades de dominio."""

    movies: Dict[int, Movie] = field(default_factory=dict)
    sessions: Dict[int, Session] = field(default_factory=dict)
    interactions: Dict[int, Interaction] = field(default_factory=dict)
    _session_counter: int = 1
    _interaction_counter: int = 1

    def next_session_id(self) -> int:
        """Obtiene un nuevo identificador de sesión consecutivo."""
        current = self._session_counter
        self._session_counter += 1
        return current

    def next_interaction_id(self) -> int:
        """Obtiene un nuevo identificador de interacción consecutivo."""
        current = self._interaction_counter
        self._interaction_counter += 1
        return current
