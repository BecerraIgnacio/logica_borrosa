from __future__ import annotations

from typing import List, Optional

from movie_recommender_fuzzy.domain.models import Interaction
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB


class InteractionRepository:
    """Repositorio de interacciones en memoria."""

    def __init__(self, db: InMemoryDB):
        self._db = db

    def next_id(self) -> int:
        """Entrega un nuevo identificador para interacciones."""
        return self._db.next_interaction_id()

    def add(self, interaction: Interaction) -> Interaction:
        """Almacena una interacción y devuelve la instancia guardada."""
        self._db.interactions[interaction.id] = interaction
        return interaction

    def get(self, interaction_id: int) -> Optional[Interaction]:
        """Obtiene una interacción por id."""
        return self._db.interactions.get(interaction_id)

    def list_by_session(self, session_id: int) -> List[Interaction]:
        """Devuelve las interacciones asociadas a una sesión."""
        return [
            interaction
            for interaction in self._db.interactions.values()
            if interaction.session_id == session_id
        ]

    def list_by_user(self, user_id: int) -> List[Interaction]:
        """Devuelve las interacciones realizadas por un usuario."""
        return [
            interaction
            for interaction in self._db.interactions.values()
            if interaction.user_id == user_id
        ]

    def list_movie_ids_by_session(self, session_id: int) -> List[int]:
        """Devuelve los ids de películas ya valoradas en la sesión."""
        return [interaction.movie_id for interaction in self.list_by_session(session_id)]
