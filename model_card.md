# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The catalog is not evenly spread across genres: 13 of the 15 genres have
exactly one song, while lofi has three and pop has two. That means a user
whose favorite genre is lofi gets three real candidates to rank between,
while a user whose favorite genre is classical or reggae only ever gets one
possible genre match — the system can't tell a "good" classical song from a
"bad" one because there's nothing to compare it against. This directly
mirrors a real-world bias: platforms with more data in mainstream genres give
those listeners richer, more confident recommendations, while niche-taste
listeners get thin results almost by default, not because their taste is
unusual. The genre weight (+2.0) is also strong enough to override a missing
mood match entirely: testing a "favorite_genre=metal, favorite_mood=happy"
profile returned an aggressive metal song in first place, because it was the
only metal song available and genre outweighed the mood mismatch — the
system doesn't have a way to say "no good match exists" when the two signals
disagree, it just picks the least-bad option. Finally, `valence` (the
continuous happy↔sad dimension) is tracked in the data but never scored,
so two songs with very different valence can tie on mood if they share the
same mood label — a real gap in how well the system captures "vibe."

---

## 7. Evaluation  

Tested five profiles against the 18-song catalog: three realistic tastes
(High-Energy Pop, Chill Lofi, Deep Intense Rock) and two adversarial ones
designed to break the system (a genre/mood conflict — "happy metal" — and a
genre that doesn't exist in the catalog at all, "k-pop"). Full outputs are in
the README's "Experiments You Tried" section.

**Pairwise comparisons:**

- **High-Energy Pop vs. Deep Intense Rock** — these landed on completely
  different top songs (Sunrise City vs. Storm Runner) even though both
  target energy ~0.9. That's the point: energy alone isn't the whole story,
  genre and mood pull the ranking toward genuinely different songs even at
  matched intensity. Makes sense — a fan of intense rock and a fan of
  high-energy pop are not asking for the same thing just because both want
  something intense.
- **High-Energy Pop vs. Chill Lofi** — near-total reversal, as expected:
  Chill Lofi's top pick (Library Rain, energy 0.35) would score close to
  zero on energy for the High-Energy Pop profile (target 0.9), and vice
  versa. The energy-closeness formula is doing exactly its job here.
- **Deep Intense Rock vs. Adversarial Happy Metal** — both target energy 0.9
  and both have thin genre pools (1 song each: rock, metal), but Deep
  Intense Rock's mood (`intense`) actually matches its top song while Happy
  Metal's mood (`happy`) doesn't match Iron Requiem's real mood
  (`aggressive`) at all. Both still returned their genre's one song in
  first place — showing the genre weight is strong enough to win even
  when the mood signal actively disagrees with the result, not just when
  it's neutral/absent.
- **What surprised me:** I expected the "unknown genre" adversarial case
  (k-pop) to produce a much weaker or more random-looking list. Instead it
  gracefully fell back to mood + energy matches and still returned a
  coherent top 5 — the scoring recipe degrades sensibly even when one whole
  signal is unavailable, which wasn't guaranteed by the design and was worth
  confirming with an actual test rather than assuming it.

**Weight-shift experiment:** temporarily doubled the energy weight and halved
the genre weight (not shipped — reverted after testing). This flipped the
rank order for the Default profile: Rooftop Lights (mood match, no genre
match) overtook Gym Hero (genre match, no mood match), because a very close
energy match started outweighing a genre match paired with a looser energy
match. Confirms the system is genuinely sensitive to these weight choices,
not just cosmetically — small tuning changes visibly reshuffle who gets
recommended.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
