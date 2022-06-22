local TweenService = game:GetService('TweenService')
local HttpService = game:GetService('HttpService')

local ServerStorage = game:GetService('ServerStorage')
local BodyTrackerExternalModule = require(ServerStorage:WaitForChild('BodyTrackerExternal'))

local Terrain = workspace.Terrain

local tweenInfo = TweenInfo.new(0.075)
local global_origin = Vector3.new(0, 15, 0)
local global_scale = 1.25

local baseAttachment = Instance.new('Attachment')
baseAttachment.Visible = true
baseAttachment.Position = global_origin

--[[
local offsetValues = {
	['LeftHand'] = Vector3.new(1, 0, 0),
	['RightHand'] = Vector3.new(-1, 0, 0),
	['Face'] = Vector3.new(0, 1.5, 0),
	['Pose'] = Vector3.new(0, -0.1, 0),
}]]

local Attachments = {}

local function UpdateAttachments( Category, PointsTable, Origin )
	-- print(Category, #PointsTable, Origin)
	if not Attachments[Category] then
		Attachments[Category] = {}
	end
	for index, pointData in pairs(PointsTable) do
		if not Attachments[Category][index] then
			local attachment = baseAttachment:Clone()
			attachment.Name = Category..'_'..index
			attachment.Parent = Terrain
			Attachments[Category][index] = attachment
		end
		local offsetPosition = 5 * Vector3.new(pointData[1], -pointData[2], pointData[3])
		local finalPosition = Origin + global_scale * ( global_origin + offsetPosition )
		-- Attachments[category][index].Position = finalPosition
		TweenService:Create(Attachments[Category][index], tweenInfo, {Position = finalPosition}):Play()
	end
end

local function ToVec3(array)
	local x,y = unpack(array)
	return Vector3.new(x, y)
end

local function OnDataUpdated(Data)

	Data = Data and HttpService:JSONDecode(Data)
	if not Data then
		return
	end

	local HeadData, HandData, PoseData = unpack(Data)

	-- Hand1  = 1-21, Hand2 = 22-42
	local LeftHand = {}
	table.move(HandData, 1, 21, 1, LeftHand) -- move all left hand points elsewhere

	UpdateAttachments( 'Pose', PoseData, Vector3.new() )
	local NeckPosition = ToVec3(PoseData[1]) -- ToVec3(PoseData[12]):Lerp(ToVec3(PoseData[13]), 0.5)
	UpdateAttachments( 'Head', HeadData, NeckPosition )
	local LeftHandPosition = ToVec3(PoseData[16])
	UpdateAttachments( 'Hand_Left', LeftHand, LeftHandPosition )
	local RightHandPosition = ToVec3(PoseData[17])
	UpdateAttachments( 'Hand_Right', HandData, RightHandPosition )
end

BodyTrackerExternalModule.DataUpdate:Connect(OnDataUpdated)
BodyTrackerExternalModule:Init()
