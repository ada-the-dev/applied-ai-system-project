# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommendation systems have a lot of nuance in their workings and different types of data to make inferences from. For example, these systems may compare users to each other, so that similar users can receive similar recommendations, or so that the system can further reinforce that this recommendation is worth recommending to another similar user. 

There may also be factors like watch time, skips, paused, subscriptions/followed creators, time of day, location, and the device currently being used that can be utilized to provide a recommendation for the user. A collection of data based on the user's preferences, circumstances, and whims can be analyzed and extracted from to generate quantifiable results that determine whether a recommendation should be made to a user.

Now, for my particular music recommender simulation, a weighted proximity scoring algorithm will be used in which every song is scored against a user's profile, and then these songs will be ranked against each other on this scoring. The algorithm will be a  "mood-first" algorithm since this has the heaviest weight. The top three ranking songs will be recommended to the user. This algorithm will reward a song's closeness to a user's profile.

Each song will receive a score in the range [0.0, 1.0]. The score is a weighted sum of four sub-scores, and then this score is divided by the total possible points (8 points) to normalize it. In particular, the genre, mood, energy, and acousticness features of each song will scored against the user profile's genre, mood, energy, and acousticness.

While this recommendation system will be able to better recommend songs that match a user's mood and overall preference, one potential drawback to the weight decision, and, therefore the recommedation algorithm, is that users who greatly value genre over mood (a.k.a. "genre-loyalists") will have a higher chance of being exposed to song genres that do not align with their preferences and music-related boundaries.

Here is a Mermaid Live that describes the data flow of my proposed and implemented music recommendation system:

```
flowchart TD
    A[(songs.csv)] -->|load_songs| B[Song List]
    C[User Profile\ngenre · mood · energy · target_acousticness] --> D

    B -->|one song at a time| D

    subgraph SCORE["score_song — repeats for every song"]
        D[Genre match?\n× WEIGHT_GENRE 2]
        D --> E[Mood match?\n× WEIGHT_MOOD 3]
        E --> F["Energy proximity\n1 - abs song.energy - target x 2"]
        F --> G["Acousticness proximity\n1 - abs song.acousticness - target x 1"]
        G --> H[Sum raw score / 8\nnormalized score 0.0 to 1.0]
    end

    H --> I["(song, score) pairs"]
    I --> J[Sort all pairs descending by score]
    J --> K[Slice top-k]
    K --> L[Top K Recommendations]
```

Here is an example result output that is generated from the CLI simulation of this program.

![CLI Simulation Output (Results)](CLI-Simulation-Result-Output.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

From this project, I learned that recommenders can take the values of certain features and compare them against against an ideal set of features' values. The influence of particular features on the final, generated recommendations can vary based on the weights assigned to these features. 

As a result, an example of where bias or unfairness can show up in systems, like this recommender, is when we assign weights to features. The decision of choosing which features weigh more is made by the human, and humans are biased or may make decisions in a way that differs from another human's approach. For example, there is a greater bias and emphasis placed on a song's mood than on that song's genre. This is due to the intentional design of the my algorithm as I made the weight larger for the mood feature.

---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Songs for Your Mood

---

## 2. Intended Use

- This system will try to recommend the top K songs to a user based on their listening profile. In particular, this system will look for songs that closely match with the user's genre, mood, energy, and acousticness preferences.
- This system is made to be used by people who seek to listen to songs that match their preference and who value a mood match over sticking to song recommendations that stem from one genre. At the moment, the user may not have diverse music taste necesarily since the system currently accepts one value for each aforementioned feature. For example, a user's listening profile may list one genre only. As a side note, this is a class project, so this system is intended for hypothetical users.

---

## 3. How It Works (Short Explanation)

This system will consider the values of a song's and a user's genre, mood, energy, and acousticness features. Comparisons will be made these values such that exact genre and mood matches are rewarded with points. 

Additionally, energy and acousticness features have a mathematical formula that rewards numerical proximity. This means that if the energy level and acousticness of a song is similar to a user's desired energy level and acousticness then we will see a higher score returned.

Once the total points are calculated from these four comparisons, the score will be normalized by diving the total points by the possible maximum value for total points.

---

## 4. Data

There are a total of 20 songs in data/songs.csv.

Initially, there were only 10 songs, but I added 10 more songs, so that there is a more diverse set of songs to work with.

Examples of the kinds of genres represented in the data are: pop, lofi, rap.
Examples of the kinds of moods represented in the data are: happy, chill, relaxed.

- Whose taste does this data mostly reflect
Most of the songs in this data set have a tempo that leans towards a more upbeat tone, so the data reflects the taste of someone who doesn't primarily listen to slower-paced music.

---

## 5. Strengths

I was not able to test my system yet, but, based on personal observation, my recommender would work well for user profiles that prefer songs that are not slow-paced and that are positive and upbeat.

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

I was not able to test my system yet, but, based on personal observation, my recommender would not work well for user profiles that prefer more somber and slow-paced songs due to the songs that are represented in my data set.

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If I had more time, I would:
1) Further test my recommender
2) Diversify my data set to include more slower-paced and somber music
3) Incorporate semantics in the recommendation algorithm, so that mood comparisons are not rewarded for exact matches. I want to reward semantics and similar "vibes" for a song.

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

I had a lot of fun designing and implementing this project. From this project, I was able to have a better idea of how real music recommenders use data to generate recommendations via quantifiable methods. Additionally, I saw how useful and nuanced it can be to plan the design and intent for how a recommender algorithm should be implemented. For me, the magic of recommenders is being revealed from behind the curtain by doing this project.

This said, human judgement is still valuable in the designing and implementation of this model because a human (with the proper knowledge) can ensure the efficiency of algorithms. Additionally, humans will typically understand better the context of the results they are seeking to achieve and the information they will use to achieve this results and to create the model. Unless, all of this information is supplied in an efficient and full manner to a model or to an AI, assumptions will be made. These assumptions may or may not be true, but a human can vet these assumptions in their stead.

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"
