import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

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
    target_acousticness: float

# ---------------------------------------------------------------------------
# Scoring weights — energy-prioritized strategy
# Energy is now more important, while mood is still more important than genre.
# We combine categorical matches with numeric proximity to create a transparent score.
# ---------------------------------------------------------------------------
WEIGHT_GENRE        = 1
WEIGHT_MOOD         = 3
WEIGHT_ENERGY       = 4
WEIGHT_ACOUSTICNESS = 1
MAX_SCORE = WEIGHT_GENRE + WEIGHT_MOOD + WEIGHT_ENERGY + WEIGHT_ACOUSTICNESS  # 9

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against the user profile and return the top-k matches."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "target_acousticness": user.target_acousticness,
        }
        scored = [(song, score_song(user_prefs, asdict(song))[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a string explaining why a song was recommended for a user."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "target_acousticness": user.target_acousticness,
        }
        _, reasons = score_song(user_prefs, asdict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load and return all songs from a CSV file as a list of dictionaries."""
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)

    #DEBUG
    #for song in songs:
    #    print(song)

    return songs

def _proximity_label(proximity: float) -> str:
    """Return a qualitative label describing how close a proximity score is."""
    if proximity >= 0.80:
        return "close match"
    elif proximity >= 0.50:
        return "partial match"
    else:
        return "poor match"


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against a user profile and return a (normalized_score, reasons) tuple."""
    raw = 0.0
    reasons = []

    # Categorical rule: award full WEIGHT_GENRE points for an exact match, 0 otherwise.
    # Formula: points = WEIGHT_GENRE if song["genre"] == user genre else 0
    if song["genre"] == user_prefs.get("genre"):
        raw += WEIGHT_GENRE
        reasons.append(f"genre match (+{WEIGHT_GENRE:.1f})")
    else:
        reasons.append(f"no genre match (+0.0)")

    # Categorical rule: award full WEIGHT_MOOD points for an exact match, 0 otherwise.
    # Formula: points = WEIGHT_MOOD if song["mood"] == user mood else 0
    if song["mood"] == user_prefs.get("mood"):
        raw += WEIGHT_MOOD
        reasons.append(f"mood match (+{WEIGHT_MOOD:.1f})")
    else:
        reasons.append(f"no mood match (+0.0)")

    # Proximity rule: reward closeness to the user's target energy level.
    # Formula: proximity = 1.0 - |song energy - target energy|
    #          points = proximity * WEIGHT_ENERGY
    energy_proximity = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    energy_points = WEIGHT_ENERGY * energy_proximity
    raw += energy_points
    reasons.append(f"energy proximity: {energy_proximity:.2f} — {_proximity_label(energy_proximity)} (+{energy_points:.2f})")

    # Proximity rule: reward closeness to the user's target acousticness level.
    # Formula: proximity = 1.0 - |song acousticness - target acousticness|
    #          points = proximity * WEIGHT_ACOUSTICNESS
    acoustic_proximity = 1.0 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.5))
    acoustic_points = WEIGHT_ACOUSTICNESS * acoustic_proximity
    raw += acoustic_points
    reasons.append(f"acousticness proximity: {acoustic_proximity:.2f} — {_proximity_label(acoustic_proximity)} (+{acoustic_points:.2f})")

    return raw / MAX_SCORE, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top-k results."""
    # Score every song — higher score means a better match for the user
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # sorted() is used instead of .sort() so the original songs list is not mutated
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
