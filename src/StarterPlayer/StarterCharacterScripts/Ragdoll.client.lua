local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

game:GetService("UserInputService").InputBegan:connect(function(input, e)
    if e then return end

    if input.keyCode == Enum.KeyCode.F or input.UserInputType == Enum.UserInputType.Touch then
        local RagdollEvent = game:GetService("ReplicatedStorage"):WaitForChild("RagdollEvent")
        RagdollEvent:FireServer()
    end
end)
