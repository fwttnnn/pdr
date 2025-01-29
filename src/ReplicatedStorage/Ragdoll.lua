local Ragdoll = { ["Collision"] = {} }

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

    for _, motor6d: Motor6D in ipairs(character:GetDescendants()) do
        if not motor6d:IsA("Motor6D") or not config[motor6d.Name] then continue end

        local ballSocket = Instance.new("BallSocketConstraint")
        ballSocket.Name = "RagdollBallSocket" -- TODO: Name

        -- BallSocket Intensity Configuration
        ballSocket.LimitsEnabled = true
        ballSocket.TwistLimitsEnabled = true
        ballSocket.MaxFrictionTorque = 0
        ballSocket.Restitution = 0
        ballSocket.UpperAngle = 45
        ballSocket.TwistLowerAngle = -45
        ballSocket.TwistUpperAngle = 45

        ballSocket.Attachment0 = Instance.new("Attachment")
        ballSocket.Attachment0.Name = "RagdollBallSocketAttachment"
        ballSocket.Attachment0.CFrame = config[motor6d.Name][1]
        ballSocket.Attachment0.Parent = motor6d.Part0

        ballSocket.Attachment1 = Instance.new("Attachment")
        ballSocket.Attachment1.Name = "RagdollBallSocketAttachment"
        ballSocket.Attachment1.CFrame = config[motor6d.Name][2]
        ballSocket.Attachment1.Parent = motor6d.Part1

        ballSocket.Enabled = false
        ballSocket.Parent = motor6d.Part0
    end
end

function Ragdoll.destroy(character: Character)
    -- TODO: Refactor with filter()
    for _, v in ipairs(character:GetDescendants()) do
        if v:IsA("Motor6D") and Ragdoll.RAGDOLL_DEFAULT_ATTACHMENT_CONFIG[v.Name] then
            Ragdoll.Collision.destroy(v.Part1)
            continue
        end

        if v.Name == "RagdollBallSocket" then
            v.Attachment0:Destroy()
            v.Attachment1:Destroy()
            v:Destroy()
            continue
        end
    end
end

function Ragdoll.Collision.init(part: Part)
    local collision = Instance.new("Part")
    collision.Name = "RagdollCollision"
    -- collision.Transparency = 1
    collision.Size = part.Size / 2
    collision.CFrame = part.CFrame
    collision.Parent = part

    local highlight = Instance.new("Highlight")
    highlight.Name = "RagdollHighlight"
    highlight.Parent = collision

    local weld = Instance.new("WeldConstraint")
    weld.Name = "RagdollWeld"
    weld.Part0 = part
    weld.Part1 = collision
    weld.Parent = part
end

function Ragdoll.Collision.destroy(part: Part)
    part.RagdollCollision.RagdollHighlight:Destroy()
    part.RagdollCollision:Destroy()
    part.RagdollWeld:Destroy()
end

function Ragdoll.enable(character: Model)
    if character:GetAttribute("Ragdoll") == nil then Ragdoll.init(character) end

    character:WaitForChild("Humanoid")
    character.Humanoid.BreakJointsOnDeath = false
    character.Humanoid.RequiresNeck = false
    character.Humanoid.PlatformStand = true

    for _, v in ipairs(character:GetDescendants()) do
        if v.Name == "RagdollBallSocket" then
            v.Enabled = true
            continue
        end

        if v:IsA("Motor6D") and Ragdoll.RAGDOLL_DEFAULT_ATTACHMENT_CONFIG[v.Name] then
            v.Enabled = false
            Ragdoll.Collision.init(v.Part1)
        end
    end

    character:SetAttribute("Ragdoll", true)
end

function Ragdoll.disable(character: Model)
    -- Most likely not gonna happen, but maybe you're dumb enough to call disable() first.
    if character:GetAttribute("Ragdoll") == nil then Ragdoll.init(character) end

    character:WaitForChild("Humanoid")
    character.Humanoid.BreakJointsOnDeath = true
    character.Humanoid.RequiresNeck = true
    character.Humanoid.PlatformStand = false

    for _, v in ipairs(character:GetDescendants()) do
        if v:IsA("Motor6D") and Ragdoll.RAGDOLL_DEFAULT_ATTACHMENT_CONFIG[v.Name] then
            v.Enabled = true
            Ragdoll.Collision.destroy(v.Part1)
        end
    end

    character:SetAttribute("Ragdoll", false)
end

function Ragdoll.toggle(character: Model)
    if character:GetAttribute("Ragdoll") then 
        Ragdoll.disable(character) 
    else 
        Ragdoll.enable(character)
    end
end

return Ragdoll
