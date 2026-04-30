import json
import os
from typing import List, Dict, Any
from src.recommender import Recommender, Song, UserProfile
from src.gemini_client import generate_text

# Path to the song docs
SONG_DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "song_docs.json")

# This function will parse the json file into a list of dictionaries.
# Each dictionary will represent a song and its attributes.
def load_song_docs() -> List[Dict[str, Any]]:
    """Load song documentation from JSON file."""
    with open(SONG_DOCS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# This function will take in the user's request and the list of song documents, and it will return a list of the 
# most relevant song documents based on keyword matching.
def retrieve_relevant_docs(user_request: str, song_docs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve the top-k most relevant song documents based on keyword matching.
    
    This is a simple retrieval method that scores documents by counting how many
    words from the user's request appear in the song's description, mood summary,
    or listening context. It's efficient and doesn't require embeddings.
    
    Args:
        user_request: The user's plain-English music request (e.g., "chill study music").
        song_docs: List of song document dictionaries from song_docs.json.
        top_k: Number of top-matching documents to return.
    
    Returns:
        List of the top-k relevant song documents.
    """
    # Extract keywords from the user request by splitting into words and converting to lowercase
    keywords = set(user_request.lower().split())
    
    # Score each song document by counting keyword matches in its text fields
    scored_docs = []
    for doc in song_docs:
        score = 0
        # Combine description, mood_summary, and listening_context into one text block for matching
        text_to_check = f"{doc['description']} {doc['mood_summary']} {doc['listening_context']}".lower()
        # Increment score for each keyword found in the text
        for keyword in keywords:
            if keyword in text_to_check:
                score += 1
        # After loop is over, the score for a song is appended.
        scored_docs.append((doc, score))
    
    # Sort documents by score in descending order (highest matches first)
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    # Return only the documents, not the scores
    return [doc for doc, _ in scored_docs[:top_k]]

# This function will build a prompt for Gemini that includes the user's request, the retrieved song documents, 
# and the candidate songs from the recommender. 
# The prompt will ask Gemini to rank the candidate songs and provide explanations 
# based on the retrieved context.
def build_rag_prompt(user_request: str, retrieved_docs: List[Dict[str, Any]], candidate_songs: List[Song], user_profile: UserProfile) -> str:
    """
    Build a prompt for Gemini to rank and explain song recommendations using RAG context.

    The prompt includes:
    - The user's original request
    - The user's taste profile
    - Retrieved song documents for context
    - List of candidate songs to rank

    This allows Gemini to use retrieved information to make more informed recommendations.

    Args:
        user_request: The user's plain-English request.
        retrieved_docs: List of relevant song documents from retrieval.
        candidate_songs: List of Song objects from the recommender's initial selection.
        user_profile: The user's taste preferences.

    Returns:
        A formatted prompt string for Gemini.
    """
    # Format retrieved docs as a readable list
    docs_text = "\n".join([
        f"- Song {doc['song_id']}: {doc['title']} - {doc['description']} Mood: {doc['mood_summary']}. Context: {doc['listening_context']}."
        for doc in retrieved_docs
    ])

    # Format candidate songs with their attributes
    songs_text = "\n".join([
        f"- Song {song.id}: {song.title} by {song.artist} (Genre: {song.genre}, Mood: {song.mood}, Energy: {song.energy:.2f}, Acousticness: {song.acousticness:.2f})"
        for song in candidate_songs
    ])

    # Format the user's taste profile
    profile_text = (
        f"Favorite genre: {user_profile.favorite_genre}, "
        f"Favorite mood: {user_profile.favorite_mood}, "
        f"Target energy: {user_profile.target_energy:.2f}, "
        f"Target acousticness: {user_profile.target_acousticness:.2f}"
    )

    # Construct the full prompt
    prompt = f"""
You are a music recommendation assistant. A user has requested: "{user_request}"

User taste profile: {profile_text}

Here is some relevant information about songs that might match their request:
{docs_text}

From our catalog, here are some candidate songs to consider:
{songs_text}

Based on the user's request, their taste profile, and the retrieved song information, rank the top 3 candidate songs that best match. For each top song, provide:
1. The song ID and title
2. A brief explanation of why it fits, using details from the retrieved information
3. How it aligns with the user's request

Format your response as:
1. Song ID: Title - Explanation
2. Song ID: Title - Explanation
3. Song ID: Title - Explanation
"""
    return prompt.strip()

def rank_songs_with_gemini(prompt: str) -> List[Dict[str, str]]:
    """
    Send the RAG prompt to Gemini and parse the ranked song recommendations.
    
    This function makes one API call to Gemini to get AI-powered rankings
    and explanations based on the user's request and retrieved context.
    
    Args:
        prompt: The formatted prompt string from build_rag_prompt.
    
    Returns:
        List of dictionaries with 'song_id', 'title', and 'explanation' for top songs.
        Returns empty list if parsing fails or no response.
    """
    # Call Gemini to generate the ranked response
    response = generate_text(prompt, max_tokens=300)
    if not response:
        return []  # Fallback if API fails
    
    # Parse the response (expected format: "1. Song ID: Title - Explanation")
    ranked_songs = []
    lines = response.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith(('1.', '2.', '3.')) and ' - ' in line:
            # Extract song ID and title from the line
            parts = line.split(' - ', 1)
            if len(parts) == 2:
                song_part = parts[0].split('.', 1)[1].strip()  # Remove "1. "
                explanation = parts[1].strip()
                # Parse song ID and title (format: "Song ID: Title")
                if ': ' in song_part:
                    id_title = song_part.split(': ', 1)
                    song_id = id_title[0].replace('Song ', '').strip()
                    title = id_title[1].strip()
                    ranked_songs.append({
                        'song_id': song_id,
                        'title': title,
                        'explanation': explanation
                    })
    
    return ranked_songs

def rag_recommend(user_request: str, recommender: Recommender, k: int = 3) -> List[Dict[str, Any]]:
    """
    Perform RAG-based song recommendations.
    
    This is the main entry point for RAG recommendations:
    1. Load song documentation
    2. Retrieve relevant docs based on user request
    3. Get candidate songs from the recommender (using a default profile for now)
    4. Build RAG prompt with request, docs, and candidates
    5. Call Gemini to rank and explain top songs
    6. Return structured recommendations
    
    Args:
        user_request: The user's plain-English music request.
        recommender: The Recommender instance with loaded songs.
        k: Number of top recommendations to return.
    
    Returns:
        List of dictionaries with song details and AI explanations.
        Each dict includes: song_id, title, artist, genre, mood, energy, acousticness, explanation.
    """
    # Load song docs for retrieval
    song_docs = load_song_docs()
    
    # Retrieve relevant docs based on user request
    retrieved_docs = retrieve_relevant_docs(user_request, song_docs, top_k=5)
    
    # For now, use a default profile to get candidate songs (can be improved later)
    # This gets a broad set of candidates that Gemini can then rank
    default_profile = UserProfile(
        favorite_genre="pop",  # Neutral defaults
        favorite_mood="happy",
        target_energy=0.5,
        target_acousticness=0.5
    )
    candidate_songs = recommender.recommend(default_profile, k=10)  # Get more candidates for ranking
    
    # Build the RAG prompt
    prompt = build_rag_prompt(user_request, retrieved_docs, candidate_songs, default_profile)
    
    # Get AI-ranked recommendations
    ranked_results = rank_songs_with_gemini(prompt)
    
    # Integrate with full song data and return top-k
    recommendations = []
    for result in ranked_results[:k]:
        # Find the full song object by ID
        song = next((s for s in recommender.songs if str(s.id) == result['song_id']), None)
        if song:
            recommendations.append({
                'song_id': song.id,
                'title': song.title,
                'artist': song.artist,
                'genre': song.genre,
                'mood': song.mood,
                'energy': song.energy,
                'acousticness': song.acousticness,
                'explanation': result['explanation']
            })
    
    return recommendations