# Story Animation Channel: Project Context

Everything decided and built so far for the Roblox-style animated story channel (YouTube Shorts + TikTok). This document lets anyone (or any AI session) pick the project up without the original chat.

---

## 1. Goal

A faceless short-form channel posting **addictive, serialized, Roblox-style animated stories**: cliffhangers people come back for, recurring characters, heavy visual feedback ("dopamine"), and comment-driving hooks. The target is monetization via TikTok Creator Rewards (videos over 1 min) and YouTube Shorts, with paid "Series" episodes as a possible later add-on.

## 2. Market research (Nov 2026)

- Roblox-style story animations ("In this town…", "In my town…") are **flooding** TikTok/Shorts. AI tools mass-produce the format (a rule, a disaster, a twist), so plain one-offs are commoditising.
- **Highest comment ratio observed:** "In my town the mayor banned L and R… then a girl said 'library'" (~21.8K likes / 1.7K comments). **Play-along rules** make viewers comment their own answers.
- **Brainrot / absurdist humour** is the hottest Roblox content category of 2026.
- **Recurring casts win:** the AI "Fruit Love Island" serialized drama hit 3M followers / 300M views in ~9 days. Almost all "In this town" channels are one-offs.
- **The gap we're exploiting:** play-along rule + absurd humour + hypnotic visual escalation + the same cast every episode, set **"In my hood"** (an American block) instead of the saturated "In my town".

## 3. Episodes made

| # | Title | Length | Notes |
|---|---|---|---|
| 1 | **NIGHT RULES Ep1: "The Silent Night"** | 1:22 | Kofi, West-African-inspired town Ashwe, Anansi the spider. Spooky/cliffhanger. Blender + Cycles stills with Ken Burns moves. |
| 2 | **Zara's Birthday Power, Part 1** | 1:12 | Bright suburb; every kid gets a power at 10; Zara's is stopping time. First fully animated (Workbench) episode. Feedback: "boring, no retention, no comment dispute". |
| 3 | **IN MY HOOD Ep1: "Whatever number you say…"** | 1:03 | See §4. |
| 4 | **IN MY TOWN Ep1: "Everyone steals eggs"** | 1:01 | Famous-Roblox-game parody (Steal An Egg), one narrator voice, EEVEE renders, hypnotic beats. See §4b. |
| 5 | **ON MY BLOCK Ep1: "Everybody got motion… except me"** | 1:01 | **Current main format.** YN cast, Dre narrates, funnier. See §4a. |

## 4a. ON MY BLOCK: the main format (from Nov 2026)

**Why:** the IN MY HOOD video performed best, so the channel now centres on the hood flow. The owner wants it **funnier** and the **main cast to be YNs** (young hood dudes: drip, chains, durags, slang, jokes). Keep it to drip and comedy, with no guns or crime.
**Vibe / hook:** "On my block, everybody got motion… except me." The narrator is the broke one, and the jokes are self-own reveals.
**Workflow rule:** write 2–3 storyline options first and get the owner's pick **before** generating the voice or building anything.

**Cast (YNs):**
- **Dre**: narrator, broke and funny. Navy durag, white tee, grey sweats. Voice: "Dre - On My Block narrator" (designed, `vA7VdYNRDShiWPeVQjRp`). He narrates everything and does everyone's voices, so there is **one voice only**.
- **Milo**: red hoodie, fade, gold chain. Has a gold whip at 12, and roasts Dre.
- **Big Kev**: huge, black hoodie, cornrows, chain so heavy he can't stand up straight (a pizza-sized "K" pendant).
- **Uncle Ray**: runs the deli (cap, beard, apron) and gives terrible "wise" advice.
- **Lil bro**: one year old, shades and a chain, richer than everyone.

**Ep1 script:** everybody's motion → Dre's library card → lemonade sold to himself → "them is Crocs" → Ray: "you just gotta… MOVE" → he literally can't stop moving (block → city → OHIO → round a tiny planet) → Kev: "bro, how you stop?" → "I DON'T KNOW!!!" End card: **HOW DOES HE STOP? wrong answers only 👇 PART 2**.
**Hypnotic beats:** money rain; a Droste zoom into a deli inside a deli inside a deli (STORES counter racing); lil bro's net-worth counter; a hero sunburst on TODAY; a running loop round a tiny planet with tunnel rings; and the end-card tunnel.
**Part 2 ideas:** how he stops (Uncle Ray says "stop" in Ohio); everybody got drip except Dre; everybody got a plug except Dre.

## 4b. IN MY TOWN: famous Roblox games, one narrator (Nov 2026)

**Format:** "In my town, everyone [does the famous Roblox game]." Each episode parodies whatever is #1 on Roblox right now (Nov 2026: **Steal An Egg**, ~820K avg / 7.6M peak players, ahead of Throw Food For Animals, Brookhaven, Blox Fruits). Next candidates: Grow a Garden ("everyone grows a garden"), Steal a Brainrot, 99 Nights, Dress to Impress.

**Narrator / hero: Toby.** Green hoodie, navy pants, chunky brown hair. He narrates everything in first person and quotes everyone else, so **one voice only**.

**Character look (all characters, from the approved reference image):** R6 build (torso 2x2x1, arms and legs 1x2x1 that sit flush), rounded bevelled blocks (4-segment bevels, smooth shading), head at about 0.62x torso width with soft rounded corners, and painted faces in the reference style: small black oval eyes with one white glint, a D-shaped open smile with a white teeth strip, no blush. Every expression (happy, excited, laugh, talk, blink, sad, shocked, scared, determined, smug) is drawn in that style (`faces.py`, `lib.py`). The reference image sets the proportions, roundness, face style and build, not a specific outfit.

**Ep1 script (one ElevenLabs take, cut per shot by Whisper word timings):**
1. In my town, everyone steals eggs. EVERYONE. *(low-angle sprint at camera)*
2. My mom? Steals eggs. 3. My teacher? Steals eggs. 4. Even the COPS steal eggs!
5. Whoever has the most eggs… runs the whole town. *(mayor on an egg mountain)*
6. And me? I had one. One tiny, cracked, sad little egg.
7. Until last night… 8. I saw it. A GOLDEN egg! On top of the mayor's house!
9. Rule number one in my town: never… touch… the mayor's egg.
10. So obviously… I touched the mayor's egg. 11. RUN!!! *(the in-game "RUN!!" prompt)*
12. My mom? Chasing me. My teacher? Chasing me. The cops? DEFINITELY chasing me!
13. I made it home, slammed the door, put it down… and it started to crack.
14. The whole town went silent. 15. Because what came out of that egg… was NOT a pet.
16. End card: **WHAT HATCHED? 🥚 wrong answers only 👇 PART 2**

**Hypnotic beats (keep at least one every ~10 s):** an endless spiral of eggs raining onto the mayor's mountain with an orbiting camera and a racing counter; rotating sunburst rays plus tunnel rings behind the golden egg; a red/white spinning burst on RUN!!; endless marching columns of chasers with a racing CHASERS counter; the whole town frozen in perfect concentric rings with a slow spiral up to overhead; and the hatch, where rays and rings speed up into a white-out.

**Comment bait:** "What hatched? Wrong answers only." Part 2 ideas: what hatched, the mayor's revenge, Grow a Garden crossover.

## 4c. IN MY TOWN: The Game (cinematic universe, Nov 2026)

**Brief from the owner:** a cinematic family-adventure series in an ordinary British town (library, corner shop, park bandstand, clock tower). The palette is midnight blue, amber streetlights, emerald green and gold, with feature-film cameras.
**Production rules:**
- Nothing static for 5 s.
- Don't reveal the biggest spectacle in the opening.
- No follow/subscribe outro: the story ends and loops.

**Style decision:** the owner first asked for Pixar-like models. Image-to-3D (Meshy) and AI video weren't available (no key, paid plans), and they rejected hand-built "smooth" models, so they chose **the Roblox look** (R6 rig and painted faces, `town/rcast.py`) inside cinematic EEVEE sets.
**Cast (from their character sheet):**
- **Jayden**: black puffer, curly top. He rolls the dice.
- **Maya**: pink crop hoodie, long curls, hoops. She stops him and finds the solution.
- **Leo**: denim jacket, swoopy brown hair. Comic relief.
- **Tyrone**: green hoodie, glasses, big. Fights the croc with a chair.
- **Rico**: black, backwards cap. Films everything and **narrates**.
- **Whiskers**: tabby cat. Secretly the sixth player; wears the golden crown.

**Ep1 script (approved upgrade):** "In my town there's one game you're never allowed to play" → the board is a **map of our town** (each roll turns a real place into a level, which sets up the series) → Maya: "Jayden, don't!" → he rolls → the windows shatter in bullet-time → crocodile → Tyrone plus chair → Rico's phone POV → GAME: "Six players. Six squares." → Maya: "There's only five of us" → everyone turns to the cat → Whiskers rolls → emerald vortex to the jungle → "Guys… where's Whiskers?" → ROAR, Whiskers on a branch in a crown → GAME: "The final player has been selected", and the trees turn to face them → "And that's why…" loops into "In my town…". A hidden detail in s09 (Whiskers nudging the dice) drives rewatches and comments.
**Voices:**
- Rico: designed, `QqO8z07M2DIuW3MHy5SL`.
- Maya: Evie, `KpKlC1Ey74H3XPtTv7nv`.
- Leo: Peter, `Y8bH5VlCiEtvsc2vu6df`.
- The game: Ben Lucas `DlSZgkElKXmDKq713bQ6`, pitched −4 semitones with reverb.

**Files:** `pipeline/town/` (`game.py` sets/shots, `town_timeline.py`, `town_compose.py` grade/bloom/phone UI/captions, `town_audio.py`). Rendering takes about 20 s/frame per process (two in parallel).
**Next episodes:** the corner shop square, the park bandstand, the clock tower (the boss level).

## 4. IN MY HOOD: format

**Logline:** In my hood, whatever number you say out loud… that's how many of you pull up.

**Cast** (mostly Black characters, written as real, likeable people; no stereotypes or caricature accents):
- **Zara**: narrator, purple puffer jacket, puffs. Deadpan and funny.
- **Lil Milo**: class clown, red hoodie, fade. Says "ten", becomes ten Milos, then a million.
- **Ms. Johnson**: teacher, mustard cardigan, afro, glasses. "Milo, baby, how old are you?"
- **Uncle Ray**: runs the corner deli, apron, cap, grey beard. Prices are just "A LIL SUM".
- **Baby brother**: says his first word at the end… it's a number.
- Block kids: afro, cornrows (+ chain), locs, ponytail, fade.

**Ep1 script:**
1. *In my hood, whatever number you say out loud… that's how many of you pull up!* (a kid says "2!" and a second kid pops in)
2. *So nobody round here says numbers. Like, EVER.* (people covering mouths, NO NUMBERS sign)
3. *The corner store don't even have prices!* (Uncle Ray's "A LIL SUM / $ ???" sign)
4. *Birthday cakes look like this.* ("?" candle)
5. *And math class? Ms. Johnson just be guessing.* (board: "1 + 1 = 3??", "MAYBE 7?")
6. *Then… she made a mistake.* (record scratch)
7. **Ms. Johnson:** *Milo, baby, how old are you?*
8. **Milo (inner monologue, thought bubble):** *Okay okay okay… just say a number, bro. How bad could it be?*
9. **Milo:** *Uhh… ten?* (9 clones POP in with rising pitch; MILO COUNT ticker 1 → 10)
10. *Ten Milos!* / *And not ONE of 'em did the homework.* (bonk montage)
11. **Milo clone:** *Yo! It's like a MILLION of us!*
12. **Zara:** *…Bro.* (deadpan, arms crossed)
13. *A million Milos! Every block! Every stoop! Every corner store!* (hypnotic flood; counter races to 1,000,000)
14. **Uncle Ray:** *Y'all stay CALM! Whatever you do… do NOT say ZERO!*
15. *And that's when my baby brother said his first word… It was a number.*
16. End card: **"What number would YOU say? 👇 PART 2"**

**Comment bait:** "what number would you say?" + "what happens at zero?"

**Next episode ideas:** someone says "zero"; someone says "infinity"; someone says "half"; Uncle Ray's prices; Ms. Johnson's math test.

## 5. Voices (ElevenLabs, model `eleven_v4`)

| Character | Voice | voice_id |
|---|---|---|
| Zara (hood) | Margot, bright & upbeat | `tAtHhBlA3E0eKZJKNSKE` |
| Lil Milo | VALF, energetic kid | `loY1uopAz31XyhAEhNSa` |
| Ms. Johnson | Ms. Harris, warm Southern | `u0REnIJvUgcGQYW2Ux8K` |
| Uncle Ray | Carter D, comedic New York | `GorLj2SsI4u2JqL58gAA` |
| Zara (birthday ep) | Gudiya, kid narrator | `e3FEEanj39p8QCSMe8iV` |
| Milo (birthday ep) | Teddy Twinkle | `XjGYkUkzth8BPs29fmcV` |
| Kofi (Night Rules) | Liam | `TX3LPaxmHKxFdv7VOQHJ` |
| **Dre (ON MY BLOCK, the only voice, current)** | Dre - On My Block narrator (designed: hype, funny, young adult East Coast) | `vA7VdYNRDShiWPeVQjRp` |
| **Toby (IN MY TOWN, the only voice)** | Toby - In My Town narrator (designed: energetic, extroverted, youthful American male) | `1BempFyI57oP6ldXrZtr` |
| **IN MY TOWN: The Game** | Rico = Caliph - Upbeat Gamer `GzrA7L2rl4TVlFYss7aF`; Maya = Hallie - Fun, Young & Feminine `jpICOesdLlRSc39O1UB5`; Leo + game voice (pitched down) = Dre `vA7VdYNRDShiWPeVQjRp`. No British voices: user wants American, energetic, extroverted. |

- Use audio tags in prompts: `[excited]`, `[whispering]`, `[deadpan]`, `[panicking]`, etc.
- The account is on the **free plan (10k credits/month)**. Free-plan audio isn't licensed for commercial use, so upgrade to Starter before monetising.
- Workflow: generate in ElevenLabs, download, put the MP3s in the project, then `hsplit.py` splits each narration take into per-shot lines (DTW alignment against a Kokoro reference + pause snapping).

## 6. Music

- Background: **TEMPOREX – "Numbers" (instrumental)**, ducked under the voices. It's copyrighted, so **add it inside TikTok** at 15–20% volume rather than baking it in (licensed, and the video appears on the sound's page). Post the `_no_music` render.
- Older episodes use synthesized in-house scores (no licensing issues).

## 7. Visual style rules

- IN MY TOWN renders with **EEVEE Next** (8 samples, sun + sky world, real soft shadows: `EEVEE=1`, `eevee_patch.py`). That's about 7–9 s/frame per process; run two processes in parallel on 4 cores, about 1h40 for a 61 s episode. Workbench shadows break on the software GL in the cloud container, so older episodes render with shadows off.
- Vertical 9:16, final 1080×1920, 24 fps, Blender **Workbench** (texture colour mode, "outdoor" studio light, shadows + cavity). It renders at roughly 3–4 s/frame on 2 CPU cores.
- Blocky R6-style characters with rounded edges; **faces are painted textures** (one clean plane per expression: happy, excited, laugh, sad, shocked, scared, determined, blink, smug, talk). Expressions swap over time.
- Constant movement: idle bob, walks/runs, jumps, dances, laughs, flailing, head turns, blinks.
- Visual feedback every 1–2 s: emoji pops, text slams (POP!, BONK!, ZERO), confetti, sparkles, shockwave rings, speed lines, flashes, zoom punches, screen shake, colour grades (freeze/blue/dark), red danger pulses, speech and thought bubbles, a hypnotic counter.
- Captions: one word at a time, white with a thick black outline; "hot" words in yellow and bigger, with a pop-in scale.
- Every episode ends on a cliffhanger plus a comment question plus "PART 2".

## 8. Posting

- UK evening slot (~17:00–19:00); Fridays strongest; post the next part within 24 h of a hit.
- Pin a comment that drives replies ("What number would YOU say?").
- Profile idea (Night Rules era): Kofi's shocked face on purple. The hood channel needs its own avatar (Zara or Milo).

## 9. Pipeline (see `pipeline/`)

| File | Purpose |
|---|---|
| `lib.py` | Mesh helpers, blocky `Char` rig (pose/walk/run/jump/dance/laugh/float/idle + texture faces), dog rig |
| `faces.py` | Generates the painted face textures per skin tone |
| `world.py` | Suburb world, bedroom, Zara-ep cast + shots (set `HOOD=1` to skip suburb houses) |
| `hood.py` | American block: rowhouses, deli, court + mural, bus, hydrants, power lines, skyline |
| `number.py` | IN MY HOOD Ep1: classroom, kitchen, hood cast, crowd instancing/merging, all shots |
| `compose.py` / `ncompose.py` | Frame compositor: sky, grade, FX, bubbles, counter, captions, end card → ffmpeg |
| `audio.py` / `naudio.py` | Score + SFX synced to FX + VO ducking; writes with-music and no-music mixes |
| `split.py` / `hsplit.py` | Split ElevenLabs narration into per-shot lines |
| `night_rules_*.py` | Episode 1 (Cycles stills + Ken Burns) pipeline |

Run order for an ON MY BLOCK episode (same pattern; files `block_timeline.py`, `block.py`, `block_compose.py`, `block_audio.py`, data in `block/`):
```bash
python block_timeline.py && EEVEE=1 python block.py -- all still     # cut VO, preview stills -> block/preview/
EEVEE=1 python block.py -- b17,b01,...,b08 &  EEVEE=1 python block.py -- b09,...,b16 &   # ~2h render
python block_compose.py block/block_noaudio.mp4 && python block_audio.py
```

Run order for an IN MY TOWN episode (`/home/claude/zara`, bpy 4.2 venv, needs `libegl1`):
```bash
python egg_timeline.py                                # cuts egg/vo_full.wav by Whisper word timings (egg/words.json)
EEVEE=1 python egg.py -- all still                    # preview one frame per shot -> egg/preview/
EEVEE=1 python egg.py -- e01,...,e07 &  EEVEE=1 python egg.py -- e08,...,e14 &   # render (~1h40)
python egg_compose.py egg/egg_noaudio.mp4             # composite with hypnotic layers, FX, captions, end card
python egg_audio.py                                   # egg_mix.wav + egg_mix_nomusic.wav
```

Run order for a hood episode:
```bash
python hsplit.py                                     # after voice files are in hel/
HOOD=1 blender-python number.py -- all still         # preview one frame per shot
HOOD=1 blender-python number.py -- all               # render frames (≈80 min)
python ncompose.py out_noaudio.mp4                   # composite (writes default path if argv is dropped)
python naudio.py                                     # audio mixes
ffmpeg -i out_noaudio.mp4 -i hood_mix_nomusic.wav -map 0:v -map 1:a -c:v copy -c:a aac final.mp4
```
Requirements: `bpy` (Python 3.11 venv), Pillow, numpy, librosa, soundfile, kokoro-onnx (reference voice for alignment), ffmpeg.

## 10. Known constraints

- (Nov 2026: ElevenLabs downloads from `elevenlabsusercontent.com` now work in the cloud container.) Earlier note: the cloud workspace can't download from ElevenLabs/ForgeGUI file hosts, so voice files have to be attached manually (or fetched via the desktop app's browser).
- Large crowds: use `crowd_merged()` with the low-poly `POSES_LO` Milos for anything far from the camera.
