
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose = mp_pose.Pose( min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Face Mesh Landmarks
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
def DrawFaceMeshLandmarks( parseImage, results ):
	for face_landmarks in results.multi_face_landmarks:
		mp_drawing.draw_landmarks(
			image=parseImage,
			landmark_list=face_landmarks,
			connections=mp_face_mesh.FACEMESH_TESSELATION,
			landmark_drawing_spec=drawing_spec,
			connection_drawing_spec=mp_drawing_styles
			.get_default_face_mesh_tesselation_style()
		)
		mp_drawing.draw_landmarks(
			image=parseImage,
			landmark_list=face_landmarks,
			connections=mp_face_mesh.FACEMESH_CONTOURS,
			landmark_drawing_spec=drawing_spec,
			connection_drawing_spec=mp_drawing_styles
			.get_default_face_mesh_contours_style()
		)
		mp_drawing.draw_landmarks(
			image=parseImage,
			landmark_list=face_landmarks,
			connections=mp_face_mesh.FACEMESH_IRISES,
			landmark_drawing_spec=drawing_spec,
			connection_drawing_spec=mp_drawing_styles
			.get_default_face_mesh_iris_connections_style()
		)

# Hand Landmarks
def DrawHandLandmarks( parseImage, results ):
	for hand_landmarks in results.multi_hand_landmarks:
		mp_drawing.draw_landmarks(
			parseImage,
			hand_landmarks,
			mp_hands.HAND_CONNECTIONS,
			mp_drawing_styles.get_default_hand_landmarks_style(),
			mp_drawing_styles.get_default_hand_connections_style()
		)

# Pose Landmarks
def DrawPoseLandmarks( parseImage, results ):
	mp_drawing.draw_landmarks(
		parseImage,
		results.pose_landmarks,
		mp_pose.POSE_CONNECTIONS,
		landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
	)

# Get XYZ List
def ParseFaceMeshResults( results ) -> list:
	landmarks_xyz = []
	if results.multi_face_landmarks != None:
		for face_landmarks in results.multi_face_landmarks:
			landmarks_xyz.append(face_landmarks.landmark)
	return landmarks_xyz

# Get XYZ List
def ParseHandResults( results ) -> list:
	landmarks_xyz = []
	if results.multi_hand_landmarks != None:
		for hand_landmarks in results.multi_hand_landmarks:
			landmarks_xyz.append(hand_landmarks.landmark)
	return landmarks_xyz

# Get XYZ List
def ParsePoseResults( results ) -> list:
	return results.pose_landmarks.landmark

def ParseImage( parseImage ):
	image = cv2.cvtColor(parseImage, cv2.COLOR_BGR2RGB)
	image.flags.writeable = False # slight performance boost
	
	# process
	face_mesh_results = face_mesh.process(image)
	hands_results = hands.process(image)
	pose_results = pose.process(image)	

	# Draw the landmarks on the image.
	image.flags.writeable = True
	image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
	if face_mesh_results.multi_face_landmarks:
		DrawFaceMeshLandmarks( image, face_mesh_results )
	if hands_results.multi_hand_landmarks:
		DrawHandLandmarks(image, hands_results)
	DrawPoseLandmarks(image, pose_results)

	return image, face_mesh_results, hands_results, pose_results

def ShowImage( parseImage ):
	cv2.imshow('Image Feed', cv2.flip(parseImage, 1))
