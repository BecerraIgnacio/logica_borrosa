from movie_recommender_fuzzy.services.fuzzy_engine import FuzzyEngine


def test_high_inputs_return_high_relevance():
    score = FuzzyEngine.compute_relevance(1.0, 1.0, 1.0)
    assert score > 0.8


def test_low_inputs_return_low_relevance():
    score = FuzzyEngine.compute_relevance(0.0, 0.0, 0.0)
    assert score < 0.3


def test_mixed_inputs_are_intermediate():
    score = FuzzyEngine.compute_relevance(0.5, 0.6, 0.5)
    assert 0.3 < score < 0.8
