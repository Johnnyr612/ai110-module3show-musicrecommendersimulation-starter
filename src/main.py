"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import (
    DEFAULT_MODE,
    MODES,
    load_songs,
    recommend_songs,
)

# ---------------------------------------------------------------------------
# Challenge 2: pick the scoring mode here. Options come from recommender.MODES:
#   "balanced"       - genre leads, energy gentle (the original starter design)
#   "genre-first"    - genre dominates the ranking
#   "mood-first"     - the vibe/mood dominates the ranking
#   "energy-focused" - closeness to target energy dominates (the default)
# Change this one string to switch how EVERY profile below is ranked.
# ---------------------------------------------------------------------------
MODE = DEFAULT_MODE


def print_recommendations(user_prefs: dict, recommendations: list, mode: str = DEFAULT_MODE) -> None:
    """Render the ranked recommendations as a clean, readable terminal layout."""
    width = 60
    header = (
        f"[mode: {mode}]  Recommendations for genre='{user_prefs.get('genre')}', "
        f"mood='{user_prefs.get('mood')}', energy={user_prefs.get('energy')}"
    )
    print("=" * width)
    print(header)
    print("=" * width)

    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        # recommend_songs already returns the structured reasons (including any
        # Challenge 3 diversity penalty), so we just print them here.
        print(f"\n#{rank}  {song['title']} - {song['artist']}")
        print(f"    Score: {score:.2f}")
        if reasons:
            print("    Reasons:")
            for reason in reasons:
                print(f"      - {reason}")
        else:
            print("    Reasons: general pick (no strong matches)")

    print("\n" + "=" * width)


# ---------------------------------------------------------------------------
# Profiles to simulate.
# The first three are "normal" personas - each cleans on a different mix of
# genre / mood / energy so we can see the weights doing their job.
# The last three are ADVERSARIAL profiles: they are built to fight the scoring
# logic and expose its blind spots. Each carries a `label` and a `note` about
# what we expect (or fear) will happen.
# ---------------------------------------------------------------------------
PROFILES = [
    # --- Three distinct, coherent personas -------------------------------
    {
        "label": "High-Energy Pop",
        "prefs": {
            "genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False,
            # Challenge 1 features: modern, mainstream, upbeat, clean english pop.
            "decade": 2020, "mood_tags": ["euphoric", "bright"],
            "popularity": 80, "language": "english", "avoid_explicit": True,
        },
        "note": "Coherent taste: pop + happy + loud + produced should all agree.",
    },
    {
        "label": "Chill Lofi",
        "prefs": {
            "genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
            # Modern instrumental study vibes, niche/underground is fine.
            "decade": 2020, "mood_tags": ["calm", "dreamy"],
            "popularity": 45, "language": "instrumental",
        },
        "note": "Low energy, acoustic-leaning study music. Should surface the lofi tracks.",
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {
            "genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False,
            # Dark, aggressive, 2010s rock, wants it clean.
            "decade": 2010, "mood_tags": ["aggressive", "dark"], "avoid_explicit": True,
        },
        "note": "Wants the hardest, loudest, most-produced rock in the catalog.",
    },

    # --- Adversarial / edge-case profiles --------------------------------
    {
        "label": "ADVERSARIAL: Conflicting (loud but sad)",
        "prefs": {"genre": "pop", "mood": "sad", "energy": 0.95, "likes_acoustic": True},
        "note": (
            "Internally contradictory: wants max energy AND acoustic AND a 'sad' "
            "mood no song has. Watch which rules win - energy+genre likely drag in"
            "loud produced pop even though 'sad' and 'acoustic' never match."
        ),
    },
    {
        "label": "ADVERSARIAL: Empty profile (no opinions)",
        "prefs": {},
        "note": (
            "No genre/mood/energy/acoustic at all. Every rule is skipped, so every "
            "song scores 0.0 and 'ranking' collapses to catalog order. Exposes that "
            "ties are broken by input order, not by merit."
        ),
    },
    {
        "label": "ADVERSARIAL: Out-of-range energy (2.0)",
        "prefs": {"genre": "edm", "mood": "energetic", "energy": 2.0, "likes_acoustic": False},
        "note": (
            "energy=2.0 is outside the 0..1 range the closeness math assumes. "
            "closeness = 1 - |song-2.0| goes NEGATIVE, so the energy rule can now "
            "PENALIZE songs. Checks whether the scorer clamps its inputs (it doesn't)."
        ),
    },
]


def compare_modes(user_prefs: dict, songs: list, k: int = 3) -> None:
    """Challenge 2 demo: run ONE profile through EVERY mode, side by side.

    This makes the effect of switching modes obvious: the same listener and the
    same catalog produce different rankings depending on which signal leads.
    """
    print("\n" + "*" * 60)
    print("# MODE COMPARISON for the 'High-Energy Pop' profile")
    print("# Same listener, same songs, four different ranking strategies.")
    print("*" * 60)

    for mode in MODES:
        ranked = recommend_songs(user_prefs, songs, k=k, mode=mode)
        top = ", ".join(f"{song['title']} ({score:.2f})" for song, score, _ in ranked)
        print(f"\n[{mode}]\n    {top}")
    print("\n" + "*" * 60)


def compare_diversity(songs: list) -> None:
    """Challenge 3 demo: the same profile with the diversity penalty OFF vs ON.

    Uses a hip hop fan on purpose: the catalog has several songs by one artist
    (Mike Sherm), so with diversity OFF they stack up, and with diversity ON the
    penalty spreads them out and lets other artists/genres into the list.
    """
    prefs = {"genre": "hip hop", "mood": "defiant", "energy": 0.7, "likes_acoustic": False}
    print("\n" + "*" * 60)
    print("# DIVERSITY DEMO for a 'Hip Hop' fan (mode: genre-first)")
    print("# Watch repeated artists/genres get spread out when diversity is ON.")
    print("*" * 60)

    for label, on in (("OFF", False), ("ON", True)):
        ranked = recommend_songs(prefs, songs, k=6, mode="genre-first", diversity=on)
        print(f"\n[diversity {label}]")
        for rank, (song, score, _reasons) in enumerate(ranked, start=1):
            print(f"  {rank}. {song['title']} - {song['artist']} [{song['genre']}] ({score:.2f})")
    print("\n" + "*" * 60)


def main() -> None:
    """Run the end-to-end CLI simulation: load, recommend, and print."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {MODE}\n")

    for profile in PROFILES:
        print("\n" + "#" * 60)
        print(f"# PROFILE: {profile['label']}")
        print(f"# Expectation: {profile['note']}")
        print("#" * 60)

        # Challenge 2: rank this profile using the mode selected at the top.
        recommendations = recommend_songs(profile["prefs"], songs, k=7, mode=MODE)
        print_recommendations(profile["prefs"], recommendations, mode=MODE)

    # Challenge 2: show how the same profile reranks under each mode.
    compare_modes(PROFILES[0]["prefs"], songs)

    # Challenge 3: show how the diversity penalty spreads out artists/genres.
    compare_diversity(songs)


if __name__ == "__main__":
    main()
