import pytest
from unittest.mock import patch

from src.recommender import Song, Recommender
from src.rag import (
    load_song_docs,
    retrieve_relevant_docs,
    build_rag_prompt,
    rank_songs_with_gemini,
    rag_recommend,
)


def make_test_recommender() -> Recommender:
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


def test_load_song_docs_returns_data():
    # Verify the retrieval corpus can be loaded and contains the expected keys.
    docs = load_song_docs()

    assert isinstance(docs, list)
    assert len(docs) > 0
    assert "song_id" in docs[0]
    assert "description" in docs[0]
    assert "listening_context" in docs[0]


def test_retrieve_relevant_docs_finds_matching_entries():
    # Ensure keyword-based retrieval returns documents relevant to the user's request.
    docs = load_song_docs()
    results = retrieve_relevant_docs("chill study", docs, top_k=3)

    assert len(results) == 3
    assert any("study" in doc["listening_context"].lower() or "chill" in doc["mood_summary"].lower() for doc in results)


def test_build_rag_prompt_contains_request_and_songs():
    # Confirm the RAG prompt includes the user request and candidate song metadata.
    docs = [
        {
            "song_id": 99,
            "title": "Study Breeze",
            "description": "A calm and chill track for focus.",
            "mood_summary": "Chill and quiet.",
            "listening_context": "Perfect for studying or reading.",
        }
    ]
    candidate_songs = [
        Song(
            id=99,
            title="Study Breeze",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.2,
            tempo_bpm=70,
            valence=0.6,
            danceability=0.4,
            acousticness=0.85,
        )
    ]

    prompt = build_rag_prompt("Give me chill music for studying", docs, candidate_songs)

    assert "Give me chill music for studying" in prompt
    assert "Study Breeze" in prompt
    assert "Genre:" in prompt
    assert "Mood:" in prompt


def test_build_rag_prompt_includes_retrieved_context():
    # Confirm the prompt contains retrieved context from song docs, not just the request.
    docs = [
        {
            "song_id": 100,
            "title": "Focus Stream",
            "description": "A low-energy track for concentration.",
            "mood_summary": "Calm and focused.",
            "listening_context": "Best for studying and writing reports.",
        }
    ]
    candidate_songs = [
        Song(
            id=100,
            title="Focus Stream",
            artist="Test Artist",
            genre="lofi",
            mood="focused",
            energy=0.3,
            tempo_bpm=75,
            valence=0.5,
            danceability=0.4,
            acousticness=0.88,
        )
    ]

    prompt = build_rag_prompt("I need music to study with", docs, candidate_songs)

    assert "I need music to study with" in prompt
    assert "A low-energy track for concentration." in prompt
    assert "Best for studying and writing reports." in prompt
    assert "Focus Stream" in prompt


def test_rank_songs_with_gemini_parses_api_response():
    # Verify that the Gemini response parser extracts song IDs, titles, and explanations correctly.
    fake_response = (
        "1. Song 2: Chill Lofi Loop - The song is ideal for studying with a calm atmosphere.\n"
        "2. Song 1: Test Pop Track - It provides a positive and upbeat mood for light focus."
    )

    with patch("src.rag.generate_text", return_value=fake_response):
        results = rank_songs_with_gemini("fake prompt")

    assert len(results) == 2
    assert results[0]["song_id"] == "2"
    assert results[0]["title"] == "Chill Lofi Loop"
    assert "ideal for studying" in results[0]["explanation"]


def test_rag_recommend_returns_structured_output():
    # Validate the end-to-end RAG recommendation flow returns structured recommendations.
    recommender = make_test_recommender()
    fake_response = (
        "1. Song 2: Chill Lofi Loop - The song matches a relaxed study request.\n"
        "2. Song 1: Test Pop Track - The song provides an upbeat alternative."
    )

    with patch("src.rag.generate_text", return_value=fake_response):
        recommendations = rag_recommend("Give me chill music for studying", recommender, k=2)

    assert len(recommendations) == 2
    assert recommendations[0]["song_id"] == 2
    assert recommendations[0]["title"] == "Chill Lofi Loop"
    assert "relaxed study request" in recommendations[0]["explanation"]
