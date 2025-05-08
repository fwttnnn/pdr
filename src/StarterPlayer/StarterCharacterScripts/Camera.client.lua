local character: Character = script.Parent
local camera: Camera = game.workspace.CurrentCamera

camera.CameraType = Enum.CameraType.Scriptable
camera.FieldOfView = 50

function cameraLookAt(from: Position, to: Position)
    camera.CFrame = CFrame.lookAt(from, to)
end

character.Humanoid.Touched:Connect(function(hit, _limb)
    local camFolder = game.workspace.:WaitForChild("Invisible"):WaitForChild("Camera")
    if hit.Name == "Hit@Lobby" then cameraLookAt(camFolder.Lobby.Cam.Position, camFolder.Lobby.Focus.Position) end
    if hit.Name == "Hit@Left"  then cameraLookAt(camFolder.Left.Cam.Position, camFolder.Left.Focus.Position) end
    if hit.Name == "Hit@Right" then cameraLookAt(camFolder.Right.Cam.Position, camFolder.Right.Focus.Position) end
end)
