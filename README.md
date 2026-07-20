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

> The table above shows the **original baseline** design. Two things have since changed the live scorer: (1) **Experiment 1** re-weighted genre to 1.0 and energy to up-to-2.0 (see the Experiments section), and (2) **Challenge 1** added five advanced features below.

### Algorithm Recipe (Challenge 1 additions)

Challenge 1 added five more features to `data/songs.csv` and five matching rules. These are weighted smaller than the core taste rules, so they act as refinements and tie-breakers. They raise the **max possible score to 7.5**.

| Rule | Feature | How it scores | Weight |
|---|---|---|---|
| Decade | `release_decade` | exact decade match, else 0 | 0.75 |
| Mood tags | `mood_tags` | +0.25 per matching detailed tag | up to 0.75 |
| Popularity | `popularity` (0-100) | closeness to `target_popularity` | up to 0.5 |
| Language | `language` | exact match, else 0 | 0.5 |
| Explicit | `explicit` | clean bonus / explicit penalty when `avoid_explicit` is set | +0.5 or -0.5 |

The **Explicit** rule is the only one that can subtract points: if a user asks to avoid explicit content, a clean song gains +0.5 and an explicit song loses -0.5. All five rules are skipped when the user states no preference for them, so a bare `{genre, mood, energy}` profile still works exactly as before.

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
Loading songs from data/songs.csv...
Loaded songs: 19

============================================================
Recommendations for genre='pop', mood='happy', energy=0.8
============================================================

#1  Sunrise City - Neon Echo
    Score: 3.98
    Reasons:
      - genre match: pop (+2.0)
      - mood match: happy (+1.0)
      - energy match: 0.82 vs target 0.80 (+0.98)

#2  Gym Hero - Max Pulse
    Score: 2.87
    Reasons:
      - genre match: pop (+2.0)
      - energy match: 0.93 vs target 0.80 (+0.87)

#3  Rooftop Lights - Indigo Parade
    Score: 1.96
    Reasons:
      - mood match: happy (+1.0)
      - energy match: 0.76 vs target 0.80 (+0.96)

#4  Sunlit Savanna - Ayo Drumline
    Score: 0.99
    Reasons:
      - energy match: 0.79 vs target 0.80 (+0.99)

#5  Night Drive Loop - Neon Echo
    Score: 0.95
    Reasons:
      - energy match: 0.75 vs target 0.80 (+0.95)

============================================================
```

## Sample Recommendation Output (Phase 4)
```
Loading songs from data/songs.csv...
Loaded songs: 19


############################################################
# PROFILE: High-Energy Pop
# Expectation: Coherent taste: pop + happy + loud + produced should all agree.
############################################################
============================================================
Recommendations for genre='pop', mood='happy', energy=0.9
============================================================

#1  Sunrise City - Neon Echo
    Score: 4.42
    Reasons:
      - genre match: pop (+2.0)
      - mood match: happy (+1.0)
      - energy match: 0.82 vs target 0.90 (+0.92)
      - acoustic match: you like produced tracks (+0.5)

#2  Gym Hero - Max Pulse
    Score: 3.47
    Reasons:
      - genre match: pop (+2.0)
      - energy match: 0.93 vs target 0.90 (+0.97)
      - acoustic match: you like produced tracks (+0.5)

#3  Rooftop Lights - Indigo Parade
    Score: 2.36
    Reasons:
      - mood match: happy (+1.0)
      - energy match: 0.76 vs target 0.90 (+0.86)
      - acoustic match: you like produced tracks (+0.5)

#4  Storm Runner - Voltline
    Score: 1.49
    Reasons:
      - energy match: 0.91 vs target 0.90 (+0.99)
      - acoustic match: you like produced tracks (+0.5)

#5  Neon Voltage - Circuit Kids
    Score: 1.45
    Reasons:
      - energy match: 0.95 vs target 0.90 (+0.95)
      - acoustic match: you like produced tracks (+0.5)

============================================================

############################################################
# PROFILE: Chill Lofi
# Expectation: Low energy, acoustic-leaning study music. Should surface the lofi tracks.
############################################################
============================================================
Recommendations for genre='lofi', mood='chill', energy=0.35
============================================================

#1  Library Rain - Paper Lanterns
    Score: 4.50
    Reasons:
      - genre match: lofi (+2.0)
      - mood match: chill (+1.0)
      - energy match: 0.35 vs target 0.35 (+1.00)
      - acoustic match: you like acoustic (+0.5)

#2  Midnight Coding - LoRoom
    Score: 4.43
    Reasons:
      - genre match: lofi (+2.0)
      - mood match: chill (+1.0)
      - energy match: 0.42 vs target 0.35 (+0.93)
      - acoustic match: you like acoustic (+0.5)

#3  Focus Flow - LoRoom
    Score: 3.45
    Reasons:
      - genre match: lofi (+2.0)
      - energy match: 0.40 vs target 0.35 (+0.95)
      - acoustic match: you like acoustic (+0.5)

#4  Spacewalk Thoughts - Orbit Bloom
    Score: 2.43
    Reasons:
      - mood match: chill (+1.0)
      - energy match: 0.28 vs target 0.35 (+0.93)
      - acoustic match: you like acoustic (+0.5)

#5  Coffee Shop Stories - Slow Stereo
    Score: 1.48
    Reasons:
      - energy match: 0.37 vs target 0.35 (+0.98)
      - acoustic match: you like acoustic (+0.5)

============================================================

############################################################
# PROFILE: Deep Intense Rock
# Expectation: Wants the hardest, loudest, most-produced rock in the catalog.
############################################################
============================================================
Recommendations for genre='rock', mood='intense', energy=0.95
============================================================

#1  Storm Runner - Voltline
    Score: 4.46
    Reasons:
      - genre match: rock (+2.0)
      - mood match: intense (+1.0)
      - energy match: 0.91 vs target 0.95 (+0.96)
      - acoustic match: you like produced tracks (+0.5)

#2  Gym Hero - Max Pulse
    Score: 2.48
    Reasons:
      - mood match: intense (+1.0)
      - energy match: 0.93 vs target 0.95 (+0.98)
      - acoustic match: you like produced tracks (+0.5)

#3  Neon Voltage - Circuit Kids
    Score: 1.50
    Reasons:
      - energy match: 0.95 vs target 0.95 (+1.00)
      - acoustic match: you like produced tracks (+0.5)

#4  Sunrise City - Neon Echo
    Score: 1.37
    Reasons:
      - energy match: 0.82 vs target 0.95 (+0.87)
      - acoustic match: you like produced tracks (+0.5)

#5  Sunlit Savanna - Ayo Drumline
    Score: 1.34
    Reasons:
      - energy match: 0.79 vs target 0.95 (+0.84)
      - acoustic match: you like produced tracks (+0.5)

============================================================

############################################################
# PROFILE: ADVERSARIAL: Conflicting (loud but sad)
# Expectation: Internally contradictory: wants max energy AND acoustic AND a 'sad' mood no song has. Watch which rules win - energy+genre likely drag in loud produced pop even though 'sad' and 'acoustic' never match.
############################################################
============================================================
Recommendations for genre='pop', mood='sad', energy=0.95
============================================================

#1  Gym Hero - Max Pulse
    Score: 2.98
    Reasons:
      - genre match: pop (+2.0)
      - energy match: 0.93 vs target 0.95 (+0.98)

#2  Sunrise City - Neon Echo
    Score: 2.87
    Reasons:
      - genre match: pop (+2.0)
      - energy match: 0.82 vs target 0.95 (+0.87)

#3  Dust and Diesel - Rhett Canyon
    Score: 1.10
    Reasons:
      - acoustic match: you like acoustic (+0.5)

#4  Neon Voltage - Circuit Kids
    Score: 1.00
    Reasons:
      - energy match: 0.95 vs target 0.95 (+1.00)

#5  Midnight Coding - LoRoom
    Score: 0.97
    Reasons:
      - acoustic match: you like acoustic (+0.5)

============================================================

############################################################
# PROFILE: ADVERSARIAL: Empty profile (no opinions)
# Expectation: No genre/mood/energy/acoustic at all. Every rule is skipped, so every song scores 0.0 and 'ranking' collapses to catalog order. Exposes that ties are broken by input order, not by merit.
############################################################
============================================================
Recommendations for genre='None', mood='None', energy=None
============================================================

#1  Sunrise City - Neon Echo
    Score: 0.00
    Reasons: general pick (no strong matches)

#2  Midnight Coding - LoRoom
    Score: 0.00
    Reasons: general pick (no strong matches)

#3  Storm Runner - Voltline
    Score: 0.00
    Reasons: general pick (no strong matches)

#4  Library Rain - Paper Lanterns
    Score: 0.00
    Reasons: general pick (no strong matches)

#5  Gym Hero - Max Pulse
    Score: 0.00
    Reasons: general pick (no strong matches)

============================================================

############################################################
# PROFILE: ADVERSARIAL: Out-of-range energy (2.0)
# Expectation: energy=2.0 is outside the 0..1 range the closeness math assumes. closeness = 1 - |song-2.0| goes NEGATIVE, so the energy rule can now PENALIZE songs. Checks whether the scorer clamps its inputs (it doesn't).
############################################################
============================================================
Recommendations for genre='edm', mood='energetic', energy=2.0
============================================================

#1  Neon Voltage - Circuit Kids
    Score: 3.45
    Reasons:
      - genre match: edm (+2.0)
      - mood match: energetic (+1.0)
      - acoustic match: you like produced tracks (+0.5)

#2  Gym Hero - Max Pulse
    Score: 0.43
    Reasons:
      - acoustic match: you like produced tracks (+0.5)

#3  Storm Runner - Voltline
    Score: 0.41
    Reasons:
      - acoustic match: you like produced tracks (+0.5)

#4  Sunrise City - Neon Echo
    Score: 0.32
    Reasons:
      - acoustic match: you like produced tracks (+0.5)

#5  Sunlit Savanna - Ayo Drumline
    Score: 0.29
    Reasons:
      - acoustic match: you like produced tracks (+0.5)

============================================================
```
---

## Sample Recommendation Output (Challenge 1: Advanced Features)

After adding the five advanced features (popularity, release decade, mood tags, language, explicit), the profiles now use them and the scores go higher (max 7.5). The headline change: **Gym Hero finally stops hogging the top of the "Happy Pop" list**. Because this listener asked to avoid explicit content, Gym Hero (explicit) takes a -0.5 penalty and drops to #4, while the genuinely happy *Rooftop Lights* rises to #2. Only the three coherent profiles are shown here; the adversarial profiles do not set the new preferences, so their output is unchanged.

```
############################################################
# PROFILE: High-Energy Pop
############################################################
Recommendations for genre='pop', mood='happy', energy=0.9

#1  Sunrise City - Neon Echo
    Score: 7.08
    Reasons:
      - genre match: pop (+1.0)
      - mood match: happy (+1.0)
      - energy match: 0.82 vs target 0.90 (+1.84)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: bright, euphoric (+0.50)
      - popularity match: 78 vs target 80 (+0.49)
      - language match: english (+0.50)
      - clean track: no explicit content (+0.50)

#2  Rooftop Lights - Indigo Parade
    Score: 5.16
    Reasons:
      - mood match: happy (+1.0)
      - energy match: 0.76 vs target 0.90 (+1.72)
      - acoustic match: you like produced tracks (+0.5)
      - mood tags: bright, euphoric (+0.50)
      - popularity match: 68 vs target 80 (+0.44)
      - language match: english (+0.50)
      - clean track: no explicit content (+0.50)

#3  Sunlit Savanna - Ayo Drumline
    Score: 4.95
    Reasons:
      - energy match: 0.79 vs target 0.90 (+1.78)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: bright, euphoric (+0.50)
      - popularity match: 63 vs target 80 (+0.41)
      - language match: english (+0.50)
      - clean track: no explicit content (+0.50)

#4  Gym Hero - Max Pulse
    Score: 4.93
    Reasons:
      - genre match: pop (+1.0)
      - energy match: 0.93 vs target 0.90 (+1.94)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: euphoric (+0.25)
      - popularity match: 82 vs target 80 (+0.49)
      - language match: english (+0.50)
      - explicit content: you asked to avoid it (-0.50)

#5  Neon Voltage - Circuit Kids
    Score: 4.60
    Reasons:
      - energy match: 0.95 vs target 0.90 (+1.90)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: bright, euphoric (+0.50)
      - popularity match: 70 vs target 80 (+0.45)
      - clean track: no explicit content (+0.50)

############################################################
# PROFILE: Chill Lofi
############################################################
Recommendations for genre='lofi', mood='chill', energy=0.35

#1  Library Rain - Paper Lanterns
    Score: 6.74
    Reasons:
      - genre match: lofi (+1.0)
      - mood match: chill (+1.0)
      - energy match: 0.35 vs target 0.35 (+2.00)
      - acoustic match: you like acoustic (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: calm, dreamy (+0.50)
      - popularity match: 47 vs target 45 (+0.49)
      - language match: instrumental (+0.50)

#2  Midnight Coding - LoRoom
    Score: 6.56
    Reasons:
      - genre match: lofi (+1.0)
      - mood match: chill (+1.0)
      - energy match: 0.42 vs target 0.35 (+1.86)
      - acoustic match: you like acoustic (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: calm, dreamy (+0.50)
      - popularity match: 55 vs target 45 (+0.45)
      - language match: instrumental (+0.50)

#3  Focus Flow - LoRoom
    Score: 5.62
    Reasons:
      - genre match: lofi (+1.0)
      - energy match: 0.40 vs target 0.35 (+1.90)
      - acoustic match: you like acoustic (+0.5)
      - decade match: 2020s (+0.75)
      - mood tags: calm, dreamy (+0.50)
      - popularity match: 52 vs target 45 (+0.46)
      - language match: instrumental (+0.50)

############################################################
# PROFILE: Deep Intense Rock
############################################################
Recommendations for genre='rock', mood='intense', energy=0.95

#1  Storm Runner - Voltline
    Score: 6.17
    Reasons:
      - genre match: rock (+1.0)
      - mood match: intense (+1.0)
      - energy match: 0.91 vs target 0.95 (+1.92)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2010s (+0.75)
      - mood tags: aggressive, dark (+0.50)
      - clean track: no explicit content (+0.50)

#2  Night Drive Loop - Neon Echo
    Score: 3.60
    Reasons:
      - energy match: 0.75 vs target 0.95 (+1.60)
      - acoustic match: you like produced tracks (+0.5)
      - decade match: 2010s (+0.75)
      - mood tags: dark (+0.25)
      - clean track: no explicit content (+0.50)

#5  Gym Hero - Max Pulse
    Score: 3.21
    Reasons:
      - mood match: intense (+1.0)
      - energy match: 0.93 vs target 0.95 (+1.96)
      - acoustic match: you like produced tracks (+0.5)
      - mood tags: aggressive (+0.25)
      - explicit content: you asked to avoid it (-0.50)
```
---

## Experiments You Tried

### Experiment 1: Weight Shift - double energy, halve genre

**The change.** In `src/recommender.py` I doubled the energy weight and halved the genre weight, leaving mood and acoustic alone:

| Weight | Before | After |
|---|---|---|
| `WEIGHT_GENRE` | 2.0 | **1.0** |
| `WEIGHT_MOOD` | 1.0 | 1.0 |
| `WEIGHT_ENERGY` | 1.0 | **2.0** |
| `WEIGHT_ACOUSTIC` | 0.5 | 0.5 |

**Hypothesis.** Genre (2.0) was outranking mood, so "right genre, wrong vibe" songs beat "right vibe, adjacent genre" songs. Making energy the strongest signal, and dropping genre to tie with mood, should reward songs that *feel* like the target even if the genre label differs.

**Is the math still valid?** Yes. The max possible score is unchanged at **4.5**: I removed 1.0 from genre's ceiling and added 1.0 to energy's, so `1.0 + 1.0 + 2.0 + 0.5 = 4.5`. Verified in the output: *Library Rain* still tops out at exactly 4.50 on a perfect four-rule match. Energy now caps at +2.00 (e.g. *Neon Voltage*, energy 0.95 vs target 0.95 → closeness 1.0 × 2.0 = 2.00), and each "genre match" line now reads `(+1.0)`.

**What changed - High-Energy Pop profile:**

| Rank | Before (genre 2.0) | After (energy 2.0) |
|---|---|---|
| #1 | Sunrise City 4.42 | Sunrise City 4.34 |
| #2 | Gym Hero 3.47 | Gym Hero 3.44 |
| #3 | Rooftop Lights **2.36** | Rooftop Lights **3.22** |

*Rooftop Lights* (a **happy** indie-pop song, exactly what a "happy pop" user wants) surged from a **1.11-point gap** behind Gym Hero to just **0.22**. More importantly, *why* Gym Hero still edges it out changed: with genre and mood now tied at 1.0, the tiebreaker is pure energy closeness, and Gym Hero's 0.93 is genuinely nearer the 0.90 target than Rooftop's 0.76. That's a fairer ordering than the old "genre bulldozer" result.

**Takeaway.** The system is sensitive to the weights in the predicted direction: halving genre stopped it from burying strong mood/energy matches, and the lists now rank more on "does this *feel* like what I asked for" than on an exact genre-label match. The scoring math stayed sound throughout (max still 4.5, no rule broke). A side effect worth noting: doubling energy also *doubled the penalty* in the out-of-range (energy = 2.0) adversarial profile, pushing those scores lower, consistent behavior, but more evidence the scorer should clamp energy to 0-1.

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



