local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

local remoteEvent = Instance.new("RemoteEvent")
remoteEvent.Name = "RagdollEvent"
remoteEvent.Parent = game:GetService("ReplicatedStorage")

remoteEvent.OnServerEvent:Connect(function(player, model)
    Ragdoll:toggle(model)
end)
