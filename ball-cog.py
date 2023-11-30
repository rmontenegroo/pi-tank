# from collections import deque
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time

# TRACKSIZE = 10

TARGET_COLOR = (0, 0, 255)
TARGET_RADIUS = 5

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
# pts = deque(maxlen=TRACKSIZE)

vs = VideoStream(src=0).start()

time.sleep(2.0)

while True:
	
    frame = vs.read()
	
    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv, greenLower, greenUpper)
    mask2 = cv2.erode(mask1, None, iterations=7)
    # mask = cv2.dilate(mask2, None, iterations=2)

    cnts = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:

        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        # M = cv2.moments(c)
        # center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 0:
            cv2.circle(frame, (int(x), int(y)), int(radius), TARGET_COLOR, 2)
            cv2.circle(frame, (int(x), int(y)), TARGET_RADIUS, TARGET_COLOR, -1)

        # if radius > 10:
        #     cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        #     cv2.circle(frame, center, 5, (0, 0, 255), -1)

    # pts.appendleft(center)

    # for i in range(1, len(pts)):
    #     if pts[i - 1] is None or pts[i] is None:
    #         continue

    #     thickness = int(np.sqrt(TRACKSIZE / float(i + 1)) * 2.5)
    #     cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # cv2.imshow("Frame", mask2)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
	    break

vs.stop()

cv2.destroyAllWindows()