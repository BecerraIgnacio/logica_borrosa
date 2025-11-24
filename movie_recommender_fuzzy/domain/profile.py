from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import Interaction, Movie


@dataclass
class UserPreferenceProfile:
    """Perfil que resume las preferencias del usuario."""

    user_id: int
    genre_affinities: Dict[str, float] = field(default_factory=dict)
    preferred_rating: Optional[float] = None

    def get_genre_affinity(self, genre: str) -> float:
        """Devuelve la afinidad para un género o 0.0 si es desconocido."""
        key = genre.strip().lower()
        return self.genre_affinities.get(key, 0.0)

    def update_from_interactions(
        self, interactions: List[Interaction], movies_by_id: Dict[int, Movie]
    ) -> None:
        """Recalcula afinidades y rating preferido a partir de interacciones."""
        likes_by_genre: Dict[str, int] = {}
        dislikes_by_genre: Dict[str, int] = {}
        score_sum_by_genre: Dict[str, int] = {}
        score_count_by_genre: Dict[str, int] = {}
        liked_ratings: List[float] = []

        for interaction in interactions:
            if not interaction.is_valid_rating():
                continue

            movie = movies_by_id.get(interaction.movie_id)
            if movie is None or not movie.genres:
                continue

            score = interaction.score
            if score is not None:
                for raw in movie.genres:
                    genre = raw.strip().lower()
                    score_sum_by_genre[genre] = score_sum_by_genre.get(genre, 0) + score
                    score_count_by_genre[genre] = score_count_by_genre.get(genre, 0) + 1
                # Umbrales: 4-5 fuerte preferencia; 1-2 aversión; 3 neutro.
                if score >= 4:
                    for raw in movie.genres:
                        genre = raw.strip().lower()
                        likes_by_genre[genre] = likes_by_genre.get(genre, 0) + 1
                    if movie.rating is not None:
                        liked_ratings.append(movie.rating * (score / 5))
                elif score <= 2:
                    for raw in movie.genres:
                        genre = raw.strip().lower()
                        dislikes_by_genre[genre] = dislikes_by_genre.get(genre, 0) + 1
            else:
                if interaction.decision == Interaction.LIKE:
                    for raw in movie.genres:
                        genre = raw.strip().lower()
                        likes_by_genre[genre] = likes_by_genre.get(genre, 0) + 1
                    if movie.rating is not None:
                        liked_ratings.append(movie.rating)
                elif interaction.decision == Interaction.DISLIKE:
                    for raw in movie.genres:
                        genre = raw.strip().lower()
                        dislikes_by_genre[genre] = dislikes_by_genre.get(genre, 0) + 1

        affinities: Dict[str, float] = {}
        if score_count_by_genre:
            for genre, total_score in score_sum_by_genre.items():
                count = score_count_by_genre.get(genre, 1)
                avg = total_score / count
                # Solo contar afinidades desde 2 en adelante; 2 o menos -> 0, 5 -> 1
                if avg <= 2.0:
                    affinity = 0.0
                elif avg >= 5.0:
                    affinity = 1.0
                else:
                    affinity = (avg - 2.0) / 3.0
                affinities[genre] = max(0.0, min(1.0, affinity))
        else:
            for genre in set(likes_by_genre) | set(dislikes_by_genre):
                likes = likes_by_genre.get(genre, 0)
                dislikes = dislikes_by_genre.get(genre, 0)
                total = likes + dislikes
                if total > 0:
                    affinities[genre] = likes / total

        self.genre_affinities = affinities
        self.preferred_rating = (
            sum(liked_ratings) / len(liked_ratings) if liked_ratings else None
        )
