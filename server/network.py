
import socket
import json
import _thread

finishKey = '5e100"'

# connections
def recieveAll(connection):
	data = []
	while 1:
		# recieve
		chunk = connection.recv(512)
		if not chunk:
			break
		chunk = chunk.decode('utf-8')
		# append
		data.append(chunk)
		# check if finished
		index = "".join(data).find(finishKey)
		if index != -1:
			break
	return "".join(data)

def hasPassword( data, password ):
	if (password == False):
		return True
	return type(data) == dict and ( 'CODE' in data.keys() ) and ( str(data['CODE']) == password )

class NetworkHost:
	ip = False
	ports = []
	password = False

	__sockets = []
	__threads = []
	__hasSetup = False

	# Override this for custom behavior.
	def getReturnData(self, addr, receieved_data):
		return {"Result": "Accepted"}
	
	# Override this for custom behavior.
	def handleReceivedData(self, receieved_data):
		print("Recieved:", receieved_data)

	# On Incoming Data, check validility.
	def __onDataRecieve(self, address, data):
		returnData = json.dumps({"Result": "Denied Access"})
		print( address, data )
		if hasPassword( data, self.password ):
			data.pop("CODE")
			self.handleReceivedData(data)
			returnData = json.dumps(self.getReturnData(address, data))
		return returnData

	# Setup socket handling
	def __setup_network_handle(self):
		while True:
			for sock in self.__sockets:
				conn, addr = sock.accept()
				print("Connection started; ", addr)
				data = recieveAll(conn)
				try:
					startIndex = data.find("{")
					endIndex = data.find(finishKey) - 2
					# print( startIndex, endIndex )
					# print( data[startIndex:endIndex] )
					data = json.loads(data[startIndex:endIndex])
				except:
					data = None
				# print(data)
				returnData = self.__onDataRecieve(addr, data)
				response_headers = { 'Content-Type': 'text/html; encoding=utf8', 'Content-Length': len(returnData), 'Connection': 'close' }
				response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.items())
				conn.sendall('HTTP/1.1 200 OK'.encode())
				conn.sendall(response_headers_raw.encode())
				conn.sendall('\n'.encode()) # to separate headers from body
				conn.sendall(str(returnData).encode())
				print("Close Connection")
				conn.close()

	def setup( self ):
		# prevent multiple occurences
		if self.__hasSetup:
			return
		self.__hasSetup = True
		# setup ports
		for portNumber in self.ports:
			print(self.ip + ":" + str(portNumber))
			newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			newSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			newSocket.bind((self.ip, portNumber))
			#newSocket.setblocking(0)
			newSocket.listen(1)
			self.__sockets.append(newSocket)
		# create a thread for handling the sockets
		self.__threads.append( _thread.start_new_thread(self.__setup_network_handle, ()) ) 
		print("Total of " + str(len(self.ports)) + " ports opened.")

	def kill( self ):
		# kill threads
		for thread in self.__threads:
			thread.exit()
		# close sockets
		for sock in self.__sockets:
			sock.shutdown(socket.SHUT_RDWR)

	# initialise
	def __init__( self, ip, ports, password ):
		self.ip = ip
		self.ports = ports
		self.password = str(password)
		# self.setup()
	pass