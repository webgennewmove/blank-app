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
| 3 | **IN MY HOOD Ep1: "Whatever number you say…"** | 1:03 | Current flagship format. See §4. |

## 4. IN MY HOOD: current format

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

- Use audio tags in prompts: `[excited]`, `[whispering]`, `[deadpan]`, `[panicking]`, etc.
- The account is on the **free plan (10k credits/month)**. Free-plan audio isn't licensed for commercial use, so upgrade to Starter before monetising.
- Workflow: generate in ElevenLabs, download, put the MP3s in the project, then `hsplit.py` splits each narration take into per-shot lines (DTW alignment against a Kokoro reference + pause snapping).

## 6. Music

- Background: **TEMPOREX – "Numbers" (instrumental)**, ducked under the voices. It's copyrighted, so **add it inside TikTok** at 15–20% volume rather than baking it in (licensed, and the video appears on the sound's page). Post the `_no_music` render.
- Older episodes use synthesized in-house scores (no licensing issues).

## 7. Visual style rules

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

- The cloud workspace can't download from ElevenLabs/ForgeGUI file hosts, so voice files have to be attached manually (or fetched via the desktop app's browser).
- Large crowds: use `crowd_merged()` with the low-poly `POSES_LO` Milos for anything far from the camera.
