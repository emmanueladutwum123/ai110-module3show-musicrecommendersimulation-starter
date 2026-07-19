import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# --- Scoring weights (see README "Algorithm Recipe") ---
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_core(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Shared scoring recipe used by both the dict-based and dataclass-based APIs."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT})")

    # Closeness, not magnitude: a song near the target energy scores well
    # regardless of whether it's the highest- or lowest-energy track around.
    energy_gap = abs(float(song["energy"]) - float(user_prefs["target_energy"]))
    energy_points = ENERGY_WEIGHT * (1 - energy_gap)
    if energy_points > 0:
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") and float(song["acousticness"]) >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic match (+{ACOUSTIC_BONUS})")

    if not reasons:
        reasons.append("no strong matches")

    return round(score, 2), reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for this user, ranked highest score first."""
        user_prefs = asdict(user)
        scored = [(song, _score_core(user_prefs, asdict(song))[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation of why a song scored the way it did."""
        user_prefs = asdict(user)
        score, reasons = _score_core(user_prefs, asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts, with numeric fields as floats/ints."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against a user_prefs dict; returns (score, reasons)."""
    return _score_core(user_prefs, song)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, ranks them, and returns the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
