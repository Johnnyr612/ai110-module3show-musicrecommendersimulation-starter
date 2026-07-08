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

This is a content-based recommender that matches songs to a user by comparing the attributes of each song against the stated preferences of the user. Each song carries four features that actually drive the score: genre, mood, energy, and acousticness. `UserProfile` stores the following: favorite_genre, favorite_mood, target_energy, and likes_acoustic.

### Data flow

```
INPUT                    PROCESS                              OUTPUT
─────                    ───────                              ──────
User Prefs   ──►   The Loop: score EVERY song in the   ──►   The Ranking:
(genre, mood,      CSV one at a time with the recipe         sort by score,
 energy,           below → (score, reasons)                  take Top K
 likes_acoustic)                                             recommendations
```

- **Input** — a taste profile: `favorite_genre`, `favorite_mood`, `target_energy` (0.0–1.0), and `likes_acoustic` (True/False).
- **Process** — `score_song` judges each song independently and returns `(score, reasons)`. This is the **Scoring Rule** (one song at a time).
- **Output** — `recommend_songs` collects all scores, **sorts** them best-to-worst, and returns the **top `k`** as `(song, score, explanation)`. This is the **Ranking Rule** (the whole list).

### Algorithm Recipe

Each song's score is the sum of four weighted rules (**max 4.5 points**):

| Rule | Feature | How it scores | Weight |
|---|---|---|---|
| Genre | `genre` | exact match → full points, else 0 | 2.0 |
| Mood | `mood` | exact match → full points, else 0 | 1.0 |
| Energy | `energy` | closeness to `target_energy` | up to 1.0 |
| Acoustic | `acousticness` | reward per `likes_acoustic` | 0.5 |

Energy is scored by **closeness, not size**: `closeness = 1 - abs(song_energy - target_energy)`. A song exactly at the target earns the full point; a song far off (in either direction) earns almost nothing. Genre is weighted highest because a genre mismatch is the most jarring; mood is softer and cuts across genres.

### How songs are chosen to recommend

```
UserProfile ─┐
             ├─► score_song(song) ──► (score, reasons)  ── for each song
Song ────────┘                                │
                                              ▼
                              recommend_songs: sort by score, take top k
                                              │
                                              ▼
                            [(song, score, explanation), ...]
```

### Potential biases I expect

- **Genre over-prioritization.** Genre (2.0) outweighs every other rule, so a perfect genre match can bury a song that nails the user's mood and energy but sits in a neighboring genre — great cross-genre picks get ignored.
- **All-or-nothing categories.** Genre and mood are exact-match, so "ambient" earns *zero* genre credit against a "lofi" fan even though they're musically close — the same zero a totally unrelated genre gets.
- **Filter bubble.** It only rewards similarity to what the user already likes, so it never surprises them with something new.
- **Small-catalog bias.** It can only recommend from this tiny CSV; whatever genres and moods are over-represented there dominate the results.

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

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

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

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



