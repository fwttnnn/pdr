local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

local remoteEvent = Instance.new("RemoteEvent")
remoteEvent.Name = "RagdollEvent"
remoteEvent.Parent = game:GetService("ReplicatedStorage")

remoteEvent.OnServerEvent:Connect(function(player, __model)
    -- NOTE: for debugging
    if __model then
        Ragdoll:toggle(__model)
        return
    end

    Ragdoll:toggle(player.Character)
end)
