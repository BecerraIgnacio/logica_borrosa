from movie_recommender_fuzzy.domain.models import Interaction, Movie
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository
from movie_recommender_fuzzy.infra.session_repository import SessionRepository
from movie_recommender_fuzzy.services.fuzzy_engine import FuzzyEngine
from movie_recommender_fuzzy.services.preference_service import PreferenceService
from movie_recommender_fuzzy.services.recommendation_service import RecommendationService


def build_recommendation_service():
    db = InMemoryDB()
    movie_repo = MovieRepository(db)
    movies = [
        Movie(
            id=1,
            title="Action One",
            year=2020,
            genres=["Action"],
            rating=8.0,
            popularity=0.9,
            is_top_100=True,
        ),
        Movie(
            id=2,
            title="Romantic Drama",
            year=2019,
            genres=["Romance"],
            rating=7.5,
            popularity=0.7,
            is_top_100=True,
        ),
        Movie(
            id=3,
            title="Sci-Fi Epic",
            year=2021,
            genres=["Sci-Fi"],
            rating=8.5,
            popularity=0.8,
            is_top_100=True,
        ),
        Movie(id=4, title="Action Two", year=2022, genres=["Action"], rating=7.0, popularity=0.6),
        Movie(id=5, title="Comedy Fun", year=2018, genres=["Comedy"], rating=6.0, popularity=0.5),
    ]
    movie_repo.add_movies(movies)

    session_repo = SessionRepository(db)
    interaction_repo = InteractionRepository(db)
    preference_service = PreferenceService(interaction_repo, movie_repo)
    fuzzy_engine = FuzzyEngine()
    recommendation_service = RecommendationService(
        movie_repository=movie_repo,
        interaction_repository=interaction_repo,
        preference_service=preference_service,
        fuzzy_engine=fuzzy_engine,
    )
    return recommendation_service, interaction_repo, session_repo


def test_recommendations_exclude_rated_and_prioritize_affinity():
    recommendation_service, interaction_repo, session_repo = build_recommendation_service()
    session = session_repo.create(user_id=1, target_ratings=3)

    interactions = [
        Interaction(
            id=interaction_repo.next_id(),
            user_id=1,
            movie_id=1,
            session_id=session.id,
            decision=Interaction.LIKE,
        ),
        Interaction(
            id=interaction_repo.next_id(),
            user_id=1,
            movie_id=2,
            session_id=session.id,
            decision=Interaction.DISLIKE,
        ),
        Interaction(
            id=interaction_repo.next_id(),
            user_id=1,
            movie_id=3,
            session_id=session.id,
            decision=Interaction.LIKE,
        ),
    ]
    for interaction in interactions:
        interaction_repo.add(interaction)

    recommendations = recommendation_service.recommend_movies(user_id=1, session_id=session.id, k=2)
    movie_ids = [movie.id for movie, _score in recommendations]

    # Películas ya valoradas (1,2,3) no deben aparecer.
    assert all(movie_id not in (1, 2, 3) for movie_id in movie_ids)
    # Afinidades fuertes con Action/Sci-Fi deben priorizar la siguiente de Action sobre Comedy.
    assert movie_ids == [4, 5]
