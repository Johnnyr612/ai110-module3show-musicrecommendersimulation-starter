"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs, score_song


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Render the ranked recommendations as a clean, readable terminal layout."""
    width = 60
    header = (
        f"Recommendations for genre='{user_prefs.get('genre')}', "
        f"mood='{user_prefs.get('mood')}', energy={user_prefs.get('energy')}"
    )
    print("=" * width)
    print(header)
    print("=" * width)

    for rank, (song, score, _explanation) in enumerate(recommendations, start=1):
        # Pull the structured reasons back so we can list them one per line.
        _score, reasons = score_song(user_prefs, song)

        print(f"\n#{rank}  {song['title']} - {song['artist']}")
        print(f"    Score: {score:.2f}")
        if reasons:
            print("    Reasons:")
            for reason in reasons:
                print(f"      - {reason}")
        else:
            print("    Reasons: general pick (no strong matches)")

    print("\n" + "=" * width)


def main() -> None:
    """Run the end-to-end CLI simulation: load, recommend, and print."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
