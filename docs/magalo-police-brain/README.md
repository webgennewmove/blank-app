# MAGALO Police Brain: design blueprint (v1)

Design only. No game code. Status: for review.

- Published page: https://claude.ai/artifact/F1HT7oXui622SCTAbBMaJe
- `magalo-police-brain.html`: the full blueprint (16 sections, 7 diagrams, 5 scenario simulations)
- `diagrams/A–G.mmd`: Mermaid sources (architecture, officer workflow, witness-to-dispatch, pursuit/LOS, coordinated search, multiplayer cases, arrest/escape/apartment)
- `tools/occupancy_sim.py`: the search-model simulation behind Scenario 2 and the hiding-spot rules
- `tools/id_calc.py`: identification-time and pursuit-timing calculator
- `tools/body.html`, `base.css`, `police.css`, `build.py`: rebuild the page from sources

Companion to `docs/magalo-citizen-brain/`. First build recommendation: milestone P1, then P2.
