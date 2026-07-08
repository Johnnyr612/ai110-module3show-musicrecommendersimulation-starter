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

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

This is a content-based recommender that matches songs to a user by comparing the attributes of each song against the stated preferences of the user. Each song carries four features that actually drive the score: genre, mood, energy, and acousticness. `UserProfile` stores the following favorite_genre, favorite_mood, target_energy, and likes_acoustic.
How the `recommender.py` computes a score for each song:
| Rule | Feature | How it scores | Weight |
|---|---|---|---|
| Genre | `genre` | exact match → full points, else 0 | 3.0 |
| Mood | `mood` | exact match → full points, else 0 | 2.0 |
| Energy | `energy` | closeness to `target_energy` | 2.0 |
| Acoustic | `acousticness` | reward/penalize per `likes_acoustic` | 1.0 |

How songs are chosen to recommend:
UserProfile ─┐
             ├─► score_song(song) ──► (score, reasons)  ── for each song
Song ────────┘                                │
                                              ▼
                              recommend_songs: sort by score, take top k
                                              │
                                              ▼
                            [(song, score, explanation), ...]


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



