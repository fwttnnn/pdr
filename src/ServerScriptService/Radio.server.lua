soundIds = {1848354536, 8551016315, 12222253, 157167203, 358280695, 6832470734, 1841998846, 15689444712}
cursor = 1

sound = Instance.new("Sound")
sound.Name = "Background"
sound.Parent = workspace.Invisible.SFX

sound.SoundId = "rbxassetid://" .. soundIds[cursor]
sound:Play()

sound.Ended:Connect(function(_soundId)
    cursor = (cursor % #soundIds) + 1

    sound.SoundId = "rbxassetid://" .. soundIds[cursor]
    sound:Play()
end)
