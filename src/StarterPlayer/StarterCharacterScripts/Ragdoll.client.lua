local Ragdoll = require(game:GetService("ReplicatedStorage").Ragdoll)

game:GetService("UserInputService").InputBegan:connect(function(input, e)
    if e then return end

    if input.keyCode == Enum.KeyCode.F then
        Ragdoll:toggle(script.Parent)
    end
end)
