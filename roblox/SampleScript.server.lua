local TweenService = game:GetService('TweenService')
local HttpService = game:GetService('HttpService')

local ServerStorage = game:GetService('ServerStorage')
local BodyTrackerExternalModule = require(ServerStorage:WaitForChild('BodyTrackerExternal'))

local Terrain = workspace.Terrain

local tweenInfo = TweenInfo.new(0.075)
local origin = Vector3.new(0, 15, 0)
local scale = 1.25

local baseAttachment = Instance.new('Attachment')
baseAttachment.Visible = true
baseAttachment.Position = origin

local offsetValues = {
	['LeftHand'] = Vector3.new(1, 0, 0),
	['RightHand'] = Vector3.new(-1, 0, 0),
	['Face'] = Vector3.new(0, 1.5, 0),
	['Pose'] = Vector3.new(0, -0.1, 0),
}

local Attachments = {}
local function UpdateAttachments( Data )
	if Data.Success then
		Data.Body = HttpService:JSONDecode(Data.Body)
	else
		return
	end

	for category, pointsTable in pairs(Data) do
		if not Attachments[category] then
			Attachments[category] = {}
		end
		for index, pointData in pairs(pointsTable) do
			if not Attachments[category][index] then
				local attachment = baseAttachment:Clone()
				attachment.Name = category..'_'..index
				attachment.Parent = Terrain
				Attachments[category][index] = attachment
			end
			local offsetPosition = 5 * Vector3.new(pointData[1], -pointData[2], (category=='Pose' and 0.5 or 1) * pointData[3])
			local finalPosition = scale * (origin + offsetValues[category] + offsetPosition)
			--Attachments[category][index].Position = finalPosition
			TweenService:Create(Attachments[category][index], tweenInfo, {Position = finalPosition}):Play()
		end
	end
end

BodyTrackerExternalModule.DataUpdate:Connect(UpdateAttachments)

BodyTrackerExternalModule:Init()