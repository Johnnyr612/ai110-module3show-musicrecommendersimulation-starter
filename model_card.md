# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
**Song Vibe Searcher**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

VibeFinder suggests songs. You tell it what you like. You give it a genre, a mood, an energy level, and whether you like acoustic or produced tracks. It then ranks the songs and picks the best matches. It also tells you why it picked each one.

It makes a few assumptions about you. It assumes you can name your taste in those four ways. It assumes your taste stays the same during a session. It assumes a good song is one that matches what you asked for. It does not try to surprise you with something new.

This is a classroom project, not a real app. The catalog has only 19 songs. The rules are kept simple on purpose, so they are easy to read and change. The goal is to learn how a recommender turns your preferences into picks. It also shows where bias can sneak in.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The model looks at four things about each song. It looks at the genre, the mood, the energy level, and whether the song is acoustic or produced. You give the model the same four things about yourself.

The model then compares your taste to each song. Each match earns points. A genre match earns points. A mood match earns points. A song close to your energy level earns points. If the sound (acoustic or produced) fits your taste, it gets a small bonus.

Then the model adds up the points for every song. It sorts the songs from most points to fewest. The songs at the top become your picks.

One rule is worth explaining. Energy is scored by closeness, not by size. A song does not win just for being loud. It wins for being close to the energy you asked for.

We started from the simple starter rules. Then we ran an experiment. We made energy count more. We made genre count less. This helped songs that fit your mood and energy, even when the genre label was a little different.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog has 19 songs. Each song lists its genre, mood, energy, tempo, and a few other traits.

Many genres are included. There is pop, lofi, rock, jazz, edm, hip hop, soul, r&b, country, classical, and more. Many moods are included too, like happy, chill, intense, and relaxed.

We did not add or remove any songs. We used the catalog as it came.

Some parts of taste are missing. Most genres have only one song. Only lofi and pop have more than one. So a fan of a rare genre has almost nothing to pick from. There are also no "sad" songs at all. That means a sad mood can never be matched. And the catalog is tiny, so it cannot cover real music taste.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The model works best when your taste matches the catalog. It does well for pop fans and lofi fans. Those genres have several songs to choose from.

The "chill lofi" listener was a great example. The top picks were exactly right. They were quiet, acoustic study songs.

The model is good at reading energy. A calm listener gets calm songs. A loud listener gets loud songs. This felt correct every time we tested it.

The model also explains itself. It tells you why it picked each song. This makes it easy to trust and easy to check.

When a profile had clear matches in the catalog, the top few picks matched our own gut feeling. That is a good sign the scoring works.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

**Weakness discovered: the energy score is "direction-blind."** When I ran the weight-shift experiment (doubling the importance of energy), I noticed the system measures energy purely as the *distance* from the user's target, treating a song that is too calm exactly the same as a song that is too intense. That is a problem, because for a user who wants relaxed music, a song that is slightly calmer than expected is still fine, while a song that is louder and more intense actually ruins the mood yet, the model gives them the identical score. This got worse once energy was weighted more heavily, because a single mismatched song(but close) could outrank a song that genuinely fit the user's vibe. The weakness unfairly affects low-energy listeners (study, sleep, focus music) more than high-energy ones, since a too energetic recommendation is far more disruptive to them than a too-mellow one is to a party listener.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

### Profiles I tested

I ran six imaginary listeners through the system. Three were "normal" people with sensible taste, and three were "trick" profiles designed to try to confuse the scorer:

1. **High-Energy Pop** - wants upbeat, produced pop.
2. **Chill Lofi** - wants quiet, acoustic study music.
3. **Deep Intense Rock** - wants loud, hard rock.
4. **Conflicting (loud but sad)** - a contradiction: max energy *and* acoustic *and* a "sad" mood no song in the catalog actually has.
5. **Empty profile** - a listener who states no preferences at all.
6. **Out-of-range energy** - an energy value of 2.0, which is outside the normal 0-to-1 range, to see if the math would break.

### What surprised me

The biggest surprise was that the **"Gym Hero" problem is not a bug - it's the scoring rules doing exactly what I told them to.** Gym Hero is a pop song with very high energy, but its mood is labeled *intense*, not *happy*. When the "Happy Pop" listener asks for happy music, I expected the happy songs to win. Instead Gym Hero kept landing near the top. The reason, in plain terms: the system gives a lot of points for matching the **genre** (pop) and for matching the **energy level** (loud), but only a small amount of points for matching the **mood** (happy). So a song that is the right genre and the right energy but the *wrong* mood can still beat a song that has the right mood but isn't pop. The listener asked for "happy," but the math quietly cares more about "pop and loud" than about "happy." That was a real eye-opener about how a recommender can look like it's ignoring what you asked for, when really it's just weighing your request differently than you meant it.

### Comparing the profiles two at a time

- **High-Energy Pop vs. Chill Lofi.** These are near-opposites and the outputs proved it. The Pop listener got loud, produced songs at the top (Sunrise City, Gym Hero); the Lofi listener got quiet, acoustic songs (Library Rain, Midnight Coding). Almost no overlap. This makes sense: the two profiles ask for opposite energy levels and opposite production styles, so the scorer sends them in opposite directions. Good sign that the system actually listens to the user.

- **High-Energy Pop vs. Deep Intense Rock.** These share the *same* high energy but a *different* genre, and that's exactly the difference the outputs showed. Both lists were topped by loud songs, and interestingly **Gym Hero appeared high for both** - because it's loud enough to please both, and it matches "pop" for one and "intense" for the other. The main difference was which song sat at #1: Sunrise City (a pop song) for the Pop listener, Storm Runner (a rock song) for the Rock listener. This makes sense - when energy is similar, the genre label becomes the tiebreaker.

- **Chill Lofi vs. Deep Intense Rock.** These are the most opposite pair, and their lists had essentially nothing in common. Lofi got the slowest, most acoustic tracks; Rock got the fastest, loudest ones. This is the clearest proof the profiles are really testing different things.

- **High-Energy Pop vs. Conflicting (loud but sad).** These share the same genre (pop) and both want high energy, so their top songs were similar (Gym Hero, Sunrise City). The revealing difference: the Conflicting listener asked for a "sad" mood, but **no song scored any mood points at all**, because the catalog has no "sad" songs. So the "sad" request was silently ignored, and the listener got loud happy pop anyway. This shows a real weakness - the system doesn't warn you when it can't honor part of your request; it just leaves that part out.

- **Any normal profile vs. Empty profile.** The normal profiles produced clearly ranked lists; the Empty profile produced a list where **every song scored zero**, so the "ranking" was just the order the songs happen to appear in the file. This makes sense (no preferences means nothing to match), but it exposes that a listener who gives no input gets a meaningless list dressed up to look like a real recommendation.

- **Deep Intense Rock vs. Out-of-range energy (2.0).** The normal Rock profile scored songs positively for being loud. The out-of-range profile did the opposite: because 2.0 is outside the expected range, the energy math flipped and started *subtracting* points from songs, dragging almost everything down near zero. This confirmed a bug I suspected - the system trusts the energy number blindly and never checks that it falls between 0 and 1.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

There are many ways to make this better.

First, grow the catalog. Nineteen songs is too few. More songs would give rare genres a real chance.

Second, fix the energy math. Right now it treats "too calm" and "too loud" the same. It should know that a loud song hurts a chill mood more than a quiet one does. It should also block bad values like an energy of 2.0.

Third, add more features. Tempo, danceability, and mood shades could all help. This would let people describe richer taste.

Fourth, handle genres that are close. Right now lofi and ambient are treated as total strangers. The model should know they are neighbors.

Fifth, add some variety to the top picks. The list can feel samey. A little surprise would make it more fun.

Last, help new users. Someone with no preferences gets a useless list. We could ask a few quick questions first.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that a recommender is just points and sorting. It is not magic. You pick what matters. You give each thing a weight. The math does the rest.

The biggest surprise was the "Gym Hero" song. It kept showing up for a happy pop fan, even though it is not a happy song. The system was not broken. It just cared about genre and energy more than mood. I had told it to do that without realizing.

This changed how I see real music apps. When a bad song shows up in my feed, it is not random. Someone chose the rules. The app is showing me what its math thinks I want. That can be helpful. It can also trap me in the same kind of music over and over. Now I understand why that happens.
