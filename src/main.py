"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

Uses the functional API from recommender.py:
- load_songs
- score_song (used internally by recommend_songs)
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# Default profile — see README "Algorithm Recipe" for how this is scored.
DEFAULT_PROFILE = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.8,
    "likes_acoustic": False,
}

# Phase 4 stress-test profiles — three distinct "normal" tastes plus two
# adversarial ones designed to probe conflicting or missing preferences.
# Results/analysis documented in README "Experiments You Tried" and
# model_card.md "Evaluation".
EVAL_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Adversarial: Happy Metal (conflicting genre/mood)": {
        "favorite_genre": "metal",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Adversarial: Unknown Genre (not in catalog)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.7,
        "likes_acoustic": False,
    },
}


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Prints a labeled, ranked, explained top-k recommendation list for one profile."""
    print(f"\n=== {label} ===")
    print(f"Profile: {user_prefs}")
    for song, score, explanation in recommend_songs(user_prefs, songs, k=k):
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print_recommendations("Default profile", DEFAULT_PROFILE, songs)


def evaluate() -> None:
    """Runs every profile in EVAL_PROFILES and prints its top-5 — Phase 4 stress test."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for label, prefs in EVAL_PROFILES.items():
        print_recommendations(label, prefs, songs)


if __name__ == "__main__":
    main()
