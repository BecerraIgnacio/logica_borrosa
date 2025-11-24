from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from movie_recommender_fuzzy.domain.models import Interaction, Movie
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository
from movie_recommender_fuzzy.infra.session_repository import SessionRepository
from movie_recommender_fuzzy.services.fuzzy_engine import FuzzyEngine
from movie_recommender_fuzzy.services.preference_service import PreferenceService
from movie_recommender_fuzzy.services.recommendation_service import RecommendationService
from movie_recommender_fuzzy.services.session_service import SessionService


def load_movies(path: Path) -> List[Movie]:
    """Carga películas desde un JSON compatible con el modelo Movie."""
    data = json.loads(path.read_text(encoding="utf-8"))
    movies: List[Movie] = []
    for item in data:
        movies.append(
            Movie(
                id=int(item["id"]),
                title=str(item.get("title", "")),
                year=int(item.get("year", 0)),
                genres=list(item.get("genres") or []),
                duration_minutes=item.get("duration_minutes"),
                popularity=float(item.get("popularity", 0.0)),
                rating=float(item["rating"]) if item.get("rating") is not None else None,
                poster_url=item.get("poster_url"),
                is_top_100=bool(item.get("is_top_100", False)),
            )
        )
    return movies


def bootstrap_repositories(movies: Iterable[Movie]) -> tuple[MovieRepository, SessionRepository, InteractionRepository]:
    """Inicializa repositorios en memoria y carga películas."""
    db = InMemoryDB()
    movie_repo = MovieRepository(db)
    movie_repo.add_movies(movies)
    session_repo = SessionRepository(db)
    interaction_repo = InteractionRepository(db)
    return movie_repo, session_repo, interaction_repo


def simulate_session(session_service: SessionService, top_movies: List[Movie]) -> int:
    """Crea una sesión y registra 20 valoraciones (Like/Dislike) sobre el top 100."""
    session = session_service.start_session(user_id=1, target_ratings=20)
    decisions = []
    # Alterna likes y dislikes para generar un perfil simple pero reproducible.
    for idx, movie in enumerate(top_movies[:20]):
        decision = Interaction.LIKE if idx % 3 != 0 else Interaction.DISLIKE
        session_service.register_decision(session.id, movie.id, decision)
        decisions.append((movie.title, decision))
    return session.id


def main() -> None:
    data_path = Path(__file__).resolve().parent / "data" / "movies.json"
    if not data_path.exists():
        raise SystemExit(f"No se encontró el catálogo en {data_path}. Ejecuta el loader TMDb primero.")

    movies = load_movies(data_path)
    movie_repo, session_repo, interaction_repo = bootstrap_repositories(movies)

    session_service = SessionService(session_repo, interaction_repo, movie_repo)
    preference_service = PreferenceService(interaction_repo, movie_repo)
    fuzzy_engine = FuzzyEngine()
    recommendation_service = RecommendationService(
        movie_repository=movie_repo,
        interaction_repository=interaction_repo,
        preference_service=preference_service,
        fuzzy_engine=fuzzy_engine,
    )

    top_pool = movie_repo.list_top_popular(limit=100)
    if len(top_pool) < 20:
        raise SystemExit("No hay suficientes películas en el pool top 100 para simular la sesión.")

    session_id = simulate_session(session_service, top_pool)
    recommendations = recommendation_service.recommend_movies(user_id=1, session_id=session_id, k=10)

    print("\n=== Recomendaciones calculadas ===")
    for idx, (movie, score) in enumerate(recommendations, start=1):
        print(f"{idx:02d}. {movie.title} ({movie.year}) – score={score:.3f}")


if __name__ == "__main__":
    main()
