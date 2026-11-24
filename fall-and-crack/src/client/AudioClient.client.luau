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
