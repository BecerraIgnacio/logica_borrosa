from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, List, Optional


@dataclass
class Movie:
    """Representa una película disponible para recomendar."""

    id: int
    title: str
    year: int
    genres: List[str] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    popularity: float = 0.0
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    is_top_100: bool = False


@dataclass
class User:
    """Identifica al usuario que participa en las sesiones."""

    id: int
    name: Optional[str] = None


@dataclass
class Session:
    """Sesion de valoración de películas por un usuario."""

    ACTIVE: ClassVar[str] = "ACTIVE"
    COMPLETED: ClassVar[str] = "COMPLETED"

    id: int
    user_id: int
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    target_ratings: int = 20
    valid_ratings_count: int = 0
    status: str = ACTIVE

    def is_completed(self) -> bool:
        """Indica si se alcanzaron las valoraciones requeridas."""
        return self.valid_ratings_count >= self.target_ratings

    def increment_valid_ratings(self) -> None:
        """Incrementa el contador de valoraciones válidas."""
        self.valid_ratings_count += 1

    def mark_completed(self) -> None:
        """Marca la sesión como completada y registra su cierre."""
        self.status = self.COMPLETED
        if self.finished_at is None:
            self.finished_at = datetime.now()


@dataclass
class Interaction:
    """Decisión del usuario sobre una película dentro de una sesión."""

    LIKE: ClassVar[str] = "LIKE"
    DISLIKE: ClassVar[str] = "DISLIKE"
    NOT_SEEN: ClassVar[str] = "NOT_SEEN"

    id: int
    user_id: int
    movie_id: int
    session_id: int
    decision: str = NOT_SEEN
    score: Optional[int] = None  # escala 1-5
    timestamp: datetime = field(default_factory=datetime.now)

    def is_valid_rating(self) -> bool:
        """Determina si la decisión cuenta como valoración."""
        if self.score is not None:
            return True
        return self.decision in (self.LIKE, self.DISLIKE)
