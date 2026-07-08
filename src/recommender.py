import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Algorithm Recipe: weights (our "design opinion" made explicit).
# These control how many points each matching rule is worth. Genre is highest
# because a genre mismatch is the most jarring; acoustic is a light nudge.
# Tuning the system == editing these four numbers, nothing else.
# ---------------------------------------------------------------------------
WEIGHT_GENRE = 2.0      # +2.0 for an exact genre match  (strongest signal)
WEIGHT_MOOD = 1.0       # +1.0 for an exact mood match
WEIGHT_ENERGY = 1.0     # up to +1.0, scaled by how CLOSE energy is to target
WEIGHT_ACOUSTIC = 0.5   # +0.5 light bonus when acousticness agrees with taste

# A song counts as "acoustic" once its acousticness crosses this line.
ACOUSTIC_THRESHOLD = 0.5


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Shared scoring core.
# Both the OOP Recommender and the functional score_song() call this, so the
# Algorithm Recipe is defined in ONE place. It takes plain values (not a Song
# or a dict) so it doesn't care which API called it.
# Returns (score, reasons) where reasons is a list of short human strings.
# ---------------------------------------------------------------------------
def _score_core(
    pref_genre: Optional[str],
    pref_mood: Optional[str],
    target_energy: Optional[float],
    likes_acoustic: Optional[bool],
    song_genre: Optional[str],
    song_mood: Optional[str],
    song_energy: Optional[float],
    song_acousticness: Optional[float],
) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []

    # R1 — Genre: exact-match categorical. All-or-nothing points.
    if pref_genre is not None and song_genre == pref_genre:
        score += WEIGHT_GENRE
        reasons.append(f"matches your favorite genre ({song_genre})")

    # R2 — Mood: exact-match categorical. Softer than genre, so worth less.
    if pref_mood is not None and song_mood == pref_mood:
        score += WEIGHT_MOOD
        reasons.append(f"matches your mood ({song_mood})")

    # R3 — Energy: scored by CLOSENESS, not size.
    # distance is 0.0 when identical, up to 1.0 when opposite (both are 0..1).
    # 1 - distance flips it so "near the target" earns the most points, in
    # EITHER direction. This is why we don't just reward the loudest song.
    if target_energy is not None and song_energy is not None:
        distance = abs(song_energy - target_energy)
        closeness = 1.0 - distance
        score += closeness * WEIGHT_ENERGY
        # Only mention energy when it's genuinely a good match, else it's noise.
        if closeness >= 0.8:
            reasons.append(
                f"has energy ({song_energy:.2f}) close to your target ({target_energy:.2f})"
            )

    # R4 — Acoustic: a boolean preference maps to reward when the song agrees.
    # Reward acoustic songs if the user likes acoustic; reward produced songs
    # if they don't. If the profile has no opinion (None), skip this rule.
    if likes_acoustic is not None and song_acousticness is not None:
        is_acoustic = song_acousticness >= ACOUSTIC_THRESHOLD
        if likes_acoustic and is_acoustic:
            score += WEIGHT_ACOUSTIC
            reasons.append("it's acoustic, which you like")
        elif not likes_acoustic and not is_acoustic:
            score += WEIGHT_ACOUSTIC
            reasons.append("it's a produced/electronic track, matching your taste")

    return score, reasons


def _build_explanation(reasons: List[str]) -> str:
    """Turn the list of reason fragments into one sentence (never empty)."""
    if not reasons:
        # Fallback so the explanation is always a non-empty string.
        return "It's a general pick that loosely fits your profile."
    return "Recommended because it " + "; ".join(reasons) + "."


def _as_float(value, default: float = 0.0) -> float:
    """CSV values arrive as strings; coerce numeric fields safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        # Adapter: pull fields off the dataclasses and hand them to the core.
        return _score_core(
            pref_genre=user.favorite_genre,
            pref_mood=user.favorite_mood,
            target_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
            song_genre=song.genre,
            song_mood=song.mood,
            song_energy=song.energy,
            song_acousticness=song.acousticness,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # RANKING RULE: score every song, sort best-to-worst, keep the top k.
        # We pair each song with its score, sort by score descending, then
        # strip the scores back off to return plain Song objects (what tests want).
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _score_value in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # Reuse the same reasons the scorer produced — one source of truth.
        _score_value, reasons = self._score(user, song)
        return _build_explanation(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    # newline="" is the documented way to open CSVs so the parser handles
    # quoted fields (like an artist "Lloyd, Lil Wayne") correctly.
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # uses the header row as dict keys
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    # Numeric columns come in as strings, so convert them now.
                    "energy": _as_float(row["energy"]),
                    "tempo_bpm": _as_float(row["tempo_bpm"]),
                    "valence": _as_float(row["valence"]),
                    "danceability": _as_float(row["danceability"]),
                    "acousticness": _as_float(row["acousticness"]),
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # The dict profile from main.py uses keys {"genre","mood","energy"}, but we
    # also accept the dataclass-style keys so either shape works. Missing keys
    # become None, and _score_core simply skips that rule.
    pref_genre = user_prefs.get("genre", user_prefs.get("favorite_genre"))
    pref_mood = user_prefs.get("mood", user_prefs.get("favorite_mood"))
    target_energy = user_prefs.get("energy", user_prefs.get("target_energy"))
    likes_acoustic = user_prefs.get("likes_acoustic")  # None if not provided

    return _score_core(
        pref_genre=pref_genre,
        pref_mood=pref_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
        song_genre=song.get("genre"),
        song_mood=song.get("mood"),
        song_energy=song.get("energy"),
        song_acousticness=song.get("acousticness"),
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # SCORING RULE: score each song and build its explanation up front.
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, _build_explanation(reasons)))

    # RANKING RULE: sort by score (index 1) descending, then take the top k.
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
