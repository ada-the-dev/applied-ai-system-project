# Model Card: Music Recommender Simulation

## 1. Model Name

Music_Librarian (Hybrid RAG Edition)

---

## 2. Intended Use

This system generates song recommendations from plain-English requests such as "give me chill music for studying." It accepts natural-language input, retrieves song context from a local document store, and uses Gemini to rank and explain the best matches. It is designed for classroom exploration of hybrid AI systems — combining deterministic scoring with retrieval-augmented generation (RAG) — and is not intended for production use.

---

## 3. How the System Works

The system is a hybrid pipeline with two layers:

**Layer 1 — Deterministic Scoring (`src/recommender.py`)**
A weighted proximity algorithm scores each song against a default user profile. It rewards exact matches for genre and mood, and uses distance-based proximity for energy and acousticness. Mood carries the highest weight, making the base recommender mood-first.

**Layer 2 — RAG + Gemini Ranking (`src/rag.py`, `src/gemini_client.py`)**
1. The user's plain-English request is keyword-matched against `data/song_docs.json` to retrieve the top 5 most contextually relevant song documents (descriptions, mood summaries, listening scenarios).
2. The base recommender generates a pool of 10 candidate songs.
3. A structured prompt is built combining the user's request, retrieved documents, and candidate songs.
4. A single call to `gemini-2.0-flash` (temperature 0.7, max 300 tokens) ranks the top 3 candidates and provides a natural-language explanation for each.
5. Results are returned with full song metadata and the AI's explanation.

The retrieval step uses simple keyword frequency rather than embeddings, keeping it fast, transparent, and easy to explain.

---

## 4. Data

**`data/songs.csv`** — 10 songs with numeric features: energy, tempo, valence, danceability, and acousticness. Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, edm, and soul. Moods include happy, chill, intense, relaxed, moody, focused, romantic, euphoric.

**`data/song_docs.json`** — A retrieval corpus with per-song descriptions, mood summaries, and listening scenarios. This is what the RAG layer reads, not what the scoring algorithm uses.

The dataset is small (10 songs) and hand-crafted for this project. It lacks lyrics, artist popularity, play history, or user interaction data.

---

## 5. Strengths

- Accepts natural-language input, which is more accessible than structured profile forms.
- Combines reliable deterministic scoring with AI-driven explanation and flexible ranking.
- Retrieved song context gives Gemini concrete details to reason from rather than relying on its training data alone.
- The hybrid architecture means the system degrades gracefully: if the Gemini call fails, the base recommender still generates candidates.
- The test suite validates the scoring logic and the full RAG pipeline independently, with Gemini mocked in `tests/test_rag.py`.

---

## 6. Limitations and Bias

**Retrieval is keyword-only.** The retrieval step splits the user request into words and counts exact matches against song document text. It will miss semantic matches (e.g., "serene" will not match a document that says "peaceful").

**Candidates come from a fixed default profile.** The base recommender always uses `genre=pop, mood=happy, energy=0.5, acousticness=0.5` as the candidate-generation profile, regardless of the user's request. This means the candidate pool sent to Gemini is always the same 10 songs, and the RAG layer has no ability to surface songs that score poorly under this fixed profile.

**Exact-match bias in base scoring.** Genre and mood only receive points on exact matches. A jazz song cannot partially match a request for soul, even if the songs are stylistically similar.

**Proximity penalizes gradual distance.** Energy and acousticness scores decrease proportionally as they drift from the target. A song slightly off-target on energy loses points even when it is otherwise a strong match.

**Small and hand-crafted dataset.** With only 10 songs, rare genre/mood combinations may map to only one or two candidates, which limits the diversity the AI can offer.

**Prompt parsing is fragile.** `rank_songs_with_gemini()` expects Gemini's response to follow the exact format `1. Song ID: Title - Explanation`. Any deviation (extra lines, re-ordering, missing delimiter) will cause songs to be silently dropped from the output.

---

## 7. Evaluation

**Automated tests** in `tests/test_recommender.py` verify that the scoring algorithm ranks songs correctly for known profiles. `tests/test_rag.py` validates retrieval, prompt construction, response parsing, and the end-to-end RAG flow with Gemini mocked.

**Manual review** is required to evaluate whether Gemini's ranked output and explanations are actually appropriate for a given request, since the test suite cannot measure recommendation quality.

**Sensitivity findings from earlier testing:** Halving genre weight and doubling energy weight improved vibe-based matching by reducing the system's reliance on exact genre labels. This showed that energy proximity is a more expressive signal than it initially appeared.

The system behaves as intended for requests that overlap well with the fixed candidate pool. Requests for niche moods or genres (e.g., classical, metal) will yield poor results due to the limited dataset.

---

## 8. Future Work

- **Parse user requests into structured profiles** so candidate generation is request-aware, not always from a fixed default.
- **Use embedding-based retrieval** (e.g., sentence-transformers or Gemini embeddings) to replace keyword matching with semantic similarity.
- **Reward genre and mood similarity** rather than requiring exact matches in the base scoring algorithm.
- **Expand the dataset** to more than 10 songs, covering a wider range of genres, moods, and energy levels.
- **Add a more robust response parser** for Gemini output to handle format variations.
- **Incorporate tempo, valence, and danceability** into the scoring weights.

---

## 9. Personal Reflection

The biggest shift from the original project to this version was learning how to make AI useful without replacing the logic I had already built. Keeping the score-based recommender as the candidate generator, then using Gemini only for ranking and explanation, made the system more reliable than if I had handed the full recommendation task to the AI.

I also learned that retrieval is what makes AI context-aware. Without `song_docs.json`, Gemini would be guessing at song qualities from its training data. With retrieved documents, it has specific descriptions to cite in its explanations.

What surprised me most is how fragile the prompt-to-output parsing step is. Gemini's response format can vary slightly, and small changes silently break the result list. This made testing the RAG pipeline in isolation (with a mocked Gemini) very important.

The human is still in the loop for final evaluation: checking that the recommendations actually make sense for the request, verifying that RAG retrieved the right context, and deciding whether the AI's explanations are trustworthy.
