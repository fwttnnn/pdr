local Ragdoll = {}

Ragdoll.RAGDOLL_DEFAULT_ATTACHMENT_CONFIG = {
    ["RootJoint"] = { CFrame.new(0, 0, 0), CFrame.new(0, 0, 0) },
    ["Neck"] = { CFrame.new(0, 1, 0), CFrame.new(0, -0.5, 0) },
    ["Left Hip"] = { CFrame.new(-0.5, -1, 0), CFrame.new(0, 1, 0) },
    ["Left Shoulder"] = { CFrame.new(-1, 1, 0), CFrame.new(-1, 1, 0) },
    ["Right Hip"] = { CFrame.new(0.5, -1, 0), CFrame.new(0, 1, 0) },
    ["Right Shoulder"] = { CFrame.new(1, 1, 0), CFrame.new(1, 1, 0) }
}

function Ragdoll.init(character: Model, config)
    if not config then config = Ragdoll.RAGDOLL_DEFAULT_ATTACHMENT_CONFIG end

    character:WaitForChild("Humanoid")
    character.Humanoid.BreakJointsOnDeath = false
    character.Humanoid.RequiresNeck = false
    character.Humanoid.PlatformStand = true

    for _, motor6d: Motor6D in ipairs(character:GetDescendants()) do
        if not motor6d:IsA("Motor6D") then continue end
        if not config[motor6d.Name] then continue end

        motor6d.Enabled = false

        local ballSocket = Instance.new("BallSocketConstraint")
        ballSocket.Name = motor6d.Part1.Name .. " BallSocket Constraint"

        -- BallSocket Intensity Configuration
        ballSocket.LimitsEnabled = true
        ballSocket.TwistLimitsEnabled = true
        ballSocket.MaxFrictionTorque = 0
        ballSocket.Restitution = 0
        ballSocket.UpperAngle = 45
        ballSocket.TwistLowerAngle = -45
        ballSocket.TwistUpperAngle = 45

        ballSocket.Attachment0 = Instance.new("Attachment")
        ballSocket.Attachment0.Name = motor6d.Part1.Name .. " BallSocket Attachment"
        ballSocket.Attachment0.CFrame = config[motor6d.Name][1]
        ballSocket.Attachment0.Parent = motor6d.Part0

        ballSocket.Attachment1 = Instance.new("Attachment")
        ballSocket.Attachment1.Name = motor6d.Part0.Name .. " BallSocket Attachment"
        ballSocket.Attachment1.CFrame = config[motor6d.Name][2]
        ballSocket.Attachment1.Parent = motor6d.Part1

        ballSocket.Parent = motor6d.Part0

        local collision = Instance.new("Part")
        collision.Name = "RagdollCollision"
        -- collision.Transparency = 1
        collision.Size = motor6d.Part1.Size / 2
        collision.CFrame = motor6d.Part1.CFrame
        collision.Parent = motor6d.Part1

        local highlight = Instance.new("Highlight")
        highlight.Parent = collision

        local weld = Instance.new("WeldConstraint")
        weld.Part0 = motor6d.Part1
        weld.Part1 = collision
        weld.Parent = motor6d.Part1

    end
end

function Ragdoll:enable(character: Model)
    if character:GetAttribute("Ragdoll") == nil then Ragdoll.init(character) end

    -- TODO
    character:SetAttribute("Ragdoll", true)
end

function Ragdoll:disable(character: Model)
    -- Most likely not gonna happen, but maybe you're dumb enough to call disable() first.
    if character:GetAttribute("Ragdoll") == nil then Ragdoll.init(character) end

    -- TODO
    character:SetAttribute("Ragdoll", false)
end

function Ragdoll:toggle(character: Model)
    if character:GetAttribute("Ragdoll") then 
        Ragdoll:disable(character) 
    else 
        Ragdoll:enable(character)
    end
end

return Ragdoll
