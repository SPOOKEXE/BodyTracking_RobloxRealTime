
import cv2
import json

import bodytracker as tracking
import network

LatestParseData = [None, None, None]

def onDataRecieve(_):
	return json.dumps([None, None, None])
	#return json.dumps(LatestParseData)

# Host
class RobloxHost(network.NetworkHost):
	def getReturnData(self, address, data):
		print(data)
		return onDataRecieve( data )
	def handleReceivedData(self, receieved_data):
		return True
	def __init__(self, ip, ports, password):
		super().__init__(ip, ports, password)
	pass

def ParseImage( parseImage ):
	drawn_image, face_mesh_results, hands_results, pose_results = tracking.ParseImage(parseImage)
	tracking.ShowImage(drawn_image)
	global LatestParseData
	LatestParseData = [
		tracking.ParseFaceMeshResults(face_mesh_results),
		tracking.ParseHandResults(hands_results),
		tracking.ParsePoseResults(pose_results)
	]

if __name__ == '__main__':
	print('start body tracker for roblox platform.')
	print('press escape to close video capture if opened')

	host = RobloxHost("127.0.0.1", [80], "epic")
	host.setup()

	videoCapture = cv2.VideoCapture(0)
	while videoCapture.isOpened():
		success, image = videoCapture.read()
		if not success:
			continue
		ParseImage( image )
		if cv2.waitKey(5) & 0xFF == 27:
			break
	videoCapture.release()
