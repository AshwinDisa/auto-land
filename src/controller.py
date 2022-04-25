#!/usr/bin/env python

import rospy
import math
import time
import tf
import numpy as np
import sys

from auto_land.msg import error

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from mavros_msgs.srv import CommandTOL
from mavros_msgs.srv import CommandBool
from mavros_msgs.srv import SetMode

global flag
global new_yaw
global yaw

def offboardmode():

	rospy.wait_for_service('/mavros/set_mode')
	response = change_mode(custom_mode="OFFBOARD")
	#rospy.loginfo(response)


def land():

	#offboardmode()
	rospy.wait_for_service('/mavros/cmd/land')
	response = landing_mode(altitude=0, latitude=0, longitude=0, min_pitch=0, yaw=0)
	#print("on sleep")
	rospy.sleep(200)
	#print("off sleep")
	sys.exit()

def orientation(error_message):

	#rospy.loginfo("Orienting")
	#offboardmode()

	twist = TwistStamped()

	yaw = error_message.rot_error
	
	#print(yaw)

	twist.header.frame_id = "base_link"
	twist.header.stamp = rospy.Time.now()
	
	if (error_message.z_error > 1):
		P_yaw = 0.1

	else:
		P_yaw = 0.05

	twist.twist.angular.z = yaw*P_yaw
	
	pub.publish(twist)
	rospy.sleep(0.1)

	#print(yaw)

def translation(error_message):

	#rospy.loginfo("Translating")
	twist = TwistStamped()

	x = error_message.x_error
	y = error_message.y_error
	z = error_message.z_error

	print(z)

	twist.header.frame_id = 'base_link_frd'
	twist.header.stamp = rospy.Time.now()
	
	P_x = 0.01
	P_y = 0.01
	P_z = 0.0

	#print(new_yaw)
	x_new, y_new = rotation(x,y,new_yaw)

	#print (x_new,y_new)

	twist.twist.linear.x = x_new*P_x
	twist.twist.linear.y = y_new*P_y

	#twist.twist.linear.x = x*P_x
	#twist.twist.linear.y = y*P_y



	#if (x < 5 or x > 5 and y < 5 or y > 5 and z > 1.2):
	
	if ( z > 0.8):
		#rospy.loginfo("descending")
		twist.twist.linear.z = -z*P_z

	elif (x < 5 and y < 5 and z < 0.8):
		
		land()

	pub.publish(twist)
	rospy.sleep(0.1)


def error_callback(error_message):

	offboardmode()
	
	if (error_message.counter == 0):
		orientation(error_message)
	else:
		translation(error_message)



def odom_callback(odom_message):

	x = odom_message.pose.pose.orientation.x
	y = odom_message.pose.pose.orientation.y
	z = odom_message.pose.pose.orientation.z
	w = odom_message.pose.pose.orientation.w

	quaternion = (x,y,z,w)

	euler = tf.transformations.euler_from_quaternion(quaternion)	

	global yaw 

	yaw = euler[2]

	global new_yaw 

	#new_yaw = ((yaw + 3.142) * 180/3.142)
	#new_yaw = yaw * 180/3.142

	new_yaw = yaw - 3.142

	#print(yaw-3.142)

	#return yaw

def rotation(x, y, new_yaw):


	sin_cos = [[math.cos(new_yaw), -math.sin(new_yaw)],
				[math.sin(new_yaw), math.cos(new_yaw)]]

	x_y = [x, y]

	result = np.dot(sin_cos, x_y)

	x_new = result[0]
	y_new = result[1]

	# print(new_yaw)
	# print([[math.cos(new_yaw), -math.sin(new_yaw)],
	# 			[math.sin(new_yaw), math.cos(new_yaw)]])
	# print(x, y, x_new, y_new)

	return x_new, y_new

if __name__ == '__main__':

	try:

		rospy.init_node('controller_node', anonymous=True)

		# vel publisher to mavros
		pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel", TwistStamped, queue_size=10)
		# sub to odom
		rospy.Subscriber("/mavros/local_position/odom", Odometry, odom_callback)
		# service to change to offboard
		change_mode = rospy.ServiceProxy('/mavros/set_mode', SetMode)
		# service to land
		landing_mode = rospy.ServiceProxy('/mavros/cmd/land', CommandTOL)
		# sub to error topic
		rospy.Subscriber("error_topic", error, error_callback)

		rospy.spin()

	except rospy.ROSInterruptException:
		rospy.loginfo("node terminated.")