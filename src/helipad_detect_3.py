#!/usr/bin/env python

import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from auto_land.msg import error
from cv_bridge import CvBridge, CvBridgeError
import sys
import numpy as np

bridge = CvBridge()


def image_callback(ros_image):
	global bridge
	try:
		rgb_image = bridge.imgmsg_to_cv2(ros_image, "bgr8")
	except CvBridgeError as e:
		print (e)
	detect_ball_in_a_frame(rgb_image)


def filter_color(rgb_image, yellowLower, yellowUpper):
	hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2HSV)
	cv2.imshow("RGB Frame", rgb_image)
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
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        perimeter= cv2.arcLength(c, True)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(black_image, "altitude:", (100,75), font, 1, (255,255,255), 1)
        #cv2.putText(rgb_image, "altitude:", (100,75), font, 1, (255,255,255), 1)
        cv2.circle(rgb_image, (200,200), 20,(0,255,0),1)



        if (area>300):

			cv2.drawContours(rgb_image, [c], -1, (0,255,0), 1)
			cv2.drawContours(black_image, [c], -1, (150,250,150), 1)
			cx, cy = get_contour_center(c)
			cv2.circle(rgb_image, (cx,cy),(int)(radius),(255,255,255),1)
			cv2.circle(black_image, (cx,cy),(int)(radius),(255,255,255),1)
			cv2.circle(black_image, (cx,cy),5,(150,150,255),-1)
			cv2.circle(rgb_image, (cx,cy),5,(0,0,255),-1)
			

			area_circle = (3.142*radius*radius)
			alt = 149.4*pow(area_circle,(-0.4787))+0.09907
			alt = round(alt,3)
			print(area_circle)
			flag1 = 1
			cv2.putText(black_image, str(alt), (230,75), font, 1, (255,255,255), 1)
			#cv2.putText(rgb_image, str(alt), (230,75), font, 1, (255,255,255), 1)

			# areaRect = cv2.minAreaRect(c)
			# box = cv2.boxPoints(areaRect)

			# x_coor = 0

			# for p in box:
			# 	pt = (p[0], p[1])
			# 	if (pt[1]-cy > 70):
			# 		#print(pt[0]-cx)
			# 		#print(pt[1]-cy)
			# 		# diff_x = (x_coor - pt[0])
			# 		# if (diff_x < 5 and diff_x > -5):
			# 		# 	print("oriented", diff_x)
			# 		# elif (diff_x < -5 and diff_x > -80):
			# 		# 	print("not oriented", diff_x)

			# 		x_coor = pt[0]


			# 	cv2.circle(rgb_image,pt,5,(200,0,0),2)

			# flag = 0
			# if cx < 190 and cy < 190:
			# 	cv2.putText(black_image, "Go Left and Forward!", (20,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Left and Forward!", (20,350), font, 1, (255,255,255), 1)
			# 	flag = 1
			# if cx > 210 and cy < 190:
			# 	cv2.putText(black_image, "Go Right and Forward!", (20,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Right and Forward!", (20,350), font, 1, (255,255,255), 1)
			# 	flag = 1
			# if cx < 190 and cy > 210:
			# 	cv2.putText(black_image, "Go Left and Backward!", (20,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Left and Backward!", (20,350), font, 1, (255,255,255), 1)
			# 	flag = 1
			# if cx > 210 and cy > 210:
			# 	cv2.putText(black_image, "Go Right and Backward!", (10,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Right and Backward!", (10,350), font, 1, (255,255,255), 1)
			# 	flag = 1
			# if cx < 190 and flag == 0:
			# 	cv2.putText(black_image, "Go Left!", (130,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Left!", (130,350), font, 1, (255,255,255), 1)
			# if cx > 210 and flag == 0:
			# 	cv2.putText(black_image, "Go Right!", (130,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Right!", (130,350), font, 1, (255,255,255), 1)
			# if cy < 190 and flag == 0:
			# 	cv2.putText(black_image, "Go Forward!", (110,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Forward!", (110,350), font, 1, (255,255,255), 1)
			# if cy > 210 and flag == 0:
			# 	cv2.putText(black_image, "Go Backward!", (110,350), font, 1, (255,255,255), 1)
			# 	#cv2.putText(rgb_image, "Go Backward!", (110,350), font, 1, (255,255,255), 1)
			


	cv2.imshow("RGB Frame", rgb_image)
    cv2.imshow("Black Image Contours",black_image)
    cv2.waitKey(3)

    return cx,cy, alt

def draw_ball_contour_blue(binary_image, rgb_image, bluecontours, cx, cy, alt):
    #black_image = np.zeros([binary_image.shape[0], binary_image.shape[1],3],'uint8')

    for blue_c in bluecontours:
        #c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(blue_c)
        #perimeter= cv2.arcLength(blue_c, True)
        ((blue_x, blue_y), blue_radius) = cv2.minEnclosingCircle(blue_c)
        cv2.circle(rgb_image, (200,200), 20,(0,255,0),1)



        if (area>10):

			cv2.drawContours(rgb_image, [blue_c], -1, (0,255,0), 1)
			blue_cx, blue_cy = get_contour_center(blue_c)
			cv2.circle(rgb_image, (blue_cx,blue_cy),(int)(blue_radius),(255,255,255),1)

			publish(cx, cy, blue_cx, blue_cy, alt)
			
			
			#orientation_publish(cx, cy, blue_cx, blue_cy)
			
			
			#translation_publish(cx, cy, blue_cx, blue_cy)




	cv2.imshow("RGB Frame", rgb_image)
    #cv2.imshow("Black Image Contours",black_image)
    cv2.waitKey(3)

#def translation_publish(cx, cy, blue_cx, blue_cy):

	# pub = rospy.Publisher('error_topic', error, queue_size=10)
	# rate = rospy.Rate(100)
	# error_msg = error()

	# error_msg.rot_error = 0

	# if (cx < 200):
	# 	error_msg.x_error = cy - 200
	# else:
	# 	error_msg.x_error = cy - 200

	# if (cy < 200):
	# 	error_msg.y_error = cx - 200
	
	# else:
	# 	error_msg.y_error = cx - 200

	# pub.publish(error_msg)
	# rate.sleep()
	# counter()

#def orientation_publish(cx, cy, blue_cx, blue_cy):

	# pub = rospy.Publisher('error_topic', error, queue_size=10)
	# rate = rospy.Rate(100)
	# error_msg = error()

	# error_msg.x_error = 0
	# error_msg.y_error = 0

	# if (cy < blue_cy):
	# 	#print(cx - blue_cx)
	# 	if (cx > blue_cx):
	# 		error_msg.rot_error = 25
	# 		pub.publish(error_msg)
	# 		rate.sleep()

	# 	else:
	# 		error_msg.rot_error = -25
	# 		pub.publish(error_msg)
	# 		rate.sleep()

	# else:
	# 	error_msg.rot_error = cx - blue_cx
	# 	if (cx == blue_cx):
	# 		error_msg.counter = 1
	# 	else:
	# 		error_msg.counter = 0

	# 	pub.publish(error_msg)
	# 	rate.sleep()

	# counter()

#def counter(cx, cy, blue_cx, blue_cy):

	# pub = rospy.Publisher('error_topic', error, queue_size=10)
	# rate = rospy.Rate(100)
	# error_msg = error()

	# if (cx - blue_cx < 1 or cx - blue_cx > -1):
	# 	error_msg.counter = 1
	# else:
	# 	error_msg.counter = 0

	# pub.publish(error_msg)
	# rate.sleep()


def publish(cx, cy, blue_cx, blue_cy, alt):

	pub = rospy.Publisher('error_topic', error, queue_size=10)
	rate = rospy.Rate(100)
	error_msg = error()

	# orientation

	if (cy < blue_cy):
		#print(cx - blue_cx)
		if (cx > blue_cx):
			error_msg.rot_error = 25
			# pub.publish(error_msg)
			# rate.sleep()

		else:
			error_msg.rot_error = -25
			# pub.publish(error_msg)
			# rate.sleep()

	else:
		error_msg.rot_error = cx - blue_cx

	# translation

	if (cx < 200):
		error_msg.x_error = cy - 200
	else:
		error_msg.x_error = cy - 200

	if (cy < 200):
		error_msg.y_error = cx - 200
	
	else:
		error_msg.y_error = cx - 200

	# counter

	error_msg.rot_error = cx - blue_cx
	if (cx - blue_cx >= -1 and cx - blue_cx <= 1):
		error_msg.counter = 1
	else:
		error_msg.counter = 0

	error_msg.z_error = alt

	pub.publish(error_msg)
	rate.sleep()


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
	#yellowLower = (40, 50, 100)
	#yellowUpper = (60, 255, 255)
	#cube Green
	#yellowLower = (45, 10, 10)
	#yellowUpper = (85, 255, 255)
	#usb cam red
	#yellowLower = (120, 100, 10)
	#yellowUpper = (255, 255, 255)

	#sim red
	yellowLower = (0, 100, 100)
	yellowUpper = (255, 255, 255)
	blueLower = (50, 50, 0)
	blueUpper = (255, 255, 255)

	binary_image_mask = filter_color(rgb_image, yellowLower, yellowUpper)
	binary_image_mask_blue = filter_color(rgb_image, blueLower, blueUpper)
	contours = get_contours(binary_image_mask)
	bluecontours = get_contours(binary_image_mask_blue)
	cx,cy, alt = draw_ball_contour(binary_image_mask, rgb_image, contours)
	draw_ball_contour_blue(binary_image_mask_blue, rgb_image, bluecontours, cx, cy, alt)


def main(args):

	rospy.init_node('error_publisher_image_subscriber', anonymous=True)

	pub = rospy.Publisher('error_topic', error, queue_size=10)

	#image_sub = rospy.Subscriber('/usb_cam/image_raw', Image, image_callback)
	image_sub = rospy.Subscriber('stereo/right/image_raw', Image, image_callback)
	

	
	

	

	try:
		rospy.spin()
	except KeyboardInterrupt:
		print "Shutting Down"
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main(sys.argv)
