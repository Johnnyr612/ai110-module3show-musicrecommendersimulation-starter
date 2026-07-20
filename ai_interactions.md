# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude (an AI coding agent) to complete "Challenge 1: Add Advanced Song Features." The goal was a multi-step change across several files: add five or more new attributes to the song dataset, then update the scoring logic so the recommender actually uses them, without breaking the existing tests or the simpler profiles.

**Prompts used:**

The main prompt:

> Challenge 1: Add Advanced Song Features. Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

Follow-up prompt:

> yes, update the README and document the agentic workflow: the example prompt(s) you used, a summary of the changes the AI generated, and your manual verification notes.

Earlier in the session I also gave smaller prompts that shaped the code, such as running a weight-shift experiment, asking why certain songs kept appearing, and "remove all the '—' characters from your edits."

**What did the agent generate or change?**

The agent worked autonomously across four files:

- `data/songs.csv` - added five columns (`popularity`, `release_decade`, `mood_tags`, `language`, `explicit`) and filled in values for all 19 songs.
- `src/recommender.py` - added five new weight constants; extended the `Song` and `UserProfile` dataclasses with the new fields (all with default values); added five new scoring rules to `_score_core` (decade, mood tags, popularity, language, explicit); added helper functions `_as_int`, `_as_bool`, and `_as_tag_set`; and updated `load_songs`, `Recommender._score`, and `score_song` to pass the new data through.
- `src/main.py` - added the new preferences to the three main test profiles so the run actually exercises the features.
- `README.md` - documented the five new rules and pasted an updated sample output.

Before writing any code, the agent read the existing test file to check how `Song` and `UserProfile` were being constructed, then chose to give every new field a default value so the tests would not break.

**What did you verify or fix manually?**

- Ran `python -m pytest` myself. Both tests passed (the defaults strategy worked).
- Ran `python -m src.main` and read the output. I confirmed the new reasons (decade, mood tags, popularity, language, explicit) show up and add the right points.
- Checked the headline result by hand: "Gym Hero" dropped from #2 to #4 on the Happy Pop list because it is explicit and that profile avoids explicit content (-0.5), while the genuinely happy "Rooftop Lights" moved up. This matched what I expected, which gave me confidence the rules were wired correctly.
- Spot-checked the math: the new maximum score is 7.5, and the top pick (Sunrise City, 7.08) lines up with that.
- One thing that still needs a human decision: the agent left the experimental weights (genre 1.0, energy 2.0) in place from an earlier step, so the top of the README describes the original 2.0/1.0 baseline while the live code uses the experimental values. The agent flagged this itself rather than hiding it. I need to decide whether to revert the weights or update the baseline description.
- I also had to explicitly tell the agent to stop using "—" (em dash) characters, which it kept adding to comments and docs out of habit.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
