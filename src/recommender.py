import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Default scoring weights for BalancedStrategy (see README "Algorithm Recipe") ---
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


class ScoringStrategy(ABC):
    """
    Strategy pattern interface: any scoring algorithm that can judge a song
    against a user's preferences. Recommender and recommend_songs() depend
    only on this interface, so swapping strategies changes *how* songs are
    judged without touching the ranking/CLI code at all.
    """

    @abstractmethod
    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Scores one song dict against a user_prefs dict; returns (score, reasons)."""
        raise NotImplementedError


class BalancedStrategy(ScoringStrategy):
    """
    The project's default recipe: genre match, mood match, energy closeness,
    and an acoustic-preference bonus, each independently weighted. See
    README "Algorithm Recipe" for the reasoning behind the default weights.
    """

    def __init__(
        self,
        genre_weight: float = GENRE_WEIGHT,
        mood_weight: float = MOOD_WEIGHT,
        energy_weight: float = ENERGY_WEIGHT,
        acoustic_bonus: float = ACOUSTIC_BONUS,
        acoustic_threshold: float = ACOUSTIC_THRESHOLD,
    ):
        self.genre_weight = genre_weight
        self.mood_weight = mood_weight
        self.energy_weight = energy_weight
        self.acoustic_bonus = acoustic_bonus
        self.acoustic_threshold = acoustic_threshold

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Weighted-sum scoring across genre, mood, energy closeness, and acousticness."""
        score = 0.0
        reasons: List[str] = []

        if song["genre"] == user_prefs["favorite_genre"]:
            score += self.genre_weight
            reasons.append(f"genre match (+{self.genre_weight})")

        if song["mood"] == user_prefs["favorite_mood"]:
            score += self.mood_weight
            reasons.append(f"mood match (+{self.mood_weight})")

        # Closeness, not magnitude: a song near the target energy scores well
        # regardless of whether it's the highest- or lowest-energy track around.
        energy_gap = abs(float(song["energy"]) - float(user_prefs["target_energy"]))
        energy_points = self.energy_weight * (1 - energy_gap)
        if energy_points > 0:
            score += energy_points
            reasons.append(f"energy closeness (+{energy_points:.2f})")

        if user_prefs.get("likes_acoustic") and float(song["acousticness"]) >= self.acoustic_threshold:
            score += self.acoustic_bonus
            reasons.append(f"acoustic match (+{self.acoustic_bonus})")

        if not reasons:
            reasons.append("no strong matches")

        return round(score, 2), reasons


class EnergyFocusedStrategy(BalancedStrategy):
    """
    Phase 4's weight-shift experiment, made a permanent, reusable strategy
    instead of a one-off runtime patch: energy closeness matters twice as
    much as genre, instead of the reverse.
    """

    def __init__(self):
        super().__init__(genre_weight=1.0, mood_weight=1.0, energy_weight=3.0)


class GenreOnlyStrategy(ScoringStrategy):
    """
    Minimal baseline strategy that ignores mood, energy, and acoustic
    preference entirely — useful for isolating how much those other signals
    actually change a recommendation versus genre alone.
    """

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Scores purely on genre match; every other signal is ignored."""
        if song["genre"] == user_prefs["favorite_genre"]:
            return 1.0, ["genre match (+1.0)"]
        return 0.0, ["no genre match"]


DEFAULT_STRATEGY = BalancedStrategy()


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song], strategy: Optional[ScoringStrategy] = None):
        self.songs = songs
        self.strategy = strategy or DEFAULT_STRATEGY

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for this user, ranked highest score first."""
        user_prefs = asdict(user)
        scored = [(song, self.strategy.score(user_prefs, asdict(song))[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation of why a song scored the way it did."""
        user_prefs = asdict(user)
        score, reasons = self.strategy.score(user_prefs, asdict(song))
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


def score_song(
    user_prefs: Dict, song: Dict, strategy: Optional[ScoringStrategy] = None
) -> Tuple[float, List[str]]:
    """Scores a single song dict against a user_prefs dict using the given strategy (default: balanced)."""
    return (strategy or DEFAULT_STRATEGY).score(user_prefs, song)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, strategy: Optional[ScoringStrategy] = None
) -> List[Tuple[Dict, float, str]]:
    """Scores every song with the given strategy, ranks them, and returns the top k."""
    active_strategy = strategy or DEFAULT_STRATEGY
    scored = [(song, *active_strategy.score(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
