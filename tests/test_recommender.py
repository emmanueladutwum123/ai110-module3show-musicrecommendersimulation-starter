from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    BalancedStrategy,
    EnergyFocusedStrategy,
    GenreOnlyStrategy,
    recommend_songs,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def _flip_case_songs():
    """Two songs engineered so genre-heavy vs. energy-heavy weighting disagree
    on the winner: one matches genre with a looser energy fit, the other
    matches mood with a very tight energy fit but no genre match."""
    genre_match_loose_energy = Song(
        id=1, title="Genre Match", artist="A", genre="pop", mood="sad",
        energy=0.95, tempo_bpm=120, valence=0.5, danceability=0.5, acousticness=0.1,
    )
    mood_match_tight_energy = Song(
        id=2, title="Mood Match", artist="B", genre="indie", mood="happy",
        energy=0.82, tempo_bpm=120, valence=0.5, danceability=0.5, acousticness=0.1,
    )
    return [genre_match_loose_energy, mood_match_tight_energy]


def test_balanced_strategy_favors_genre_match():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    rec = Recommender(_flip_case_songs(), strategy=BalancedStrategy())
    top = rec.recommend(user, k=1)[0]
    assert top.genre == "pop"


def test_energy_focused_strategy_can_flip_the_ranking():
    """Same songs, same user — a different strategy produces a different winner.
    This is the point of the Strategy pattern: behavior changes by substitution,
    not by editing Recommender or recommend_songs."""
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    rec = Recommender(_flip_case_songs(), strategy=EnergyFocusedStrategy())
    top = rec.recommend(user, k=1)[0]
    assert top.mood == "happy"
    assert top.genre != "pop"


def test_genre_only_strategy_ignores_mood_and_energy():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    rec = Recommender(_flip_case_songs(), strategy=GenreOnlyStrategy())
    top = rec.recommend(user, k=1)[0]
    # The pop song wins even though its mood/energy are worse — genre is all that counts.
    assert top.genre == "pop"
    score, reasons = rec.strategy.score(
        {"favorite_genre": "indie", "favorite_mood": "happy", "target_energy": 0.8}, {"genre": "pop"}
    )
    assert score == 0.0
    assert reasons == ["no genre match"]


def test_recommend_songs_functional_api_accepts_a_strategy():
    """The dict-based functional API also honors a custom strategy, not just the OOP one."""
    user_prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}
    songs = [
        {"title": "A", "genre": "pop", "mood": "sad", "energy": 0.95, "acousticness": 0.1},
        {"title": "B", "genre": "indie", "mood": "happy", "energy": 0.82, "acousticness": 0.1},
    ]
    balanced_top = recommend_songs(user_prefs, songs, k=1, strategy=BalancedStrategy())[0][0]
    energy_top = recommend_songs(user_prefs, songs, k=1, strategy=EnergyFocusedStrategy())[0][0]
    assert balanced_top["title"] == "A"
    assert energy_top["title"] == "B"
