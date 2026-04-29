# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Music_Librarian

---

## 2. Intended Use  

This recommender generates top song recommendations based on a user's preferred genre, mood, energy level, and acousticness preference. It assumes users have clear, specific tastes and recommends songs that closely match those preferences. This is designed for classroom exploration and learning about recommendation systems, not for real-world production use with actual users.  

---

## 3. How the Model Works  

The model uses a weighted proximity scoring algorithm that compares each song to a user's profile. It looks at four key features: genre, mood, energy, and acousticness. For genre and mood, it gives full points only for exact matches. For energy and acousticness, it calculates how close the song is to the user's target levels. The mood feature has the heaviest weight, making it a "mood-first" system. Each song gets a score between 0 and 1, and the top-ranked songs are recommended. This approach rewards songs that are close to the user's overall vibe.

---

## 4. Data  

The dataset contains 10 songs from a CSV file called songs.csv. It includes a mix of genres like pop, lofi, rock, ambient, jazz, synthwave, and indie pop, with moods such as happy, chill, intense, relaxed, moody, focused. The songs have numeric features for energy, tempo, valence, danceability, and acousticness. No songs were added or removed, and the dataset lacks features like lyrics, artist popularity, or user interaction data, which limits its representation of full musical taste.  

---

## 5. Strengths  

The system works well for users with strong, specific preferences, such as those who prioritize mood over genre. It captures vibe-based matching effectively, recommending songs that feel right for the user's energy and acousticness levels. For example, it matched intuition for profiles like "lofi chill" or "pop happy," providing reasonable results when all features align closely.  

---

## 6. Limitations and Bias 

Even if a song has nearly the right energy and acousticness, the song's final recommendation score can still be negatively affected if it misses an exact match for either the genre or mood feature.

This indicates that users with a rare genre or mood may be forced to a small set of songs whose genre and mood labels match with the user's profiles values. 

Addtionally, this system does not reward similar genres or moods; only exact matches are rewarded.

Furthermore, regarding the energy proximity consideration in our system, a song that is a little too high or too low energy will lose points, rather than being treated as only slightly different. This matters because say if a user's profile includes the genre and mood “jazz + relaxed,” then the one jazz-relaxed song in our data set will most likely be ranked first even if another song is actually much closer in energy and acoustic tone. This said, this is not a problem if this listener wants to strictly listen to jazz.

---

## 7. Evaluation  

I have tested all three user profiles. These user profiles are implemented as user preference dictionaries. As expected, this model rewards exact matches for genre and mood and considers proximity for energy and acousticness in its recommendation algorithm.

This model recommends songs that matches the "vibe" that listeners enjoy in their music. 

One thing I did find surprising while testing the sensitivity of my system is that when I doubled the importance of energy and halved the importance of genre via reassigning doubled and halved weights to these features, I found that decreasing the importance of genre helped the system recommend songs based on elements that would contribute to the song's vibe more (such as energy, acousticness, and mood). 

Additionally, by doubling the importance of energy proximity, I found that this led the system to reward a song's match to a user profile's desired "vibes" more. I also found that energy proximity is a more useful metric than I thought as it can be used to further reinforce that a different genre song being recommended can be similar in vibes to the user profile.

Room for improvement will include making changes in our system that rewards similarity for genres and moods.

---

## 8. Future Work  

To improve, I could add more features like tempo, valence, or danceability to the scoring. Better explanations could include why a song was recommended beyond just the score. To increase diversity, the system could include a penalty for recommending too many songs from the same artist or genre. For complex tastes, it could handle multiple preferred genres or moods instead of just one.  

---

## 9. Personal Reflection  

I learned that recommender systems balance exact matches with proximity measures to create personalized suggestions, and small changes like weight adjustments can significantly affect results. It was surprising how halving genre weight and doubling energy weight made the system more vibe-focused. This experience made me appreciate how real apps like Spotify must handle vast data and user diversity to avoid filter bubbles.  
