local player = game.Players.LocalPlayer
local camera = game.workspace.CurrentCamera
local part = game.workspace.Invisible.Camera

camera.CameraType = Enum.CameraType.Scriptable
camera.CFrame = CFrame.lookAt(part.CFrame.Position, player.Character.HumanoidRootPart.CFrame.Position)
