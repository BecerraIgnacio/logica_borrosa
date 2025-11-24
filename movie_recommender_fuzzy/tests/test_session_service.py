from movie_recommender_fuzzy.domain.models import Interaction, Movie, Session
from movie_recommender_fuzzy.infra.db_memory import InMemoryDB
from movie_recommender_fuzzy.infra.interaction_repository import InteractionRepository
from movie_recommender_fuzzy.infra.movie_repository import MovieRepository
from movie_recommender_fuzzy.infra.session_repository import SessionRepository
from movie_recommender_fuzzy.services.session_service import SessionService


def build_service_with_movies():
    db = InMemoryDB()
    movie_repo = MovieRepository(db)
    movie_repo.add_movies(
        [
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
                title="Drama Story",
                year=2019,
                genres=["Drama"],
                rating=7.0,
                popularity=0.6,
                is_top_100=True,
            ),
            Movie(
                id=3,
                title="Comedy Time",
                year=2021,
                genres=["Comedy"],
                rating=6.5,
                popularity=0.5,
                is_top_100=True,
            ),
        ]
    )
    session_repo = SessionRepository(db)
    interaction_repo = InteractionRepository(db)
    service = SessionService(session_repo, interaction_repo, movie_repo)
    return service, session_repo, interaction_repo


def test_session_flow_marks_completion():
    service, session_repo, interaction_repo = build_service_with_movies()
    session = service.start_session(user_id=42, target_ratings=2)

    first_movie = service.get_next_movie(session.id)
    assert first_movie is not None
    service.register_decision(session.id, first_movie.id, Interaction.LIKE)

    second_movie = service.get_next_movie(session.id)
    assert second_movie is not None
    service.register_decision(session.id, second_movie.id, Interaction.DISLIKE)

    updated = session_repo.get(session.id)
    assert updated is not None
    assert updated.valid_ratings_count == 2
    assert updated.is_completed()
    assert updated.status == Session.COMPLETED

    # No more movies should be served once completed.
    assert service.get_next_movie(session.id) is None
