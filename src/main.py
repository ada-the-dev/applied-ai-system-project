"""
Command line runner for the AI-powered Music Recommender with RAG.

This file accepts a plain-English user request and provides RAG-based recommendations.
"""

from src.recommender import load_songs, Song, Recommender
from src.rag import rag_recommend

def print_rag_recommendations(user_request: str, recommendations: list) -> None:
    """Helper function to print RAG-based recommendations."""
    print("\n" + "=" * 70)
    print(f"  User Request: {user_request}")
    print("=" * 70)
    
    for rank, rec in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {rec['title']}  (ID: {rec['song_id']})")
        print(f"      Artist : {rec['artist']}")
        print(f"      Genre  : {rec['genre']}  |  Mood: {rec['mood']}")
        print(f"      Energy : {rec['energy']:.2f}  |  Acousticness: {rec['acousticness']:.2f}")
        print(f"      AI Explanation:")
        print(f"        {rec['explanation']}")
    print("\n" + "=" * 70)

def main() -> None:
    # Load songs from CSV
    songs_data = load_songs("data/songs.csv")
    songs = [Song(**song) for song in songs_data]  # Convert to Song objects
    recommender = Recommender(songs)
    
    print(f"\n✓ Loaded {len(songs)} songs")
    
    # Example user request (can be made interactive later)
    user_request = "Give me chill music for studying"
    
    # Get RAG recommendations
    recommendations = rag_recommend(user_request, recommender, k=3)
    
    if recommendations:
        print_rag_recommendations(user_request, recommendations)
    else:
        print("No recommendations generated. Check API key and try again.")
    
    print("\n✓ RAG evaluation complete\n")

if __name__ == "__main__":
    main()
