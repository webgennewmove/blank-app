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
