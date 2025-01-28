local player: Model = script.Parent

player.Humanoid.BreakJointsOnDeath = false
player.Humanoid.RequiresNeck = false
player.Humanoid.PlatformStand = true

local ATTACHMENT_POSITIONS = {
    -- [<Motor6D Name>] = { <Anchor Attachment CFrame>, <Target Attachment CFrame> }
    ["RootJoint"]      = { CFrame.new(0, 0, 0), CFrame.new(0, 0, 0) },
    ["Neck"]           = { CFrame.new(0, 1, 0), CFrame.new(0, -0.5, 0) },
    ["Left Hip"]       = { CFrame.new(-0.5, -1, 0), CFrame.new(0, 1, 0) },
    ["Left Shoulder"]  = { CFrame.new(-1, 1, 0), CFrame.new(-1, 1, 0) },
    ["Right Hip"]      = { CFrame.new(0.5, -1, 0), CFrame.new(0, 1, 0) },
    ["Right Shoulder"] = { CFrame.new(1, 1, 0), CFrame.new(1, 1, 0) },
}

for _, motor6d: Motor6D in ipairs(player:GetDescendants()) do
    if not motor6d:IsA("Motor6D") then continue end
    if not ATTACHMENT_POSITIONS[motor6d.Name] then continue end

    motor6d.Enabled = false

    local attachments = { Instance.new("Attachment"), Instance.new("Attachment") }
    attachments[1].Name = motor6d.Part1.Name .. " BallSocket Attachment"
    attachments[1].CFrame = ATTACHMENT_POSITIONS[motor6d.Name][1]
    attachments[1].Parent = motor6d.Part0

    attachments[2].Name = motor6d.Part0.Name .. " BallSocket Attachment"
    attachments[2].CFrame = ATTACHMENT_POSITIONS[motor6d.Name][2]
    attachments[2].Parent = motor6d.Part1

    local ballSocket = Instance.new("BallSocketConstraint")
    ballSocket.Name = motor6d.Part1.Name .. " BallSocket Constraint"
    ballSocket.Attachment0 = attachments[1]
    ballSocket.Attachment1 = attachments[2]
    
    -- BallSocket Intensity Configuration
    ballSocket.LimitsEnabled = true
    ballSocket.TwistLimitsEnabled = true
    ballSocket.MaxFrictionTorque = 0
    ballSocket.Restitution = 0
    ballSocket.UpperAngle = 45
    ballSocket.TwistLowerAngle = -45
    ballSocket.TwistUpperAngle = 45

    ballSocket.Parent = motor6d.Part0
end
