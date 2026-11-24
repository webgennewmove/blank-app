--!strict
-- Server-side audio API. Gameplay scripts call these functions; every client then plays
-- the right sounds and music. Nothing here listens to clients, so exploiters can't trigger it.
--
--   local AudioCues = require(game.ServerScriptService.Audio.AudioCues)
--   AudioCues.slam(player, landingPosition, "Big")
--   AudioCues.layerBreak(position)
--   AudioCues.setPlanetLowHp(true)
--   AudioCues.planetShatter(planetCenter)

local ReplicatedStorage = game:GetService("ReplicatedStorage")

export type SlamTier = "Small" | "Big" | "Perfect"

local REMOTE_NAME = "AudioCue"

local remote = ReplicatedStorage:FindFirstChild(REMOTE_NAME) :: RemoteEvent?
if not remote then
	local created = Instance.new("RemoteEvent")
	created.Name = REMOTE_NAME
	created.Parent = ReplicatedStorage
	remote = created
end
local audioRemote = remote :: RemoteEvent

local AudioCues = {}

-- A player landed. Tier: "Small" for weak hits, "Big" for strong ones, "Perfect" for a PERFECT slam.
function AudioCues.slam(player: Player, position: Vector3, tier: SlamTier)
	audioRemote:FireAllClients("Slam", position, tier, player)
end

-- A planet layer broke and the ground caved in.
function AudioCues.layerBreak(position: Vector3)
	audioRemote:FireAllClients("LayerBreak", position)
end

-- Switch the war-drum march on when planet HP drops below 20%, off when it re-forms.
-- Stored as an attribute so players who join mid-fight hear it too.
function AudioCues.setPlanetLowHp(isLow: boolean)
	ReplicatedStorage:SetAttribute("PlanetLowHp", isLow)
end

-- The planet shattered: explosion plus victory fanfare for everyone.
function AudioCues.planetShatter(position: Vector3)
	AudioCues.setPlanetLowHp(false)
	audioRemote:FireAllClients("Shatter", position)
end

return AudioCues
