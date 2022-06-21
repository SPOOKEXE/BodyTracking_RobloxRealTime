
import os
import json
from sys import modules

directory = '/'.join(__file__.split("\\")[0:-1])
if not os.path.exists(directory + './conf.json'):
    file = open(directory + "./conf.json", 'a')
    file.write("""{
    "LOCAL_IP": "127.0.0.1",
    "PORT": 65433,
    "ACCESS_CODE": 1234567890,

    "SEND_DATA": {
        "LeftHand": true,
        "RightHand": true,
        "Head": true,
        "Pose": true
    },

    "DRAW_DATA": {
        "LeftHand": true,
        "RightHand": true,
        "Head": true,
        "Pose": true
    },

    "DETECTION_PARAMS": {
        "min_detection_confidence": 0.75,
        "min_tracking_confidence": 0.75
    },

    "SHOW_NODE_CAM": true,
    "SHOW_RAW_CAM": true,
    "CAPTURE_DEVICE": 0
}""")
    file.close()

with open(directory + "./conf.json", 'r') as myfile:
    data = myfile.read()
config_data = json.loads(data)

def GetFormattedInput(input, target_match):
    if type(target_match) == int:
        try:
            int(input)
            return int(input)
        except:
            return None
    if type(target_match) == bool:
        if input.upper() == "TRUE":
            return True
        elif input.upper() == "FALSE":
            return False
    if type(target_match) == str:
        return input
    return None

def RunConfigEdit():
    active_directory = config_data
    os.system('cls||clear')
    while True:
        print("\n")
        print("Config: \n", json.dumps(active_directory, indent=4, sort_keys=True), "\n")
        print("Type the path that you would like to edit.")
        print("! to go back, # to exit")
        print("\n")
        command = input(" ")
        if active_directory == config_data:
            command = command.upper()
        if command == '!':
            active_directory = config_data
        elif command == "#":
            break
        else:
            try:
                if type(active_directory[command]) == dict:
                    active_directory = active_directory[command]
                else:
                    old = active_directory[command]
                    new_value = GetFormattedInput(input("> "), old)
                    while new_value == None:
                        new_value = GetFormattedInput(input("> "), old)
                    active_directory[command] = new_value
            except:
                print("not a valid input") 
    with open(directory + "./conf.json", 'w') as myfile:
        myfile.writelines(json.dumps(config_data, indent=4))

print(json.dumps(config_data, indent=4, sort_keys=True))
if input("Do you want to edit the config? (y/n)") == "y":
    RunConfigEdit()
os.system('cls||clear')

# Multi Threading
import threading
class myThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func
    def run(self):
        self.func()

Captured = []

# Networking
import socket
import io

def HandleIncoming(address, incoming_json):
    print(address, incoming_json)
    return {"Nodes": Captured}

def SetupNetwork():
    print("PORT: " + str(config_data['PORT']))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((config_data['LOCAL_IP'], config_data['PORT']))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        my_json = data.decode('utf8')
        try:
            data = json.loads(my_json[my_json.find("{"):])
        except:
            data = None
        returnData = {"Denied Access."}
        if type(data) == dict:
            if 'ACCESS_CODE' in data.keys() and data['ACCESS_CODE'] == config_data['ACCESS_CODE']:
                returnData = json.dumps(HandleIncoming(addr, data))
        print('return: ', returnData, '\n')
        conn.sendall(str.encode(str(returnData)))
        #conn.sendall(str.encode(json.dumps(newest_capture)))
        #newest_capture.clear()
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
myThread(SetupNetwork).start()

# Capturing
import mediapipe as mp
import cv2
import numpy as np

def DATA_CHECK_IS_ACTIVE(index):
    if 'SEND_DATA' in config_data.keys():
        if index in config_data['SEND_DATA']:
            return config_data['SEND_DATA'][index]==True
    return False

def DRAW_CHECK_IS_ACTIVE(index):
    if 'DRAW_DATA' in config_data.keys():
        if index in config_data['DRAW_DATA']:
            return config_data['DRAW_DATA'][index]
    return False

def AddToQueue(holistic, results):
    send_data = {"LeftHand": [], "RightHand": [], "Face": [], "Pose": []}
    if DATA_CHECK_IS_ACTIVE('LeftHand') == True and results.left_hand_landmarks != None:
        for data in results.left_hand_landmarks.landmark:
            send_data["LeftHand"].append([data.x, data.y, data.z, data.visibility])
    if DATA_CHECK_IS_ACTIVE('RightHand') == True and results.right_hand_landmarks != None:
        for data in results.right_hand_landmarks.landmark:
            send_data["RightHand"].append([data.x, data.y, data.z, data.visibility])
    if DATA_CHECK_IS_ACTIVE('Face') and results.face_landmarks != None:
        for data in results.face_landmarks.landmark:
            send_data["Face"].append([data.x, data.y, data.z, data.visibility])
    if DATA_CHECK_IS_ACTIVE('Pose') and results.pose_landmarks != None:
         for data in results.pose_landmarks.landmark:
             send_data["Pose"].append([data.x, data.y, data.z, data.visibility])
    if len(send_data["LeftHand"]) > 0 or len(send_data["RightHand"]) > 0 or len(send_data["Face"]) > 0 or len(send_data["Pose"]) > 0:
        Captured.insert(0, send_data)
        if len(Captured) > 20:
            Captured.pop()

def SetupWebcams():
    # Initiate holistic model
    print("Activate Feed")
    mp_drawing = mp.solutions.mediapipe.python.solutions.drawing_utils
    mp_holistic = mp.solutions.mediapipe.python.solutions.holistic
    cap = cv2.VideoCapture(config_data['CAPTURE_DEVICE'])
    with mp_holistic.Holistic(min_detection_confidence=config_data['DETECTION_PARAMS']['min_detection_confidence'], min_tracking_confidence=config_data['DETECTION_PARAMS']['min_tracking_confidence'], smooth_landmarks=True) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if config_data['SHOW_RAW_CAM'] == True:
                cv2.imshow('Raw Webcam Feed', frame)
            results = holistic.process(image)
            AddToQueue(holistic, results)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if DRAW_CHECK_IS_ACTIVE('LeftHand') == True:
                mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2))
            if DRAW_CHECK_IS_ACTIVE('RightHand') == True:
               mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4), mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2))
            if DRAW_CHECK_IS_ACTIVE('Face') == True:
                mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS, mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1), mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1))
            if DRAW_CHECK_IS_ACTIVE('Pose') == True:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))         
            if config_data['SHOW_NODE_CAM'] == True:
                cv2.imshow('Overlay Webcam Feed', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                newest_capture = None
                break
    print("Close Capture")
    cap.release()
    cv2.destroyAllWindows()
myThread(SetupWebcams).start()