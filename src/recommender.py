import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Algorithm Recipe: weights (our "design opinion" made explicit).
# These control how many points each matching rule is worth. Genre is highest
# because a genre mismatch is the most jarring; acoustic is a light nudge.
# Tuning the system == editing these four numbers, nothing else.
# ---------------------------------------------------------------------------
# EXPERIMENT (Weight Shift): energy DOUBLED (1.0 -> 2.0), genre HALVED (2.0 -> 1.0).
# Hypothesis: energy should now dominate ranking and genre should stop burying
# songs that nail the user's target energy but sit in a neighboring genre.
WEIGHT_GENRE = 1.0      # was 2.0, halved: genre is now only as strong as mood
WEIGHT_MOOD = 1.0       # +1.0 for an exact mood match (unchanged)
WEIGHT_ENERGY = 2.0     # was 1.0, doubled: up to +2.0, scaled by energy closeness
WEIGHT_ACOUSTIC = 0.5   # +0.5 light bonus when acousticness agrees with taste

# --- Challenge 1: weights for the five NEW advanced features ---------------
# These are deliberately smaller than genre/mood/energy so the core taste
# match still leads, and the new features act as refinements / tie-breakers.
WEIGHT_DECADE = 0.75        # +0.75 when the song's release decade matches
WEIGHT_MOOD_TAG = 0.25      # +0.25 per matching detailed mood tag ...
WEIGHT_MOOD_TAG_CAP = 0.75  # ... but no more than +0.75 total from tags
WEIGHT_POPULARITY = 0.5     # up to +0.5, scaled by how CLOSE popularity is
WEIGHT_LANGUAGE = 0.5       # +0.5 for an exact language match
WEIGHT_EXPLICIT = 0.5       # +0.5 for a clean track (or -0.5 penalty) when the
                            # user asked to avoid explicit content

# A song counts as "acoustic" once its acousticness crosses this line.
ACOUSTIC_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Challenge 2: Scoring Modes.
# A "mode" is just a named set of weights. Switching modes swaps which signal
# dominates the ranking WITHOUT touching any scoring code. The five advanced
# Challenge 1 features keep the same weights across every mode; a mode only
# changes the four core rules (genre / mood / energy / acoustic).
# ---------------------------------------------------------------------------

# The full default weight set, assembled from the constants above. Every mode
# starts from this and overrides only the core keys it cares about.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": WEIGHT_GENRE,
    "mood": WEIGHT_MOOD,
    "energy": WEIGHT_ENERGY,
    "acoustic": WEIGHT_ACOUSTIC,
    "decade": WEIGHT_DECADE,
    "mood_tag": WEIGHT_MOOD_TAG,
    "mood_tag_cap": WEIGHT_MOOD_TAG_CAP,
    "popularity": WEIGHT_POPULARITY,
    "language": WEIGHT_LANGUAGE,
    "explicit": WEIGHT_EXPLICIT,
}

MODES: Dict[str, Dict[str, float]] = {
    # Balanced: the original starter design. Genre leads, energy is gentle.
    "balanced":       {"genre": 2.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5},
    # Genre-First: genre dominates. You never get a "wrong genre" song near the
    # top, but great cross-genre picks stay buried.
    "genre-first":    {"genre": 3.0, "mood": 1.0, "energy": 1.0, "acoustic": 0.5},
    # Mood-First: the vibe wins. A happy song in a neighboring genre can now
    # beat a same-genre song that has the wrong mood.
    "mood-first":     {"genre": 1.0, "mood": 3.0, "energy": 1.0, "acoustic": 0.5},
    # Energy-Focused: closeness to the target energy dominates. Matches the
    # Experiment 1 weights and the Challenge 1 sample output in the README.
    "energy-focused": {"genre": 1.0, "mood": 1.0, "energy": 2.0, "acoustic": 0.5},
}

# The mode used when a caller does not name one. Kept as "energy-focused" so
# default behavior matches the numbers already documented in the README.
DEFAULT_MODE = "energy-focused"


def resolve_weights(mode: Optional[str] = None) -> Dict[str, float]:
    """
    Turn a mode name into a full weight dict. Unknown or missing modes fall back
    to DEFAULT_MODE. Advanced-feature weights come from DEFAULT_WEIGHTS; the mode
    overrides only the four core rules.
    """
    chosen = mode if mode in MODES else DEFAULT_MODE
    return {**DEFAULT_WEIGHTS, **MODES[chosen]}


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
    # Challenge 1: advanced features. Defaults keep older callers/tests (which
    # build a Song with only the 10 fields above) working unchanged.
    popularity: float = 0.0        # 0..100 mainstream popularity
    release_decade: int = 0        # e.g. 1990, 2000, 2010, 2020
    mood_tags: str = ""            # pipe-separated detailed tags, "euphoric|bright"
    language: str = ""             # "english", "spanish", "instrumental", ...
    explicit: bool = False         # True if the track has explicit content

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
    # Challenge 1: preferences for the new features. All optional (None = "no
    # opinion"), so a 4-field UserProfile still constructs and scores fine.
    favorite_decade: Optional[int] = None
    desired_tags: Optional[List[str]] = None
    target_popularity: Optional[float] = None
    favorite_language: Optional[str] = None
    avoid_explicit: Optional[bool] = None


# How close a graded match must be before it earns ANY points. Below this,
# "close" is really "not a match" and should score zero, not partial credit.
CLOSENESS_FLOOR = 0.5


def _graded_points(closeness: float, weight: float, floor: float = CLOSENESS_FLOOR) -> float:
    """
    Turn a 0..1 closeness into points, paying ZERO at or below `floor`.

    Old behavior paid `closeness * weight`, so a song only vaguely near the
    target still banked partial points. This rescales the [floor, 1.0] band to
    [0, 1.0], so only genuinely close matches score and far-off songs earn 0
    (never negative, which also tames out-of-range inputs).
    """
    if closeness <= floor:
        return 0.0
    return (closeness - floor) / (1.0 - floor) * weight


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
    # Challenge 1: advanced-feature preferences + song values (all optional).
    pref_decade: Optional[int] = None,
    desired_tags: Optional[List[str]] = None,
    target_popularity: Optional[float] = None,
    pref_language: Optional[str] = None,
    avoid_explicit: Optional[bool] = None,
    song_popularity: Optional[float] = None,
    song_release_decade: Optional[int] = None,
    song_mood_tags: Optional[str] = None,
    song_language: Optional[str] = None,
    song_explicit: Optional[bool] = None,
    # Challenge 2: the active mode's weight set. None -> the default mode.
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Apply the scoring rules to plain values; return (score, reasons).

    `weights` selects the scoring mode. Every rule reads its point value from
    this dict, so swapping modes changes the ranking without changing any logic.
    """
    w = weights if weights is not None else DEFAULT_WEIGHTS
    score = 0.0
    reasons: List[str] = []

    # R1 — Genre: exact-match categorical. All-or-nothing points.
    if pref_genre is not None and song_genre == pref_genre:
        score += w["genre"]
        reasons.append(f"genre match: {song_genre} (+{w['genre']:.1f})")

    # R2 — Mood: exact-match categorical. Softer than genre, so worth less.
    if pref_mood is not None and song_mood == pref_mood:
        score += w["mood"]
        reasons.append(f"mood match: {song_mood} (+{w['mood']:.1f})")

    # R3 — Energy: scored by CLOSENESS, not size.
    # distance is 0.0 when identical, up to 1.0 when opposite (both are 0..1).
    # 1 - distance flips it so "near the target" earns the most points, in
    # EITHER direction. This is why we don't just reward the loudest song.
    if target_energy is not None and song_energy is not None:
        distance = abs(song_energy - target_energy)
        closeness = 1.0 - distance
        # Closeness floor: a song more than 0.5 away in energy earns NOTHING,
        # instead of banking partial credit just for being vaguely in range.
        energy_points = _graded_points(closeness, w["energy"])
        score += energy_points
        # Only mention energy when it's genuinely a good match, else it's noise.
        if energy_points > 0 and closeness >= 0.8:
            reasons.append(
                f"energy match: {song_energy:.2f} vs target {target_energy:.2f} "
                f"(+{energy_points:.2f})"
            )

    # R4 — Acoustic: a boolean preference maps to reward when the song agrees.
    # Reward acoustic songs if the user likes acoustic; reward produced songs
    # if they don't. If the profile has no opinion (None), skip this rule.
    if likes_acoustic is not None and song_acousticness is not None:
        is_acoustic = song_acousticness >= ACOUSTIC_THRESHOLD
        if likes_acoustic and is_acoustic:
            score += w["acoustic"]
            reasons.append(f"acoustic match: you like acoustic (+{w['acoustic']:.1f})")
        elif not likes_acoustic and not is_acoustic:
            score += w["acoustic"]
            reasons.append(f"acoustic match: you like produced tracks (+{w['acoustic']:.1f})")

    # -----------------------------------------------------------------------
    # Challenge 1 rules for the five new advanced features. Each follows the
    # same shape as above: skip if the user has no opinion (None), otherwise
    # add points and record a human-readable reason.
    # -----------------------------------------------------------------------

    # R5 - Decade: exact-match categorical, like genre but for era.
    if pref_decade is not None and song_release_decade == pref_decade:
        score += w["decade"]
        reasons.append(f"decade match: {song_release_decade}s (+{w['decade']:.2f})")

    # R6 - Mood tags: partial credit. Count how many of the detailed tags the
    # user wants are present on the song, pay per tag, then cap the total.
    if desired_tags and song_mood_tags:
        wanted = _as_tag_set(desired_tags)
        have = _as_tag_set(song_mood_tags)
        matched = sorted(wanted & have)
        if matched:
            tag_points = min(len(matched) * w["mood_tag"], w["mood_tag_cap"])
            score += tag_points
            reasons.append(f"mood tags: {', '.join(matched)} (+{tag_points:.2f})")

    # R7 - Popularity: scored by CLOSENESS to the user's target, mirroring the
    # energy rule. Distance is normalized by 100 since popularity is 0..100.
    if target_popularity is not None and song_popularity is not None:
        distance = abs(song_popularity - target_popularity) / 100.0
        closeness = 1.0 - distance
        # Same closeness floor: songs more than ~50 points of popularity away
        # earn nothing, so this stops being a near-flat bonus for everyone.
        pop_points = _graded_points(closeness, w["popularity"])
        score += pop_points
        if pop_points > 0 and closeness >= 0.8:
            reasons.append(
                f"popularity match: {song_popularity:.0f} vs target "
                f"{target_popularity:.0f} (+{pop_points:.2f})"
            )

    # R8 - Language: exact-match categorical.
    if pref_language is not None and song_language == pref_language:
        score += w["language"]
        reasons.append(f"language match: {song_language} (+{w['language']:.2f})")

    # R9 - Explicit: only acts when the user wants to AVOID explicit content.
    # A clean track is rewarded; an explicit track is penalized (real filter).
    if avoid_explicit and song_explicit is not None:
        if not song_explicit:
            score += w["explicit"]
            reasons.append(f"clean track: no explicit content (+{w['explicit']:.2f})")
        else:
            score -= w["explicit"]
            reasons.append(f"explicit content: you asked to avoid it (-{w['explicit']:.2f})")

    return score, reasons


def _build_explanation(reasons: List[str]) -> str:
    """Turn the list of reason fragments into one sentence (never empty)."""
    if not reasons:
        # Fallback so the explanation is always a non-empty string.
        return "It's a general pick that loosely fits your profile."
    return "Recommended for " + "; ".join(reasons) + "."


def _as_float(value, default: float = 0.0) -> float:
    """CSV values arrive as strings; coerce numeric fields safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value, default: int = 0) -> int:
    """Coerce a CSV field to int safely (e.g. release_decade)."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _as_bool(value, default: bool = False) -> bool:
    """Coerce a CSV field like 'True'/'False'/'1'/'0' to a real bool."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _as_tag_set(value) -> set:
    """
    Normalize mood tags into a lowercase set. Accepts either a pipe-separated
    string ("euphoric|bright") or an already-split list (["euphoric", "bright"]).
    """
    if not value:
        return set()
    parts = value.split("|") if isinstance(value, str) else list(value)
    return {str(tag).strip().lower() for tag in parts if str(tag).strip()}


# ---------------------------------------------------------------------------
# Challenge 3: Diversity / Fairness logic.
#
# The rule (plain English):
#   As we build the top-k list, penalize a candidate song for every song
#   ALREADY chosen that shares its artist or its genre. So the first song by an
#   artist is scored normally; a SECOND song by that same artist is docked
#   DIVERSITY_ARTIST_PENALTY; a third is docked twice, and so on. Genre repeats
#   are docked more gently. This can't be done in per-song scoring because the
#   penalty depends on what is already in the list, so we re-rank greedily:
#   pick the current best, record its artist/genre, then re-score the rest.
#
# Artist repetition is penalized harder than genre, because two songs by the
# same artist feel more redundant than two songs in the same genre.
# ---------------------------------------------------------------------------
DIVERSITY_ARTIST_PENALTY = 1.5   # per earlier song by the SAME artist
DIVERSITY_GENRE_PENALTY = 0.75   # per earlier song in the SAME genre


def _diverse_order(
    items: list,
    base_scores: List[float],
    artist_of,
    genre_of,
    k: int,
    artist_penalty: float = DIVERSITY_ARTIST_PENALTY,
    genre_penalty: float = DIVERSITY_GENRE_PENALTY,
) -> List[Tuple[int, float, float, int, int]]:
    """
    Greedy diversity re-ranking. Returns a list of
    (index, adjusted_score, penalty, artist_hits, genre_hits), best first.

    `artist_of` / `genre_of` are accessors so this works for both dict songs
    (functional API) and Song dataclasses (OOP API).
    """
    used: set = set()
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    order: List[Tuple[int, float, float, int, int]] = []

    limit = min(k, len(items))
    while len(order) < limit:
        best = None  # (index, adjusted, penalty, artist_hits, genre_hits)
        for i, item in enumerate(items):
            if i in used:
                continue
            artist_hits = artist_counts.get(artist_of(item), 0)
            genre_hits = genre_counts.get(genre_of(item), 0)
            penalty = artist_hits * artist_penalty + genre_hits * genre_penalty
            adjusted = base_scores[i] - penalty
            # Strictly-greater keeps ties resolved by original order (stable).
            if best is None or adjusted > best[1]:
                best = (i, adjusted, penalty, artist_hits, genre_hits)

        idx = best[0]
        chosen = items[idx]
        artist_counts[artist_of(chosen)] = artist_counts.get(artist_of(chosen), 0) + 1
        genre_counts[genre_of(chosen)] = genre_counts.get(genre_of(chosen), 0) + 1
        used.add(idx)
        order.append(best)

    return order


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], mode: Optional[str] = None):
        """Store the song catalog and the default scoring mode for this instance."""
        self.songs = songs
        # Challenge 2: remember which mode to rank with. None -> DEFAULT_MODE.
        self.mode = mode or DEFAULT_MODE

    def _score(
        self, user: UserProfile, song: Song, weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, List[str]]:
        """Score one Song against a UserProfile via the shared scoring core."""
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
            # Challenge 1 features.
            pref_decade=user.favorite_decade,
            desired_tags=user.desired_tags,
            target_popularity=user.target_popularity,
            pref_language=user.favorite_language,
            avoid_explicit=user.avoid_explicit,
            song_popularity=song.popularity,
            song_release_decade=song.release_decade,
            song_mood_tags=song.mood_tags,
            song_language=song.language,
            song_explicit=song.explicit,
            # Challenge 2: the resolved weights for the chosen mode.
            weights=weights if weights is not None else resolve_weights(self.mode),
        )

    def recommend(
        self, user: UserProfile, k: int = 5, mode: Optional[str] = None, diversity: bool = True
    ) -> List[Song]:
        """Return the top-k Songs for a user, ranked highest score first.

        Pass `mode` to override this instance's default mode for one call.
        Pass `diversity=False` to skip the Challenge 3 artist/genre spread.
        """
        # RANKING RULE: score every song first (best-to-worst by base score).
        weights = resolve_weights(mode or self.mode)
        base = [self._score(user, song, weights)[0] for song in self.songs]

        if diversity:
            # Challenge 3: greedily re-rank so one artist/genre can't dominate.
            order = _diverse_order(
                self.songs, base, lambda s: s.artist, lambda s: s.genre, k
            )
            return [self.songs[i] for i, _adj, _pen, _a, _g in order]

        scored = sorted(zip(self.songs, base), key=lambda pair: pair[1], reverse=True)
        return [song for song, _score_value in scored[:k]]

    def explain_recommendation(
        self, user: UserProfile, song: Song, mode: Optional[str] = None
    ) -> str:
        """Build a one-sentence, human-readable reason for recommending a song."""
        # Reuse the same reasons the scorer produced — one source of truth.
        weights = resolve_weights(mode or self.mode)
        _score_value, reasons = self._score(user, song, weights)
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
                    # Challenge 1: advanced features. .get(...) keeps this
                    # backward-compatible with an old CSV that lacks the columns.
                    "popularity": _as_float(row.get("popularity")),
                    "release_decade": _as_int(row.get("release_decade")),
                    "mood_tags": row.get("mood_tags", "") or "",
                    "language": row.get("language", "") or "",
                    "explicit": _as_bool(row.get("explicit")),
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: Optional[str] = None) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    `mode` selects the Challenge 2 scoring mode (None -> DEFAULT_MODE).
    """
    # The dict profile from main.py uses keys {"genre","mood","energy"}, but we
    # also accept the dataclass-style keys so either shape works. Missing keys
    # become None, and _score_core simply skips that rule.
    pref_genre = user_prefs.get("genre", user_prefs.get("favorite_genre"))
    pref_mood = user_prefs.get("mood", user_prefs.get("favorite_mood"))
    target_energy = user_prefs.get("energy", user_prefs.get("target_energy"))
    likes_acoustic = user_prefs.get("likes_acoustic")  # None if not provided

    # Challenge 1: accept both short dict keys and dataclass-style keys.
    pref_decade = user_prefs.get("decade", user_prefs.get("favorite_decade"))
    desired_tags = user_prefs.get("mood_tags", user_prefs.get("desired_tags"))
    target_popularity = user_prefs.get("popularity", user_prefs.get("target_popularity"))
    pref_language = user_prefs.get("language", user_prefs.get("favorite_language"))
    avoid_explicit = user_prefs.get("avoid_explicit")

    return _score_core(
        pref_genre=pref_genre,
        pref_mood=pref_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
        song_genre=song.get("genre"),
        song_mood=song.get("mood"),
        song_energy=song.get("energy"),
        song_acousticness=song.get("acousticness"),
        # Challenge 1 features.
        pref_decade=pref_decade,
        desired_tags=desired_tags,
        target_popularity=target_popularity,
        pref_language=pref_language,
        avoid_explicit=avoid_explicit,
        song_popularity=song.get("popularity"),
        song_release_decade=song.get("release_decade"),
        song_mood_tags=song.get("mood_tags"),
        song_language=song.get("language"),
        song_explicit=song.get("explicit"),
        # Challenge 2: resolve the chosen mode to its weight set.
        weights=resolve_weights(mode),
    )


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Optional[str] = None,
    diversity: bool = True,
) -> List[Tuple[Dict, float, List[str]]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns a list of (song, score, reasons) triples, best first.
    - `mode` selects the Challenge 2 scoring mode (None -> DEFAULT_MODE).
    - `diversity` toggles the Challenge 3 artist/genre spread (on by default).
      When the penalty fires, an extra "diversity penalty" reason is added and
      the score shown is the penalized score.
    """
    # SCORING RULE: score each song independently -> (song, base_score, reasons).
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]

    # Plain ranking: sort by base score, keep the top k.
    if not diversity:
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        return [(song, score, reasons) for song, score, reasons in ranked[:k]]

    # RANKING RULE (Challenge 3): greedily re-rank so one artist or genre can't
    # dominate. Each pick penalizes remaining songs that repeat its artist/genre.
    base = [item[1] for item in scored]
    order = _diverse_order(
        songs, base, lambda s: s.get("artist"), lambda s: s.get("genre"), k
    )

    results: List[Tuple[Dict, float, List[str]]] = []
    for idx, adjusted, penalty, artist_hits, genre_hits in order:
        song, _base, reasons = scored[idx]
        reasons = list(reasons)
        if penalty > 0:
            parts = []
            if artist_hits:
                parts.append(f"{artist_hits}x same artist ({song.get('artist')})")
            if genre_hits:
                parts.append(f"{genre_hits}x same genre ({song.get('genre')})")
            reasons.append(f"diversity penalty: {', '.join(parts)} (-{penalty:.2f})")
        results.append((song, adjusted, reasons))
    return results
