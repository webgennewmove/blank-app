--!strict
-- Loads AudioCues at server start so the AudioCue RemoteEvent exists before clients look for it.
require(script.Parent:WaitForChild("AudioCues"))
