"""
CLI-interface for the overall Music Recommender with RAG system.

This file accepts a plain-English user request and provides RAG-based recommendations.
"""

import logging

logging.basicConfig(level=logging.INFO)

# Import necessary functions
from src.recommender import load_songs, Song, Recommender
from src.rag import rag_recommend

# This function will be used to print the user's request and their accompanying song recommendations
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

# Start of the main function.
def main() -> None:
    # Load songs from CSV.
    songs_data = load_songs("data/songs.csv")
    songs = [Song(**song) for song in songs_data]  # Convert to Song objects
    recommender = Recommender(songs)
    
    # Prints how many songs are loaded from our CSV file.
    print(f"\n✓ Loaded {len(songs)} songs")
    
    # Example user request (can be made interactive later).
    user_request = "Give me chill music for studying"
    
    # Get top 3 RAG recommendations.
    recommendations = rag_recommend(user_request, recommender, k=3)
    
    # If RAG function ran into no error, the recommendations will print.
    # Otherwise, we will receive an error message about the API key.
    if recommendations:
        print_rag_recommendations(user_request, recommendations)
    else:
        print("No recommendations generated. Check API key and try again.")
    
    # Confirmation message that the RAG recommendation process is complete
    # as well as end of program.
    print("\n✓ RAG evaluation complete\n")

if __name__ == "__main__":
    main()
