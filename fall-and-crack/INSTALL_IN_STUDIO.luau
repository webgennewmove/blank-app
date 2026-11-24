-- Fall and Crack audio installer.
-- Paste this whole file into Studio's Command Bar (View -> Command Bar) and press Enter.
-- It creates (or updates) the 4 audio scripts. Safe to run again. Undo with Ctrl+Z.
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local recording = ChangeHistoryService:TryBeginRecording("Install Fall and Crack audio")

local function resolve(path)
	local node = game
	for name in string.gmatch(path, "[^%.]+") do
		node = node:FindFirstChild(name) or game:GetService(name)
	end
	return node
end

local function install(parentPath, folderName, scriptName, className, source)
	local parent = resolve(parentPath)
	local folder = parent:FindFirstChild(folderName)
	if not folder then
		folder = Instance.new("Folder")
		folder.Name = folderName
		folder.Parent = parent
	end
	local existing = folder:FindFirstChild(scriptName)
	if existing and existing.ClassName ~= className then
		existing:Destroy()
		existing = nil
	end
	local s = existing or Instance.new(className)
	s.Name = scriptName
	s.Source = source
	s.Parent = folder
	print("[Audio installer] installed " .. s:GetFullName())
end
install("ReplicatedStorage", "Shared", "AudioConfig", "ModuleScript", [==[
--!strict
-- Every sound ID and audio setting for Fall and Crack lives here.
-- After uploading the mp3s in crack-the-planet-audio/ to Roblox, replace each 0 below
-- with that file's asset ID. A 0 is skipped silently, so the game still runs before then.

local function id(assetId: number): string
	return "rbxassetid://" .. tostring(assetId)
end

local AudioConfig = {}

AudioConfig.Music = {
	Spawn = id(1846088038), -- Morning Mood (APM, licensed for Roblox)
	Shop = id(9045766074), -- The Four Seasons - Spring, piano (APM)
	StarMap = id(1838457617), -- Clair De Lune, solo piano (APM)
	Fall = id(0), -- crack-the-planet-audio/music/fall_theme.mp3
	LowHp = id(0), -- crack-the-planet-audio/music/planet_low_hp_march.mp3
	Shatter = id(0), -- crack-the-planet-audio/music/planet_shatter_fanfare.mp3
}

AudioConfig.Sfx = {
	-- One of these is picked at random on each slam, so hits don't sound identical.
	Slam = {
		id(0), -- sfx/slam_v1.mp3
		id(0), -- sfx/slam_v2.mp3
		id(0), -- sfx/slam_v3.mp3
		id(0), -- sfx/slam_v4.mp3
	},
	Crack = {
		id(0), -- sfx/ground_crack_v1.mp3
		id(0), -- sfx/ground_crack_v2.mp3
	},
	Rumble = id(0), -- sfx/rumble.mp3
	PlanetShatter = id(0), -- sfx/planet_shatter.mp3
	Wind = id(0), -- sfx/wind_loop.mp3
	Perfect = id(0), -- sfx/perfect_sting.mp3
}

-- Volumes (0 to 1)
AudioConfig.MusicVolume = 0.5
AudioConfig.SfxVolume = 1
AudioConfig.WindMaxVolume = 0.8

-- Music behaviour
AudioConfig.MusicFadeSeconds = 1.2
AudioConfig.FallSpeedForMusic = 60 -- studs/s downward before the fall theme starts
AudioConfig.FallMusicHoldSeconds = 3 -- keep the fall theme this long after landing
AudioConfig.ShatterMusicSeconds = 20 -- length of the shatter fanfare

-- Wind gets louder and higher-pitched up to this fall speed (studs/s)
AudioConfig.WindFullSpeed = 250

-- How far away other players' slams can be heard (studs)
AudioConfig.SfxMaxDistance = 600

function AudioConfig.isSet(soundId: string): boolean
	return soundId ~= "" and soundId ~= "rbxassetid://0"
end

return AudioConfig
]==])
install("ServerScriptService", "Audio", "AudioCues", "ModuleScript", [==[
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
]==])
install("ServerScriptService", "Audio", "AudioBootstrap", "Script", [==[
--!strict
-- Loads AudioCues at server start so the AudioCue RemoteEvent exists before clients look for it.
require(script.Parent:WaitForChild("AudioCues"))
]==])
install("StarterPlayer.StarterPlayerScripts", "Audio", "AudioClient", "LocalScript", [==[
--!strict
-- Plays all music and sound effects for the local player.
--
-- Music priority (highest first):
--   Shatter fanfare  -> right after a planet shatters
--   MusicOverride    -> player attribute set by UI: "Shop" or "StarMap" (nil when closed)
--   LowHp march      -> planet below 20% HP (AudioCues.setPlanetLowHp)
--   Fall theme       -> while this player is falling fast
--   Spawn            -> everything else
--
-- The wind loop is driven locally by fall speed, so it costs no network traffic.

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local AudioConfig = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("AudioConfig"))
local audioRemote = ReplicatedStorage:WaitForChild("AudioCue") :: RemoteEvent

local player = Players.LocalPlayer
local random = Random.new()

local function makeGroup(name: string, volume: number): SoundGroup
	local group = Instance.new("SoundGroup")
	group.Name = name
	group.Volume = volume
	group.Parent = SoundService
	return group
end

local musicGroup = makeGroup("Music", AudioConfig.MusicVolume)
local sfxGroup = makeGroup("Sfx", AudioConfig.SfxVolume)

----------------------------------------------------------------------
-- Music
----------------------------------------------------------------------

local tracks: { [string]: Sound } = {}
for name, soundId in AudioConfig.Music do
	local sound = Instance.new("Sound")
	sound.Name = "Music_" .. name
	sound.SoundId = soundId
	sound.Looped = name ~= "Shatter"
	sound.Volume = 0
	sound.SoundGroup = musicGroup
	sound.Parent = SoundService
	tracks[name] = sound
end

local fadeInfo = TweenInfo.new(AudioConfig.MusicFadeSeconds, Enum.EasingStyle.Sine)
local currentTrack: string? = nil

local function playMusic(name: string, restart: boolean?)
	local nextSound = tracks[name]
	if not nextSound then
		return
	end
	if name == currentTrack and not restart then
		return
	end

	local previous = currentTrack
	if previous and previous ~= name then
		local oldSound = tracks[previous]
		local fadeOut = TweenService:Create(oldSound, fadeInfo, { Volume = 0 })
		fadeOut.Completed:Once(function(state)
			-- Only stop it if nobody switched back to this track during the fade.
			if state == Enum.PlaybackState.Completed and currentTrack ~= previous then
				oldSound:Stop()
			end
		end)
		fadeOut:Play()
	end

	currentTrack = name
	if not AudioConfig.isSet(nextSound.SoundId) then
		return
	end
	if restart or not nextSound.IsPlaying then
		nextSound.TimePosition = 0
		nextSound:Play()
	end
	TweenService:Create(nextSound, fadeInfo, { Volume = 1 }):Play()
end

local shatterMusicUntil = 0
local lastFastFallTime = -math.huge

local function chooseMusic(): string
	if os.clock() < shatterMusicUntil then
		return "Shatter"
	end
	local override = player:GetAttribute("MusicOverride")
	if typeof(override) == "string" and tracks[override] then
		return override
	end
	if ReplicatedStorage:GetAttribute("PlanetLowHp") == true then
		return "LowHp"
	end
	if os.clock() - lastFastFallTime < AudioConfig.FallMusicHoldSeconds then
		return "Fall"
	end
	return "Spawn"
end

----------------------------------------------------------------------
-- Wind loop
----------------------------------------------------------------------

local wind = Instance.new("Sound")
wind.Name = "WindLoop"
wind.SoundId = AudioConfig.Sfx.Wind
wind.Looped = true
wind.Volume = 0
wind.SoundGroup = sfxGroup
wind.Parent = SoundService
if AudioConfig.isSet(wind.SoundId) then
	wind:Play()
end

----------------------------------------------------------------------
-- One-shot sound effects
----------------------------------------------------------------------

local function pick(list: { string }): string
	return list[random:NextInteger(1, #list)]
end

-- Plays a sound once. With a position it is 3D (quieter far away); without one it plays flat.
local function playSfx(soundId: string, position: Vector3?, volume: number, speed: number)
	if not AudioConfig.isSet(soundId) then
		return
	end
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = volume
	sound.PlaybackSpeed = speed
	sound.SoundGroup = sfxGroup

	local holder: Instance = sound
	if position then
		sound.RollOffMode = Enum.RollOffMode.InverseTapered
		sound.RollOffMaxDistance = AudioConfig.SfxMaxDistance
		local attachment = Instance.new("Attachment")
		attachment.Parent = workspace.Terrain
		attachment.WorldPosition = position
		sound.Parent = attachment
		holder = attachment
	else
		sound.Parent = SoundService
	end

	sound.Ended:Once(function()
		holder:Destroy()
	end)
	Debris:AddItem(holder, 20) -- safety net if Ended never fires (e.g. failed load)
	sound:Play()
end

local function onSlam(position: Vector3, tier: string, slammer: Player?)
	if tier == "Small" then
		playSfx(pick(AudioConfig.Sfx.Slam), position, 0.6, random:NextNumber(1.2, 1.35))
		return
	end
	playSfx(pick(AudioConfig.Sfx.Slam), position, 1, random:NextNumber(0.95, 1.05))
	playSfx(pick(AudioConfig.Sfx.Crack), position, 0.6, 1)
	if tier == "Perfect" and slammer == player then
		playSfx(AudioConfig.Sfx.Perfect, nil, 1, 1)
	end
end

local function onLayerBreak(position: Vector3)
	playSfx(pick(AudioConfig.Sfx.Crack), position, 1, 0.9)
	playSfx(AudioConfig.Sfx.Rumble, nil, 0.8, 1)
end

local function onShatter(_position: Vector3)
	playSfx(AudioConfig.Sfx.PlanetShatter, nil, 1, 1)
	shatterMusicUntil = os.clock() + AudioConfig.ShatterMusicSeconds
	playMusic("Shatter", true)
end

audioRemote.OnClientEvent:Connect(function(cue: string, position: Vector3, tier: string?, slammer: Player?)
	if cue == "Slam" then
		onSlam(position, tier or "Big", slammer)
	elseif cue == "LayerBreak" then
		onLayerBreak(position)
	elseif cue == "Shatter" then
		onShatter(position)
	end
end)

----------------------------------------------------------------------
-- Per-frame update: fall detection, wind and music choice
----------------------------------------------------------------------

RunService.Heartbeat:Connect(function(dt: number)
	local fallSpeed = 0
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if root and root:IsA("BasePart") then
		fallSpeed = math.max(0, -root.AssemblyLinearVelocity.Y)
	end

	if fallSpeed >= AudioConfig.FallSpeedForMusic then
		lastFastFallTime = os.clock()
	end

	local alpha = math.clamp(fallSpeed / AudioConfig.WindFullSpeed, 0, 1)
	local smoothing = math.min(1, dt * 6)
	wind.Volume += (alpha * AudioConfig.WindMaxVolume - wind.Volume) * smoothing
	wind.PlaybackSpeed = 0.8 + 0.4 * alpha

	playMusic(chooseMusic())
end)
]==])

if recording then
	ChangeHistoryService:FinishRecording(recording, Enum.FinishRecordingOperation.Commit)
end
print("[Audio installer] done. Now upload the mp3s and paste their IDs into ReplicatedStorage.Shared.AudioConfig")
