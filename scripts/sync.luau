local net = require("@lune/net")
local roblox = require("@lune/roblox")
local fs = require("@lune/fs")

local PLACE_ID = 4824908322
local cookie = roblox.getAuthCookie()
assert(cookie, "Failed to get auth cookie")

local response = net.request({
    url = "https://assetdelivery.roblox.com/v1/asset/",
    headers = {
        Cookie = cookie,
    },
    query = {
        id = tostring(PLACE_ID),
    },
})

assert(response.ok, response.body)
local game = roblox.deserializePlace(response.body)
fs.writeFile("src/Workspace.rbxm", roblox.serializeModel({ game.Workspace }))
fs.writeFile("src/Lighting.rbxm", roblox.serializeModel({ game.Lighting }))
fs.writeFile("src/TextChatService.rbxm", roblox.serializeModel({ game.TextChatService }))
