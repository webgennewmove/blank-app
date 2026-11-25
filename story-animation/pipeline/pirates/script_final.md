# PIRATES (Angle A): "I'm The Captain Now (For 3 Seconds) 🎩": FINAL v2

- **Runtime:** ~75.4 s when read fast.
- **Narration:** 1,295 characters including tags (204 words).
- **Shots:** 51 (ids kept from v1).
- **Narrator:** Toby (brief voice `1BempFyI57oP6ldXrZtr`).
- **Hashtags:** `#pirates #roblox`. Do not mark it Made for Kids.

## 1. NARRATION (single continuous VO, Toby)

[excited] On my pirate crew there's ONE rule: whoever wears the captain's hat… IS the captain. [beat] Whoever.
[deadpan] Today that was a seagull. We gave him all our fries. Tough boss.
[excited] We got the hat back and chased a cargo ship!
Dale fired the RPG… [deadpan] Dale has never hit anything. Including the ocean.
Kevin's rope was too short. [beat] Thanks, Kevin.
We climbed aboard… standoff. Ten guns. Ten guys. ZERO plan.
Then Kevin sneezed. A shot knocked the hat onto THEIR captain. He said, "Everybody overboard."
[deadpan] So we jumped. Rules are rules.
Kevin sneezed AGAIN. Now the COOK's the captain. "LUNCH BREAK!" [beat] Same rule on their ship.
Standoff… with sandwiches.
[deadpan] KEVIN. Now the CRANE's captain. [beat] Best captain so far.
Then the wind took it! Our boat, their lifeboat, and the WHOLE cargo ship… chasing one hat!
A dolphin was captain for two seconds. Great leader.
Dale lined up the shot of his life… [panicked] Dale, NO—
KA-BOOOOM! [beat] Dale hit something.
The whole container wall went into the sea… and the wave surfed everybody onto the deck!
The hat floated down… onto ME.
[deadpan] Look at me. I'm the captain now.
First order: "Everyone… stop shooting."
[beat] … It worked.
[excited] Then a gust took the hat… [deadpan] …and he's the captain now.

*(The loop works like this: p51 has the same smug seagull landing on the bow wearing the hat, in the same framing as p01. The VO restarts on "On my pirate crew…".)*

## 2. CAST (generic pirate kit only: no real-world flags, names or group coding; skin tones mixed from the `TFOLK` palette)

**Standoff head-count:** our crew of 6 (Bev, Toby, Dale, Kevin + 2 extras) plus a cargo crew of 4 = **10 guns, 10 guys**.

| Character | Look (colours + silhouette) |
|---|---|
| **The Captain's Hat** (hero prop) | Oversized black bicorne with gold trim and a tall red feather. It is always the biggest, most readable shape in frame. |
| **Captain Bev** | Long crimson coat with gold buttons, grey bob, one wooden peg leg. Her silhouette is the wide coat flare, and with the hat she is the tallest of our crew. |
| **Toby** (narrator) | Lanky, in a teal-and-white striped shirt, brown vest and yellow bandana with long knot tails. Thin silhouette, huge grin. |
| **Dale** (RPG guy who never hits) | Stocky, in an olive cargo vest and orange bandana, with big goggles pushed up on his forehead. A chunky toy-proportioned green RPG always rides on his shoulder. |
| **Kevin** (short rope, sneezer) | Short and round, in a purple striped shirt and eye patch with a tiny tricorn and a red nose. Smallest head-height in the crew. His chunky toy rifle jerks skyward whenever he sneezes. |
| **Our extra crew** (×2) | Generic striped shirts in red and blue with bandanas. |
| **The Cook** (cargo ship) | Chubby, in a white apron and tall chef's toque, holding a ladle. The toque is a tall white column, so the captain's hat stacks on top of it. |
| **Giant Cargo Captain** | `Char(scale=2.6)`. White merchant uniform with navy epaulettes, white peaked cap, mirrored shades and a juice box. Broad, still and completely unbothered. |
| **Cargo Crew** (×4) | Matching orange hi-vis coveralls and white hard hats, carrying chunky toy rifles. They read instantly as "the other team". |
| **Seagull** (one recurring bird) | Blocky white and grey gull with a yellow beak and smug half-lidded eyes. The same gull appears in p01, p04–p07, p30 and p51. The hat is comically huge on it. |
| **Dolphin** | Blocky blue-grey dolphin with a wide permanent grin. |
| **Skiff flag** | A plain black pennant with a white cartoon hat icon. No national flag and no Jolly Roger variant. |

## 3. SHOT LIST

Sets: **sea** = open ocean / sea level. **skiff** = on board our skiff. **hull** = cargo ship's side. **deck** = cargo deck. **bridge** = bridge wing.

**Counter:** CAPTAINS TODAY (`counter()` style), top-left. It sits **below the top 12% of the frame** (top edge at about 14% height) so it clears the platform UI. It appears in p01 and ticks on every new head: gull 1, Bev 2, Giant 3, Cook 4, Crane 5, Dolphin 6, Toby 7, gull 8.

**Kevin's sneeze (p19, p24, p28):** Kevin's head snaps forward, an "ACHOO!" slam pops, and his rifle jerks straight up so the muzzle flash points at the sky. PING is SFX only, with no PING slam.

| id | sec | VO covered | set | characters + action | camera | on-screen FX | SFX |
|---|---|---|---|---|---|---|---|
| p01 | 0.0–1.6 | "On my pirate crew there's ONE rule:" | skiff | The smug seagull perched on the bow wearing the captain's hat, slow smug blink. Sky behind it | Tight CU, slow push-in | Slam "🎩 = CAPTAIN" from frame 1; counter pops "CAPTAINS TODAY: 1" | Gull "kyaa", waves |
| p02 | 1.6–3.6 | "whoever wears the captain's hat… IS the captain." | skiff | Bev, Toby, Dale, Kevin and 2 crew snap to attention and salute the gull in unison | MS low angle from gull POV, drift right | Slam "IS THE CAPTAIN" | Salute snaps fwip-fwip-fwip |
| p03 | 3.6–5.2 | "[beat] Whoever." | skiff | Hatless Bev holds the salute, deadpan, eyes sliding to the gull | CU, slow push | – | Wave lap |
| p04 | 5.2–6.8 | "Today that was a seagull." | skiff | Gull squawks an order and points a wing at the fry basket | MCU, snap zoom | 🍟 pops | SQUAWK |
| p05 | 6.8–8.2 | "We gave him all our fries." | skiff | Kevin, sad-faced, tips a whole basket of fries in front of the gull, which gulps them | MS, slight tilt down | – | Fry rustle, GULP |
| p06 | 8.2–9.4 | "Tough boss." | skiff | Toby to lens with a deadpan thumbs-up while the gull gulps behind him | MCU, handheld drift | – | Gulp |
| p07 | 9.4–11.0 | "We got the hat back" | skiff | Bev snatches the hat and slaps it on. The gull flaps off, offended | MS, whip to follow hat | Counter → 2 | Whump, angry squawk |
| p08 | 11.0–12.6 | "and chased a cargo ship!" | sea | Skiff at full speed with a big wake, aimed at a red hull corner. **Bow only: top and length out of frame** | Low tracking alongside the skiff | Speed lines | Outboard ROAR |
| p09 | 12.6–14.0 | "Dale fired the RPG…" | skiff | Dale shoulders the RPG, squints, FWOOSH, and the rocket goes straight UP | CU Dale, tilt up with the rocket | Muzzle flash, smoke trail | FWOOSH |
| p10 | 14.0–15.6 | "Dale has never hit anything." | skiff | The whole crew tilts their heads up at a tiny dot in the sky. Dale shrugs | WS from deck level, looking up | – | Fading whistle |
| p11 | 15.6–17.0 | "Including the ocean." | sea | The rocket vanishes into a cloud with a twinkle | Wide sky, slight drift | ✨ twinkle | Distant "ting" |
| p12 | 17.0–18.0 | "Kevin's rope" | hull | Two grappling hooks arc up and bite the rail, and the ropes snap taut | CU on the rail | Slam "CLANK!" ×2 | CLANK, CLANK |
| p13 | 18.0–19.2 | "was too short." | hull | Crew climb the ropes up the red hull. Kevin's rope ends 2 m below the rail | Low angle up the hull, top cropped | – | Rope creak, grunts |
| p14 | 19.2–20.2 | "[beat]" | hull | Kevin dangles at the end of the short rope, legs kicking above the waves | MS, gentle sway with him | – | Creak, Kevin "uh…" |
| p15 | 20.2–21.4 | "Thanks, Kevin." | hull | Crew climb over Kevin, boot on his head then boot on his shoulder; his face squished | MCU | 👍 pops | Boing, boop |
| p16 | 21.4–23.0 | "We climbed aboard… standoff." | deck | Our 6 pop over the rail. The **4 cargo crew** spin round and everyone raises rifles | MS, fast push-in | – | 10 rifle cocks |
| p17 | 23.0–24.6 | "Ten guns. Ten guys." | deck | Ring of **10 (6 ours + 4 cargo)** all aiming at each other. Two are accidentally aiming at their own teammates | Slow 180° orbit (`cpath`) | – | Tense drone |
| p18 | 24.6–25.8 | "ZERO plan." | deck | Kevin and a cargo crewman aim at each other, then both shrug | CU two-shot | Slam "ZERO PLAN" | Record scratch |
| p19 | 25.8–27.2 | "Then Kevin sneezed." | deck | **Sneeze #1:** Kevin's head snaps, his rifle jerks straight up and the flash points at the sky. Behind him, the hat spins off Bev's head | MCU Kevin, Bev soft in the background | Slam "ACHOO!" | ACHOO, PING |
| p20 | 27.2–29.0 | "A shot knocked the hat onto THEIR captain." | deck → bridge | The hat arcs over the deck and lands on the Giant's white cap. He looks down through his shades | Whip-tracking the hat; frame the Giant chest-up, bridge wing behind | Counter → 3 | Whoosh, soft plop |
| p21 | 29.0–30.6 | "He said, 'Everybody overboard.'" | bridge | The Giant sips his juice box and lazily points at the sea | Low angle, slow push | – | Juice-box slurp |
| p22 | 30.6–31.8 | "So we jumped." | deck | Our crew salutes, then all vault the rail in sync | MS side-on | – | "HUP!" |
| p23 | 31.8–33.2 | "Rules are rules." | sea | Six ragdolls tumble into the water in a row of splashes | High angle straight down the hull | Slam "SPLASH!" (on-screen only) | Splash ×6 |
| p24 | 33.2–34.6 | "Kevin sneezed AGAIN." | deck | The soaked crew climbs back over the rail and Kevin spits out a small fish. **At the end, sneeze #2:** head snaps, rifle jerks up, flash at the sky | MS, punch-in on the sneeze | Slam "ACHOO!" | Drips, fish flop, ACHOO, PING |
| p25 | 34.6–35.6 | "Now the COOK's" | bridge | The hat pops off the Giant's cap. He doesn't react | CU | – | Whoosh |
| p26 | 35.6–38.0 | "the captain. 'LUNCH BREAK!' [beat] Same rule on their ship." | deck (galley door) | The hat lands on top of the Cook's toque and he raises his ladle proudly. **In the background the 4 cargo crew snap to attention and salute him** | MCU, slight pull-back to reveal the saluting crew | Counter → 4, 🥪 pops | Dinner-bell CLANG |
| p27 | 38.0–39.8 | "Standoff… with sandwiches." | deck | The ring again: rifle in one hand, sandwich in the other, everyone chewing intensely | Slow orbit (matches p17) | – | Munching |
| p28 | 39.8–40.8 | "KEVIN." | deck | **Sneeze #3:** Kevin, mid-sandwich, head snaps, rifle jerks up, flash at the sky. The hat flips off the Cook's toque behind him and the Cook's face drops | MCU Kevin, Cook in the background | Slam "ACHOO!" | ACHOO, PING |
| p29 | 40.8–42.0 | "Now the CRANE's captain." | deck | The hat lands on the swinging crane hook | Low angle, sway with the hook | Counter → 5 | Chain creak |
| p30 | 42.0–43.6 | "[beat] Best captain so far." | deck | Both crews salute the dangling hook. Nothing happens. **The same smug gull from p01** lands on the hook beside the hat and gives its smug blink | WS, then a slight push toward the gull | – | Creak, gull "kyaa" |
| p31 | 43.6–45.0 | "Then the wind took it!" | deck | A gust lifts the hat off the hook and sails it over the rail | Track with the hat | – | Wind WHOOSH |
| p32 | 45.0–46.2 | "Our boat," | sea | Our soggy crew back in the skiff, racing | Low tracking | Speed lines | Outboard roar |
| p33 | 46.2–47.4 | "their lifeboat," | sea | Orange lifeboat packed with the 4 hard hats, racing | Low tracking, other side | – | Motor whine |
| p34 | 47.4–49.2 | "and the WHOLE cargo ship… chasing one hat!" | sea | The hat bobs on a wave in the foreground. Skiff and lifeboat flank it, and the cargo bow looms behind, **cropped: no full ship**. **Fire-hose jets** from the bow arc water all around the hat | Sea-level cam bobbing with the hat | 🎩 pops | Hose HISS, water slaps |
| p35 | 49.2–50.8 | "A dolphin was captain for two seconds." | sea | A dolphin leaps and the hat lands on its head mid-arc | Slow-mo side tracking | Counter → 6 | Dolphin chirp |
| p36 | 50.8–52.0 | "Great leader." | sea | Every boat salutes the dolphin, which nods gravely | MS | – | Chirp |
| p37 | 52.0–53.6 | "Dale lined up the shot of his life…" | skiff | Dale shoulders the RPG, one eye shut, tongue out | CU, slow push | **Reticle drifts over sky, sea and the floating hat only**; it never lands on a person or the dolphin | Heartbeat |
| p38 | 53.6–54.6 | "Dale, NO—" | skiff | Toby lunges at Dale, panicked. FWOOSH | MCU, whip-pan with the rocket | Muzzle flash | FWOOSH |
| p39 | 54.6–55.8 | "KA-BOOOOM!" | sea → deck | The rocket skims past the lifeboat and slams into the base of the tallest container stack. **CU on the base only.** The blast wave **flips the hat off the dolphin** in the foreground, spinning it up (the dolphin dives, fine) | Whip-follow, hard stop | White flash, shake, slam "KA-BOOM!" | KA-BOOOOM |
| p40 | 55.8–57.2 | "[beat] Dale hit something." | skiff | Dale lowers the smoking RPG, stunned then proud | MCU | Smoke curl | Ringing silence |
| p41 | 57.2–59.0 | "The whole container wall" | sea | **First full reveal (76% of runtime):** the entire mega cargo ship, with its towering container wall starting to lean | Extreme wide crane pull-back | Sunburst | Deep metal groan |
| p42 | 59.0–60.6 | "went into the sea…" | sea | Containers domino into the ocean in a chain of giant splashes. **The hat spins skyward up through the splash curtain** | Wide side-on, tilt up with the hat | Droplet lens hits | Thunder of splashes |
| p43 | 60.6–62.0 | "and the wave" | sea | A giant swell lifts the skiff AND the lifeboat side by side. Both crews scream with delight | Low tracking from behind both boats | – | Rushing water |
| p44 | 62.0–64.2 | "surfed everybody onto the deck!" | deck | **Both the skiff and the lifeboat** surf over the rail and skid to a stop at `DECK_Z`. Both crews tumble out **still aiming at each other**. Kevin is once again **dangling from his short rope** off the rail, legs kicking | Wide, then follow; end on Kevin dangling at the edge | 🏄 pops | Scrape, double THUD, rope creak |
| p45 | 64.2–65.8 | "The hat floated down…" | deck | The hat drifts down from the sky in a slow spin | Slow-mo tilt down | Soft glow | Light choir "aaah" |
| p46 | 65.8–67.2 | "onto ME." | deck | It lands on Toby's head. He looks up at the brim | MCU | Counter → 7 | Soft plop |
| p47 | 67.2–69.4 | "Look at me. I'm the captain now." | deck | Toby stares deadpan into the lens | Slow push-in to CU | – (let it breathe) | Wind, music drop |
| p48 | 69.4–71.0 | "First order: 'Everyone… stop shooting.'" | deck | Wide on all **10 (6 ours + 4 cargo)**, still aiming at each other. Kevin has just hauled himself back over the rail, dripping | WS, slow drift | – | Tense drone |
| p49 | 71.0–72.2 | "[beat] … It worked." | deck | Every gun lowers at once. The Cook starts handing out sandwiches | MS | – | Clunk of guns lowering |
| p50 | 72.2–73.8 | "Then a gust took the hat…" | deck | A gust lifts the hat off Toby, who grabs at air | CU | – | WHOOSH |
| p51 | 73.8–75.4 | "…and he's the captain now." | skiff (on deck) | The same smug seagull snatches the hat mid-air, lands on the skiff's bow and puffs up. Everyone salutes. **Same framing as p01** (tight, sky behind) → loop | Tight CU, slow push-in (matches p01) | Counter → 8 | Gull "kyaa" |

## 4. RULE CHECKS

- **No clipping:**
  - Everything that floats uses `sea_z`. All deck characters, and both boats after p44, stand at `DECK_Z`.
  - The hat has a fixed head-top offset for each wearer (scale 1, 2.6, toque top, crane hook, dolphin, gull).
  - Ropes are one keyed `rod` from hook to hand.
  - Boots on Kevin in p15 touch his surface and never go through it.
  - The support hand on each rifle is checked against the barrel, including on the sneeze jerks.
- **Never 5 s static:** every shot is 1.0–2.4 s, and sea bob, `hold()` breathing and a camera move run in all of them.
- **Late spectacle:** before p39 the ship is only ever shown as the bow or a hull section. The impact (p39) comes at 72% and the full reveal and container collapse (p41–p44) at 76–85%.
- **Loop / no outro:** there's no follow outro. The last line, "…and he's the captain now", plays over p51's gull CU, which matches p01's framing and cuts straight into "On my pirate crew…".
- **Action without gore:**
  - Guns are chunky and toy-proportioned.
  - Kevin's sneeze shots point at the sky.
  - Stray shots only hit the hat; the hoses only hit the water; the RPG hits only containers.
  - Dale's reticle never rests on a person or the dolphin.
  - People are only knocked into the sea, with splashes and no injuries. No blood, no wounds, no hostages.
