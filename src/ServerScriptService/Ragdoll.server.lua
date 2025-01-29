local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

local remoteEvent = Instance.new("RemoteEvent")
remoteEvent.Name = "RagdollEvent"
remoteEvent.Parent = game:GetService("ReplicatedStorage")

remoteEvent.OnServerEvent:Connect(function(player, __model)
    Ragdoll.toggle(if __model then __model else player.Character)
end)
