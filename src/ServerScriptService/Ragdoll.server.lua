local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

local remoteEvent = Instance.new("RemoteEvent")
remoteEvent.Name = "RagdollEvent"
remoteEvent.Parent = game:GetService("ReplicatedStorage")

remoteEvent.OnServerEvent:Connect(function(player: Player, __model: Model)
    -- NOTE: disable ragdoll
    -- Ragdoll.toggle(if __model then __model else player.Character)
end)

game:GetService("Players").PlayerAdded:Connect(function(player: Player)
    -- NOTE: disable ragdoll
    -- player.CharacterAdded:Connect(function(character: Model)
    --     Ragdoll.init(character)
    -- end)
end)


-- TODO: i'm lazy
local Light = require(game:GetService("ReplicatedStorage").Light)
for i, v in pairs(workspace:GetDescendants()) do
    if v:IsA("Part") and v.Name == "Light" then
        Light.init(v)
        break
    end
end

Light.flickr()
