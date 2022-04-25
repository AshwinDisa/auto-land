#!/usr/bin/env python

import cv2
import numpy as np
import time
import rospy

def read_rgb_read(image_name):
	rgb_image = cv2.imread(image_name)
	cv2.imshow("RGB Image", rgb_image)
	return rgb_image

def filter_color(rgb_image, yellowLower, yellowUpper):
	hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2HSV)
	cv2.imshow("RGB Frame", rgb_image)
	#cv2.imshow("HSV Image", hsv_image)
	#yellowLower = (30, 150, 100)
	#yellowUpper = (50, 255, 255)
	mask = cv2.inRange(hsv_image, yellowLower, yellowUpper)
	return mask

def get_contours(binary_image):      
    _, contours, hierarchy = cv2.findContours(binary_image.copy(), 
                                            cv2.RETR_EXTERNAL,
	                                        cv2.CHAIN_APPROX_SIMPLE)
    return contours

def draw_ball_contour(binary_image, rgb_image, contours):
    black_image = np.zeros([binary_image.shape[0], binary_image.shape[1],3],'uint8')
    
    for c in contours:
        area = cv2.contourArea(c)
        perimeter= cv2.arcLength(c, True)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if (area>100):
            cv2.drawContours(rgb_image, [c], -1, (150,250,150), 1)
            cv2.drawContours(black_image, [c], -1, (150,250,150), 1)
            cx, cy = get_contour_center(c)
            cv2.circle(rgb_image, (cx,cy),(int)(radius),(0,0,255),1)
            cv2.circle(black_image, (cx,cy),(int)(radius),(0,0,255),1)
            cv2.circle(black_image, (cx,cy),5,(150,150,255),-1)
            #print ("Area: {}, Perimeter: {}".format(area, perimeter))
    #print ("number of contours: {}".format(len(contours)))
    #cv2.imshow("RGB Image Contours",rgb_image)
    cv2.imshow("Black Image Contours",black_image)

def get_contour_center(contour):
    M = cv2.moments(contour)
    cx=-1
    cy=-1
    if (M['m00']!=0):
        cx= int(M['m10']/M['m00'])
        cy= int(M['m01']/M['m00'])
    return cx, cy

def detect_ball_in_a_frame(rgb_image):
	
	#tennis ball
	#yellowLower = (30, 10, 10)
	#yellowUpper = (50, 255, 255)
	#cube Green
	#yellowLower = (45, 10, 10)
	#yellowUpper = (85, 255, 255)
	#red
	yellowLower = (150, 120, 100)
	yellowUpper = (255, 255, 255)

	#skin
	#yellowLower = (10, 10, 50)
	#yellowUpper = (255, 255, 70)
	
	binary_image_mask = filter_color(rgb_image, yellowLower, yellowUpper)
	contours = get_contours(binary_image_mask)
	draw_ball_contour(binary_image_mask, rgb_image, contours)


def main():
	#video_capture = cv2.VideoCapture(0)
	#video_capture = cv2.VideoCapture('/home/ashd/parrot_ws/ros_essentials_cpp/src/mywork/Perception/video/tennis-ball-video.mp4')
	image_sub = rospy.Subscriber('/usb_cam/image_raw', Image, image_callback)
	while True:
		ret, rgb_image = video_capture.read()
		detect_ball_in_a_frame(rgb_image)
		time.sleep(0.02)
		if cv2.waitKey(40) & 0xFF == ord('q'):
			break

	cv2.waitKey(0)
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()

cv2.waitKey(0)
cv2.destroyAllWindows()

