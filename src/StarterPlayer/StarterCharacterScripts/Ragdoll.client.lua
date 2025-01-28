game:GetService("UserInputService").InputBegan:connect(function(input, e)
    if e then return end

    if input.keyCode == 'f' then
        -- toggle Ragdoll on/off
    end
end)
