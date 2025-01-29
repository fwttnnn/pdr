local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

local remoteEvent = Instance.new("RemoteEvent")
remoteEvent.Name = "RagdollEvent"
remoteEvent.Parent = game:GetService("ReplicatedStorage")

remoteEvent.OnServerEvent:Connect(function(player: Player, __model: Model)
    Ragdoll.toggle(if __model then __model else player.Character)
end)

game:GetService("Players").PlayerAdded:Connect(function(player: Player)
    player.CharacterAdded:Connect(function(character: Model)
        Ragdoll.init(character)
    end)
end)
