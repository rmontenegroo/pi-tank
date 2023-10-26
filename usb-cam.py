import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

while True:	
	
	ret, image = cam.read()
		
	cv2.imshow('Imagetest', image)
	
	k = cv2.waitKey(1)
	
	if k != -1:
		break
		
cam.release()

cv2.destroyAllWindows()
