
local HttpService = game:GetService('HttpService')

local UPDATE_INTERVAL = 0.1 -- # per second
local HOST_URL = ''
local HOST_PASSWORD = ''

-- // Class // --
local EventProxy = {}
EventProxy.__index = EventProxy

function EventProxy.New()
	local self = {}
	self._bindable = Instance.new('BindableEvent')
	self._event = self._bindable.Event
	self._connections = {}
	self.USE_METHODS_ONLY = true -- tag
	return setmetatable(self, EventProxy)
end

function EventProxy:Fire(...)
	self._bindable:Fire(...)
end

function EventProxy:Connect(...)
	self._event:Connect(...)
end

function EventProxy:Destroy()
	self._bindable:Destroy()
	for _, connection in ipairs( self._connections ) do
		connection:Disconnect()
	end
	setmetatable(self, nil)
	for k, _ in pairs(self) do
		rawset(self, k, nil)
	end
end

-- // Module // --
local Module = {}

Module.DataUpdate = EventProxy.New()
Module.LatestData = false

function Module:GetLatestData()
	return Module.LatestData
end

function Module:ParseData( dataFromHostServer )
	print('Received Data ; ', dataFromHostServer)
end

function Module:RequestDataFromHostServer()
	local Data = false

	local success, errMsg = pcall(function()

		Data = HttpService:RequestAsync({
			Url = HOST_URL,
			Method = "POST",
			Body = HOST_PASSWORD,
			Headers = {["Content-Type"] = "application/json"}
		})

	end)

	if not success then
		warn(errMsg)
	end
	return Data
end

function Module:Init()
	local httpEnabled, _ = pcall(function()
		return HttpService:GetAsync('www.google.com')
	end)

	if not httpEnabled then
		warn('HttpService is not enabled. Cannot use the body tracker system.')
		return
	end

	task.defer(function()
		while true do
			local Data = Module:RequestDataFromHostServer()
			if Data then
				Data = Module:ParseData( Data )
				Module.LatestData = Data
				Module.DataUpdate:Fire(Data)
			end
			task.wait(UPDATE_INTERVAL)
		end
	end)
end

return Module

