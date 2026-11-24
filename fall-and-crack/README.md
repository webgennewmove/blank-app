# Fall and Crack: audio system

Drop-in music and sound effects for Fall and Crack. The audio files are in `../crack-the-planet-audio/`.

## What plays when

| Moment | Sound | Triggered by |
|---|---|---|
| Standing around / spawn | Morning Mood | automatic |
| Shop open | Four Seasons: Spring | UI sets `player:SetAttribute("MusicOverride", "Shop")` |
| Star Map open | Clair De Lune | UI sets `MusicOverride` to `"StarMap"` |
| Falling fast | `fall_theme` + wind loop that gets louder with speed | automatic (client reads fall speed) |
| Landing | random slam boom (+ crack on big hits, + PERFECT sting for the slammer) | `AudioCues.slam(...)` |
| Layer breaks | crack + rumble | `AudioCues.layerBreak(...)` |
| Planet under 20% HP | `planet_low_hp_march` | `AudioCues.setPlanetLowHp(true)` |
| Planet shatters | `planet_shatter` boom + `planet_shatter_fanfare` | `AudioCues.planetShatter(...)` |

Music crossfades between these automatically. Priority: shatter > shop/Star Map > low HP > falling > spawn.
When the UI closes, set `MusicOverride` back to `nil`.

## Install

**With Rojo:** run `rojo serve` in this folder and connect from Studio.

**Without Rojo:** in Studio, create these and paste in each file's contents:

| Studio location | Type | File |
|---|---|---|
| ReplicatedStorage → Folder `Shared` → `AudioConfig` | ModuleScript | `src/shared/AudioConfig.luau` |
| ServerScriptService → Folder `Audio` → `AudioCues` | ModuleScript | `src/server/AudioCues.luau` |
| ServerScriptService → Folder `Audio` → `AudioBootstrap` | Script | `src/server/AudioBootstrap.server.luau` |
| StarterPlayer → StarterPlayerScripts → `AudioClient` | LocalScript | `src/client/AudioClient.client.luau` |

## Upload the sounds

1. In Studio open **Asset Manager → Bulk Import** (or create.roblox.com → Creations → Audio) and upload every mp3 in `crack-the-planet-audio/music` and `crack-the-planet-audio/sfx`.
2. Copy each asset ID into `AudioConfig.luau`, replacing the `0` next to that file's name.

Any ID still set to `0` is silently skipped, so the game runs fine before uploading.

## Hook it into gameplay (server scripts only)

```lua
local AudioCues = require(game.ServerScriptService.Audio.AudioCues)

-- when the server confirms a landing
local tier = if isPerfect then "Perfect" elseif damage >= BIG_HIT_DAMAGE then "Big" else "Small"
AudioCues.slam(player, landingPosition, tier)

-- when a layer caves in
AudioCues.layerBreak(craterPosition)

-- when planet HP crosses 20%
AudioCues.setPlanetLowHp(planetHp / planetMaxHp < 0.2)

-- when the planet shatters
AudioCues.planetShatter(planetCenter)
```

Clients can't trigger any of these: the server only sends to clients and never listens.

## Tuning

Change volumes, fade time, fall-speed threshold and how far slams can be heard at the bottom of `AudioConfig.luau`.
