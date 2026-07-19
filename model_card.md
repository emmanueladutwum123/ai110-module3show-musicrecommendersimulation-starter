# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeSonar 1.0** — it "pings" a small song catalog with your stated taste
and ranks whatever echoes back closest.

---

## 2. Intended Use  

VibeSonar takes a listener's explicitly stated taste — favorite genre,
favorite mood, a target energy level, and whether they like acoustic songs —
and ranks a small song catalog by how well each song matches, showing the
specific reasons behind every recommendation.

It assumes the listener can put their taste into words up front. It does not
watch what you actually play, skip, or replay — there's no listening history
here, because there are no real users. This is a classroom simulation built
to learn how a basic recommender works end to end, not a production system.
It's meant to run on the toy 18-song catalog in this repo, not on real
streaming data or real listeners.

---

## 3. How the Model Works  

For every song in the catalog, VibeSonar checks a few things and adds up
points:

- Does the song's genre match what you said you like? If yes, that's worth
  the most points of anything it checks.
- Does the song's mood match yours? If yes, that's worth some points too,
  just not as many as genre.
- How close is the song's energy level to the energy you asked for? The
  closer it is, the more points it earns — a song doesn't need to be the
  *most* energetic thing in the catalog, it just needs to be *close* to what
  you wanted.
- If you said you like acoustic songs, a song that's quite acoustic gets a
  small bonus.

Every song ends up with one number (its score) and a short list of plain-
English reasons for that number. Then VibeSonar sorts every song by that
score and hands back the top 5, reasons included.

The starter code was empty (just placeholders that returned nothing). I
built all of the actual scoring math described above, added the acoustic bonus
as a new signal, and made sure the exact same rules apply whether you're
using the simple version (plain data) or the more structured version (proper
song/user objects) — so there's only one true "recipe," not two that could
quietly drift apart.

---

## 4. Data  

The catalog has **18 songs** — the 10 that came with the starter project,
plus 8 I added to cover genres and moods that were completely missing (metal,
classical, hip-hop, reggae, country, r&b, folk, and edm). Between them, the
songs span 15 different genres and 14 different moods.

Each song has: title, artist, genre, mood, energy, tempo, valence,
danceability, and acousticness.

What's missing: most genres in the catalog only have exactly one song, so
there's no real competition to find the "best" song within most genres —
whatever song exists just wins by default. There's also nothing about
lyrics, vocals, production style, or era, and no real listener behavior
(skips, replays, saves) — everything here is a hand-picked, hand-labeled
attribute, not something learned from real listening data.

---

## 5. Strengths  

- When a user's taste clearly matches a song in the catalog, VibeSonar finds
  it convincingly — the Chill Lofi profile scored a perfect 5.00 (the
  maximum possible) on a song that matched genre, mood, energy, and the
  acoustic preference all at once.
- The explanations are genuinely useful, not just decoration — you can see
  exactly which signals contributed to a score instead of trusting a mystery
  number.
- It tells very different tastes apart well: a high-energy pop fan and a
  chill lofi fan land on completely different, sensible top picks even
  though both profiles are "clear" preferences.
- It doesn't break when a preference can't be matched — asking for a genre
  that isn't in the catalog still returns a coherent, reasoned list instead
  of crashing or returning nothing.

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

- Score `valence` too, so mood-matching isn't all-or-nothing. Right now a
  "happy" song and an "uplifting" song are just as far apart as a "happy"
  song and an "aggressive" song, even though the first pair probably feels
  much more similar. Valence would let close-but-not-identical moods still
  get partial credit.
- Make the acoustic bonus scale with *how* acoustic a song is, instead of a
  flat +0.5 the moment it crosses a threshold — the same "closeness, not a
  cutoff" idea already used for energy.
- Grow the catalog so every genre has several songs, so a genre match means
  picking the *best available* song in that genre, not just the *only* one.
- Add an honest "no strong match" signal instead of always confidently
  returning a top 5, even in cases like the unmatched-genre test where the
  system is really just falling back to weaker signals.

---

## 9. Personal Reflection  

The biggest learning moment was the adversarial "happy metal" test. Seeing
an aggressive-mood song get ranked first for someone who explicitly asked
for "happy" music made the idea of algorithmic bias click in a way that
reading about it never did — it wasn't a bug, it was the scoring formula
doing exactly what it was told to do. That's a small, low-stakes version of
exactly how real biased systems behave: not by malfunctioning, but by
faithfully optimizing rules that don't fully capture what people actually
want.

Using AI as a coding partner sped up writing and testing the scoring logic a
lot, especially for coming up with edge cases I wouldn't have thought to test
myself (like the genre that doesn't exist in the catalog at all). But I had
to actually run the code and read the real terminal output to trust any
claim about *why* a song scored the way it did — an explanation that sounds
reasonable isn't the same as one that's been checked against what the code
actually does.

What surprised me most is how convincing a fairly simple weighted-sum
formula can feel once it's wrapped in plain-language reasons. Seeing
"Because: genre match (+2.0); mood match (+1.0)" printed next to a song
makes the system feel a lot smarter than the underlying math actually is —
which is probably true of real recommendation apps too. If I extended this
project, I'd want to add a simulated collaborative-filtering signal (even a
fake "users who picked X also liked Y" table) to compare against the pure
content-based approach, and add a diversity pass so the top 5 aren't all
near-duplicates of each other.
