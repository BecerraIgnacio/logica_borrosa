from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from flask import Flask, redirect, render_template, request, session, url_for

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
    """Carga películas desde el JSON generado."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el catálogo en {path}. Ejecuta el loader TMDb primero.")

    data = json.loads(path.read_text(encoding="utf-8"))
    movies: List[Movie] = []
    for item in data:
        movies.append(
            Movie(
                id=int(item["id"]),
                title=str(item.get("title", "")),
                year=int(item.get("year", 0)),
                genres=[g.strip().lower() for g in (item.get("genres") or []) if g],
                duration_minutes=item.get("duration_minutes"),
                popularity=float(item.get("popularity", 0.0)),
                rating=float(item["rating"]) if item.get("rating") is not None else None,
                poster_url=item.get("poster_url"),
                is_top_100=bool(item.get("is_top_100", False)),
            )
        )
    return movies


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    data_path = Path(__file__).resolve().parents[2] / "movie_recommender_fuzzy" / "data" / "movies.json"
    movies = load_movies(data_path)

    db = InMemoryDB()
    movie_repo = MovieRepository(db)
    movie_repo.add_movies(movies)
    session_repo = SessionRepository(db)
    interaction_repo = InteractionRepository(db)

    all_genres = sorted({genre for movie in movies for genre in movie.genres})

    session_service = SessionService(session_repo, interaction_repo, movie_repo)
    preference_service = PreferenceService(interaction_repo, movie_repo)
    fuzzy_engine = FuzzyEngine()
    recommendation_service = RecommendationService(
        movie_repository=movie_repo,
        interaction_repository=interaction_repo,
        preference_service=preference_service,
        fuzzy_engine=fuzzy_engine,
    )

    def get_session_id() -> Optional[int]:
        raw = session.get("session_id")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    @app.route("/")
    def home():
        current_session_id = get_session_id()
        current_session = session_repo.get(current_session_id) if current_session_id else None
        return render_template("home.html", session=current_session)

    @app.route("/filters", methods=["GET", "POST"])
    def filters():
        if request.method == "POST":
            selected_genres = request.form.getlist("genres")
            duration = request.form.get("duration") or ""
            session["filters"] = {
                "genres": [g.strip().lower() for g in selected_genres if g],
                "duration": duration,
            }
            return redirect(url_for("start"))

        filters_data = session.get("filters", {"genres": [], "duration": ""})
        return render_template(
            "filters.html",
            genres=all_genres,
            selected_genres=filters_data.get("genres", []),
            selected_duration=filters_data.get("duration", ""),
        )

    @app.route("/start")
    def start():
        session_obj = session_service.start_session(user_id=1, target_ratings=20)
        session["session_id"] = session_obj.id
        if "filters" not in session:
            session["filters"] = {"genres": [], "duration": ""}
        return redirect(url_for("swipe"))

    @app.route("/swipe", methods=["GET", "POST"])
    def swipe():
        current_session_id = get_session_id()
        if current_session_id is None:
            return redirect(url_for("start"))

        current_session = session_repo.get(current_session_id)
        if current_session is None:
            return redirect(url_for("start"))

        if request.method == "POST":
            decision_values = request.form.getlist("decision")
            decision = decision_values[-1] if decision_values else None
            movie_id = request.form.get("movie_id")
            score_raw = request.form.get("score")
            score_val: Optional[int] = None
            if score_raw:
                try:
                    score_val = int(score_raw)
                except ValueError:
                    score_val = None
            if decision == Interaction.NOT_SEEN:
                score_val = None
            if decision and movie_id:
                try:
                    movie_int = int(movie_id)
                except ValueError:
                    movie_int = None
                if movie_int is not None:
                    session_service.register_decision(current_session_id, movie_int, decision, score=score_val)
            current_session = session_repo.get(current_session_id)
            if current_session.is_completed():
                return redirect(url_for("results"))

        filters_data = session.get("filters", {"genres": [], "duration": ""})
        movie = session_service.get_next_movie(current_session_id, filters=filters_data)
        if movie is None:
            return redirect(url_for("results"))

        progress = {
            "current": current_session.valid_ratings_count,
            "target": current_session.target_ratings,
        }
        min_for_recs = 5
        remaining_for_recs = max(0, min_for_recs - current_session.valid_ratings_count)
        return render_template(
            "swipe.html",
            movie=movie,
            progress=progress,
            session=current_session,
            remaining_for_recs=remaining_for_recs,
            min_for_recs=min_for_recs,
            like_value=Interaction.LIKE,
            dislike_value=Interaction.DISLIKE,
            skip_value=Interaction.NOT_SEEN,
            filters=filters_data,
        )

    @app.route("/results", methods=["GET", "POST"])
    def results():
        current_session_id = get_session_id()
        if current_session_id is None:
            return redirect(url_for("start"))

        current_session = session_repo.get(current_session_id)
        if current_session is None:
            return redirect(url_for("start"))

        if current_session.valid_ratings_count < 5:
            return redirect(url_for("swipe"))

        if request.method == "POST":
            movie_id = request.form.get("movie_id")
            score_raw = request.form.get("score")
            score_val: Optional[int] = None
            try:
                score_val = int(score_raw) if score_raw else None
            except ValueError:
                score_val = None
            movie_int: Optional[int] = None
            try:
                movie_int = int(movie_id) if movie_id else None
            except ValueError:
                movie_int = None
            if movie_int is not None and score_val:
                interaction = Interaction(
                    id=interaction_repo.next_id(),
                    user_id=current_session.user_id,
                    movie_id=movie_int,
                    session_id=current_session.id,
                    decision=Interaction.LIKE,
                    score=score_val,
                )
                interaction_repo.add(interaction)

        filters_data = session.get("filters", {"genres": [], "duration": ""})
        recs = recommendation_service.recommend_movies(
            user_id=1, session_id=current_session_id, k=10, include_breakdown=True, filters=filters_data
        )
        return render_template("results.html", recommendations=recs, session=current_session)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=int(os.getenv("PORT", "5000")))
