local Light = {}

function Light.init(part: Part)
    Light.part = part

    local light = Instance.new("SpotLight")
    light.Face = 4
    light.Brightness = 40 -- max
    light.Parent = Light.part

    Light.light = light
end

function Light.destroy()
    Light.part = nil
    Light.light:Destroy()
end

function Light.flickr()
    local light = Light.light

    local brightnessPrev = light.brightness
    light.Brightness = 0
    wait(.10)
    light.Brightness = brightnessPrev - 25
    wait(.7)
    light.Brightness = brightnessPrev
    wait(.2)
    light.Brightness = 0
    wait(.2)
    light.Brightness = brightnessPrev
    wait(.2)
    light.Brightness = 0
    wait(2)
    light.Brightness = brightnessPrev

    Light.flickr()
end

return Light
