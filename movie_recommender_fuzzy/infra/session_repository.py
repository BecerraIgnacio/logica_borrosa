from __future__ import annotations

from typing import List, Optional

from movie_recommender_fuzzy.domain.models import Session
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB


class SessionRepository:
    """Repositorio en memoria para sesiones de valoración."""

    def __init__(self, db: InMemoryDB):
        self._db = db

    def create(self, user_id: int, target_ratings: int = 20) -> Session:
        """Crea y almacena una sesión nueva para el usuario."""
        session_id = self._db.next_session_id()
        session = Session(
            id=session_id,
            user_id=user_id,
            target_ratings=target_ratings,
        )
        self._db.sessions[session_id] = session
        return session

    def add(self, session: Session) -> Session:
        """Guarda una sesión existente (útil para restaurar desde otro medio)."""
        self._db.sessions[session.id] = session
        return session

    def get(self, session_id: int) -> Optional[Session]:
        """Obtiene una sesión por identificador."""
        return self._db.sessions.get(session_id)

    def list_by_user(self, user_id: int) -> List[Session]:
        """Devuelve las sesiones asociadas a un usuario."""
        return [session for session in self._db.sessions.values() if session.user_id == user_id]

    def update(self, session: Session) -> Session:
        """Persiste los cambios de una sesión."""
        self._db.sessions[session.id] = session
        return session
