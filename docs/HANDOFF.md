# MAGALO AI design: session handoff

A condensed record of the whole conversation, written so a new session (or a person) can pick up without the original chat. Nothing here is code. No project source was ever available.

- Written: 26 October 2026
- Branch: `claude/magalo-citizen-brain-design-gs423g` in `webgennewmove/blank-app`
- Repository visibility: public. This file contains no credentials, personal data or private code.

## Where things are

| What | Where |
| --- | --- |
| Citizen Brain design (published page) | https://claude.ai/artifact/PDHVobzKHx9X9JGGiHE6iK |
| Police Brain blueprint (published page) | https://claude.ai/artifact/F1HT7oXui622SCTAbBMaJe |
| Citizen Brain files (page, 5 diagrams, scoring calculators) | `docs/magalo-citizen-brain/` |
| Police Brain files (page, 7 diagrams, search simulation, timing calculator) | `docs/magalo-police-brain/` |

Both published pages are private to the account that created them. Each docs folder has a README and a `tools/build.py` that rebuilds its HTML page from the sources.

## Standing facts

- **MAGALO's code has never been available.** `webgennewmove/blank-app` is an unrelated blank Streamlit template, and `webgennewmove/OmniRoute` is an unrelated fork. Both designs treat the theft, heat, XP, arrest, confiscation and apartment systems as black boxes behind adapters.
- **Nothing was implemented.** Both tasks were design and planning only, and approval was requested before any development.
- **All numbers are playtest hypotheses.** Utility scores come from the calculators in each `tools/` folder. Performance figures are budgets to verify in MicroProfiler, not measurements.

## Timeline

### 1. Citizen Brain (25 October)

**Request.** Design a convincing but cheap civilian AI for a multiplayer Roblox crime game. Civilians must never recognize a player from a previous robbery: no names, UserIds, outfits, faces, reputation or cross-session memory. A civilian may track a visible threat only during an active incident and must discard it afterwards, without breaking police pursuit or the wanted system.

**What I did.** Inspected the repo (blank template), searched for the wider repos, researched Roblox pathfinding, NPC performance guidance and CrimeLogic V2, then built a utility model in a scratch calculator so every quoted score comes from one set of formulas.

**Result (published page).**
- Architecture: a five-mode state machine (Ambient, Alert, Panic, Victim, Recover), with utility scoring of 4-8 actions inside each mode, trip-based goals (door, stops at points of interest, exit), bounded memory and event-driven reactions.
- Skipped on purpose: GOAP/HTN planners, behavior trees, needs simulation, crowd algorithms, language models, persistence.
- Perception: awareness builds over time from distance, angle, motion and activity. Hearing is event-driven with personal reaction delays.
- Three example citizens differing only in trait numbers: Priya (commuter), Des (market trader), Edith (pensioner). Six situations were simulated for each.
- No-recognition enforcement: an identity firewall, one-off track handles that die 6.8-8.8 s after sight is lost, incident notes that hold a place and a heading but no character reference, hard deletion points, no persistence, and a recognition-probe test.
- Performance: one Heartbeat scheduler, Hot/Warm/Cold tiers, server-owned Humanoids, client-side animation, bounded memory, cleanup bags.
- Roadmap: milestones M1-M7. The minimum viable brain is M1-M4.

**Integration contracts defined.** Theft hook in, stimulus hook in, a wanted adapter out (last-seen spot, heading, age, no identity), and attributes on each civilian model.

### 2. Repository and saving the work

- The user asked which repository the work should live in. I recommended a new dedicated repo, `webgennewmove/magalo`, for the real Roblox project (ideally a Rojo project).
- Creating it failed (403: the Claude GitHub App cannot create repositories). The user was asked to create it by hand. They then said they couldn't share code yet and asked me to save the work.
- I committed the Citizen Brain files to this branch. The first pushes failed with 403 (no GitHub access to `blank-app`). After the user granted access, the push succeeded.

### 3. Police Brain (26 October)

**Request.** Design the AI police system: dispatch, perception, pursuit, search, escalation, arrest, multiplayer, apartment safety, future vehicle pursuit. It must feel intelligent and fair, with no omniscience, no unfair spawns and no combat. Required: at least seven diagrams, five simulated scenarios and a phased roadmap. Do not ask for or inspect code.

**What I did.** Verified CrimeLogic claims against its game pages, researched game-AI precedents (occupancy-map search, last-known-position mechanics, witness reporting, GTA-style line-of-sight evasion), and ran two scratch simulations: an alley search model and an identification-timing calculator. One search-model bug was found and fixed while simulating (see below).

**Benchmark, verified vs not.**
- Verified from CrimeLogic pages: an AI police force ("AIPD"), AI cops dispatched when you become wanted, multiplayer support, tire popping, dodging PIT maneuvers in V2.
- Reported but not verified (a community wiki could not be fetched): star wanted levels, SWAT at 4+ stars, an update that made cops easier for new players.
- Unknown: how CrimeLogic's police perceive, search, or use witnesses. Nothing in the design assumes it.

**Result (published page).**
- Three layers: a central dispatcher (cases, escalation, unit allocation), a squad per case (shared belief, roles, search plan) and an officer brain (a 7-state machine with local utility).
- Knowledge ladder: Confirmed, Occluded, Last seen, Reported, Lost. Officers identify only a briefed suspect, at a rate set by witness description quality, distance and behavior. Radio has a 0.75-1.5 s delay.
- Search: an occupancy map over a street graph, cleared where officers can see, with hiding spots opened only on probability or noise evidence. A search ends on a minimum quiet time plus low probability, or a hard maximum. A getaway is paid only for the "Evaded" outcome, once per case id.
- Fairness: officer sprint 0.92 of player sprint with limited stamina, telegraphed arrests with a break-free window, reinforcements only from the station or map edge with a spawn audit, and heat never reveals position.
- Escalation levels L0-L4, with L5 reserved for future vehicles. Heat, case level, pursuit, search, arrest and escape are six separate concepts.
- Apartment gate: server-only `CanEnter` and `CanRevealPhones` checks with reason codes, no side effects, and a rule that simultaneous door and arrest events cannot both succeed.
- Multiplayer: one case per suspect, clusters that share officers but never outcomes, assist rules, disconnects handled as "Abandoned".
- Vehicles: a later add-on (RoadNet, driver brain, pure-pursuit controller), not a dependency of the foot system.
- Roadmap: P1-P7. First playable is P1, then P2.

**Search-model bug found by simulation.** The first model concentrated probability on the bin nearest where the suspect vanished, which made officers look there first. The fix was to move probability away from the last known position, with a heading bias. The resulting rule: hiding works when police cannot rule out that you ran on.

### 4. This handoff

The user asked to "transfer this whole chat". A live session cannot be moved, so I asked what form they wanted and they chose a handoff document in the repo (this file).

## Decisions still open

**Citizen Brain**
1. Approve the architecture (modes + utility + trips, with no planners, behavior trees or language models).
2. Approve the 7-9 s window after which a witness's live track on a suspect is deleted, even mid-incident.
3. Should civilian awareness, or a civilian putting their phone away, make theft harder? Default: no, it stays cosmetic.
4. Should civilian reports replace, add to, or only guide the existing wanted triggers? Default: add to them through an adapter.
5. Is a short, contact-free victim chase acceptable? Default: up to 6 s or 25 studs.
6. May invisible pedestrian-graph and point-of-interest markers be added to the map?

**Police Brain**
1. Approve the three-layer architecture and phasing.
2. Should getaway XP require that police actually saw the player (Evaded), not just that a report went unanswered (Unsolved)?
3. Should a reported theft that no officer was free to answer (L0) block apartment entry? Recommended: no.
4. Should a player who disconnects mid-chase have that case's phones confiscated on the next join?
5. Should the wanted player see a last-known-position marker and dispatch summaries? Recommended: yes.
6. What is the player's sprint speed? The designs assume 24 studs/s and express officer numbers relative to it.

## How to resume

1. Put MAGALO's scripts in a repository the session can reach (a Rojo project is ideal). At minimum the theft, police and wanted modules are needed so the adapters fit the real APIs. A new repo such as `webgennewmove/magalo` was recommended, but it must be created by hand because the Claude app cannot create repositories.
2. Make sure the Claude GitHub App has access to it: https://github.com/apps/claude/installations/select_target
3. Answer the open decisions above.
4. Start with the Citizen Brain M1 (purposeful pedestrians) and the Police Brain P1 (one officer who thinks), then P2. The pedestrian graph and map markers are shared groundwork for both.
5. Treat every tuning number as a starting hypothesis, and keep the debug overlays and seeded scenario harness from the milestones, since tuning depends on them.

## Caveats worth remembering

- The published pages and these files were checked in Chromium at desktop and phone widths and render all diagrams in two Mermaid versions, but nothing was tested in Roblox Studio because no game code exists.
- Roblox facts used (client-side NPC animation, disabling unused Humanoid states, pathfinding limits, the newer `ExcludeInstances`/`IncludeInstances` filters, network ownership) came from Roblox's documentation and developer forum, and should be re-checked against current docs when implementing.
- The `SupportPartialPath` pathfinding option appears to belong to a community module, not the engine, so the designs do not rely on it.
