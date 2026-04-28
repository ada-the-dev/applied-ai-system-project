"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Helper function to print recommendations for a user profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\n" + "=" * 70)
    print(f"  {profile_name}")
    print("=" * 70)
    print(f"  Profile: genre={user_prefs['favorite_genre']} | mood={user_prefs['favorite_mood']}")
    print(f"           energy={user_prefs['target_energy']} | acousticness={user_prefs['target_acousticness']}")
    print("=" * 70)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  (Score: {score:.3f})")
        print(f"      Artist : {song['artist']}")
        print(f"      Genre  : {song['genre']}  |  Mood: {song['mood']}")
        print(f"      Energy : {song['energy']}  |  Acousticness: {song['acousticness']}")
        print(f"      Why:")
        for reason in explanation.split("; "):
            if reason.strip():
                print(f"        • {reason.strip()}")
    print("\n" + "=" * 70)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\n✓ Loaded {len(songs)} songs")

    # Profile 1: Mainstream Pop Energizer — Tests aligned preferences where all signals point to the same recommendation.
    profile_1 = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "target_acousticness": 0.10,
    }

    # Profile 2: Lo-fi Study Nester — Tests low-energy, high-acousticness preference; opposite end of spectrum from Profile 1.
    profile_2 = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "target_acousticness": 0.75,
    }

    # Edge Case 1: Jazz Relax — Tests how the system ranks a rare genre (1 song) vs. mood/energy matches; reveals genre vs. vibe trade-offs.
    edge_case_1 = {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.35,
        "target_acousticness": 0.80,
    }

    # Run recommendations for all three profiles
    print_recommendations("PROFILE 1: Mainstream Pop Energizer", profile_1, songs, k=5)
    print_recommendations("PROFILE 2: Lo-fi Study Nester", profile_2, songs, k=5)
    print_recommendations("EDGE CASE 1: Jazz Relax (Rare Genre Test)", edge_case_1, songs, k=5)

    print("\n✓ Evaluation complete\n")


if __name__ == "__main__":
    main()
