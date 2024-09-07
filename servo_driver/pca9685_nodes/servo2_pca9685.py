#!/usr/bin/env python

#ROS IMPORTS
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
import os

#HARDWARE IMPORTS
import board
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import RPi.GPIO as GPIO

#IMPORT KINEMATIC LIBRARIES
import math as math

#GENERAL IMPORTS
from time import sleep as sleep
import time

# Define GPIO pins
#TRIG = 6  # Pin connected to TRIG #20
#ECHO = 5  # Pin connected to ECHO #21

TRIG_RIGHT = 6
ECHO_RIGHT = 5

TRIG_LEFT = 20
ECHO_LEFT = 21

# Set up GPIO
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_RIGHT, GPIO.OUT)
GPIO.setup(ECHO_RIGHT, GPIO.IN)
GPIO.output(TRIG_RIGHT, False)

GPIO.setup(TRIG_LEFT, GPIO.OUT)
GPIO.setup(ECHO_LEFT, GPIO.IN)
GPIO.output(TRIG_LEFT, False)



class ServoDriver(Node):
    
    #   TO DO
    #   1. Figure out Sudo Privileges for this script.
    #   2. Create Joystick Functionality (4 Buttons) 
    #   3. Create Seperate Kinematics Library
    #   4. Add Dependecies in Package.xml
    #   5. Create Launch File
    #   6. Create Helper Functions

    def __init__(self):
        super().__init__('ServoDriver')
        self.get_logger().info('Clifford Servo2 Driver Online...')

        #Declare our Publishers & Subscribers
        self.clifford_joy_sub = self.create_subscription( Joy, 'joy', self.clifford_joystick_callback,10)
        #self.cmd_vel_sub = self.create_subscription(Twist, 'cmd_vel',self.cmd_vel_callback,10)

        #INIT OUR HARDWARE
        i2c = board.I2C() # Init the I2C bus interface
        pca = PCA9685(i2c, address=0x40) # Create an instance of PCA9685
        pca.frequency = 60 # Set the PWM frequency to 60Hz
    
        #INIT CORRESPONDING CHANNELS
        self.front_left_shoulder = servo.Servo(pca.channels[12])
        self.front_left_arm = servo.Servo(pca.channels[13])
        self.front_left_wrist = servo.Servo(pca.channels[14])

        self.front_right_shoulder = servo.Servo(pca.channels[8])
        self.front_right_arm = servo.Servo(pca.channels[9])
        self.front_right_wrist = servo.Servo(pca.channels[10])

        self.back_left_shoulder = servo.Servo(pca.channels[4])
        self.back_left_arm = servo.Servo(pca.channels[5])
        self.back_left_wrist = servo.Servo(pca.channels[6])

        self.back_right_shoulder = servo.Servo(pca.channels[0])
        self.back_right_arm = servo.Servo(pca.channels[1])
        self.back_right_wrist = servo.Servo(pca.channels[2])

        #INIT PULSE PARAMETERS
        self.front_left_shoulder.set_pulse_width_range( 600,2400 )
        self.front_left_arm.set_pulse_width_range( 600,2400 )
        self.front_left_wrist.set_pulse_width_range( 600,2400 )

        self.front_right_shoulder.set_pulse_width_range( 600,2400 )
        self.front_right_arm.set_pulse_width_range( 600,2400 )
        self.front_right_wrist.set_pulse_width_range( 600,2400 )

        self.back_left_shoulder.set_pulse_width_range( 600,2400 )
        self.back_left_arm.set_pulse_width_range( 600,2400 )
        self.back_left_wrist.set_pulse_width_range( 600,2400 )

        self.back_right_shoulder.set_pulse_width_range( 600,2400 )
        self.back_right_arm.set_pulse_width_range( 600,2400 )
        self.back_right_wrist.set_pulse_width_range( 600,2400 )

        #INIT SERVO DUTY
        pca.channels[0].duty_cycle = 0x7FFF #50% Duty Cycle
        pca.channels[1].duty_cycle = 0x7FFF 
        pca.channels[2].duty_cycle = 0x7FFF 

        pca.channels[4].duty_cycle = 0x7FFF 
        pca.channels[5].duty_cycle = 0x7FFF 
        pca.channels[6].duty_cycle = 0x7FFF 
         
        pca.channels[8].duty_cycle = 0x7FFF 
        pca.channels[9].duty_cycle = 0x7FFF 
        pca.channels[10].duty_cycle = 0x7FFF 
        
        pca.channels[12].duty_cycle = 0x7FFF 
        pca.channels[13].duty_cycle = 0x7FFF 
        pca.channels[14].duty_cycle = 0x7FFF 
        
        #INIT SERVO RELATIVE COODS + MISC
        

        #EXTEND 8.11m
        #INIT OUR SERVOS TO CORRECT POSITIONS
        #self.init_servos()
        self.front_left_shoulder.angle = 87
        # self.front_left_arm.angle = 85  #OFFSET
        # self.front_left_wrist.angle = 105  #OFFSET

        self.back_right_shoulder.angle = 105
        # self.back_right_arm.angle = 100 #OFFSET
        # self.back_right_wrist.angle = 93  #OFFSET

        self.back_left_shoulder.angle = 100
        #self.back_left_arm.angle = 77  #OFFSET
        # self.back_left_wrist.angle = 109  #OFFSET

        self.front_right_shoulder.angle = 100
        # self.front_right_arm.angle = 102  #OFFSET
        # self.front_right_wrist.angle = 93  #OFFSET

        self.universal_shoulder_len = 58.17
        self.universal_arm_len = 107.00
        self.universal_wrist_len = 130.43

        #INIT OUR SERVO COORDINATE SYSTEM (TO DO)
        self.front_right_current = [-30.43,58.17,157.0]
        self.front_left_current =  [-30.43,58.17,165.0]
        self.back_right_current = [-30.43,58.17,157.0]
        self.back_left_current = [-30.43,58.17,165.0]

        self.front_right_target = [
            [-30.43,58.17,157.0],
            [-30.43,58.17,142.0],
            [10.43,58.17,142.0],
            [10.43,58.17,157.0]
        ]

        self.front_left_target = [
            [-30.43,58.17,163.0],
            [-60.43,58.17,163.0],
            [-60.43,58.17,148.0],
            [-30.43,58.17,148.0]
        ]
        
        self.back_left_target = [
            [-30.43,58.17,163.0],
            [-30.43, 58.17,148.0],
            [10.43,58.17,148.0],
            [10.43, 58.17,163.0]

        ]

        self.back_right_target = [
            [-30.43,58.17,157.0],
            [-60.43,58.17,157.0],
            [-60.43,58.17,142.0],
            [-30.43,58.17,142.0]
        ]

        #FLAGS FOR CLIFFORD DIFFERENT MODES DIFFERENT MODES
        self.idle_mode = 0
        self.walk_mode = 1
        self.clifford_walk_back = 0
        #self.prev_state = 0
       
        #TESTING VARIABLES FOR SINGLE LEG MOTION (07/24/24) / FRONT RIGHT
        self.speed_param = 6.0
        self.gait_walk_index = 0
        self.target_index = 1
        

        #GAIT VARIABLES
        self.set1_walk_index = 0
        self.set2_walk_index = 0
        self.set1_target_index = 1
        self.set2_target_index = 1
                
    
        #TESTING VARIABLES
        self.zero_coords = [130.43,58.17,107.0]
        self.start_coords = [0.43,58.17,167.0]

    def clifford_joystick_callback(self, data):
        #self.get_logger().info('Clifford Joystick Callback')
        
        # X button condition
        if data.buttons[0] == 1:
            self.walk_mode = 0
            self.get_logger().info('X Pressed...')
            self.lay_down() 
        # Circle button condition
        elif data.buttons[1] == 1:
            self.walk_mode = 0
            self.get_logger().info("Circle Pressed...")
            self.side_right_tilt()
        #Triangle button condition
        elif data.buttons[2] == 1:
            self.walk_mode = 0
            self.stand_up()  
        # Square button condition
        elif data.buttons[3] == 1:
            self.walk_mode = 0
            self.side_left_tilt()
        # Left Trigger    
        elif data.buttons[4] == 1:
            self.reset_gait()

        elif data.buttons[6] == 1:
            self.get_logger().info("LEFT BUMPER")
            self.walk_mode = 0
            self.tilt_back()

        elif data.buttons[7] == 1:
            self.get_logger().info("RIGHT BUMPER")
            self.walk_mode = 0
            self.tilt_forward()

        elif data.buttons[8] and data.buttons[9]:
            self.get_logger().info('System Shutdown Executing ')
            self.shutdown_rpi()

        self.clifford_object()

        if self.walk_mode == 1:     
            #CALCULATE SPEED VARIABLES
           
           
            speed_factor = 2.0
            if self.clifford_walk_back == 0:
                #self.get_logger().info("CLIFF SHOULD STOP")
                walk_speed = abs(data.axes[1] * self.speed_param)
                forward = data.axes[1] >= 0
            elif self.clifford_walk_back == 1:
                #self.get_logger().info("CLIFF SHOULD GO")
                walk_speed = abs(-.75 * self.speed_param)
                forward = False

            #FRONT RIGHT & BACK LEFT TAKING CHARGE
            if self.set1_walk_index in (0,1,2):
                
                if self.set1_walk_index == 0:
                    #FORWARD CONDITIONS
                    if forward:
                        self.front_right_current[2] -= walk_speed
                        self.back_left_current[2] -= walk_speed
                        self.front_left_current[0] -= (walk_speed/speed_factor)
                        self.back_right_current[0] -= (walk_speed/speed_factor)
                    else:
                        self.front_right_current[2] += walk_speed
                        self.back_left_current[2] += walk_speed
                        self.front_left_current[0] += (walk_speed/speed_factor)
                        self.back_right_current[0] += (walk_speed/speed_factor)

                    
                        #set1_coordinates and set2 are just variables to keep the code less confusing but really they are front_right/front_left
                    if forward and self.front_right_current[2] >= self.front_right_target[self.set1_target_index][2] or \
                        (not forward and self.front_right_current[2] <= self.front_right_target[3][2]):
                            self.update_servos()
                    else:
                        if forward:
                            self.front_right_current[2] = self.front_right_target[self.set1_target_index][2]
                            self.back_left_current[2] = self.back_left_target[self.set1_target_index][2]

                            self.set1_target_index = 2 
                            self.set1_walk_index = 1
                        else:
                            self.front_right_current[2] = self.front_right_target[self.set1_walk_index][2]
                            self.back_left_current[2] = self.back_left_target[self.set1_walk_index][2]
                            self.set1_walk_index = 3
                            self.set1_target_index = 0
                       
                        if not forward:
                            self.front_left_current[0] = self.front_left_target[self.set2_walk_index][0]
                            self.back_right_current[0] = self.back_right_target[self.set2_walk_index][0]
                            self.set2_walk_index = 3
                            self.set2_target_index = 0
                            
                elif self.set1_walk_index == 1:
                    
                    if forward:
                        self.front_right_current[0] += walk_speed
                        self.back_left_current[0] += walk_speed
                        self.front_left_current[0] -= (walk_speed / speed_factor)
                        self.back_right_current[0] -= (walk_speed / speed_factor)
                    else:
                        self.front_right_current[0] -= walk_speed
                        self.back_left_current[0] -= walk_speed
                        self.front_left_current[0] += (walk_speed / speed_factor)
                        self.back_right_current[0] += (walk_speed / speed_factor)

                    if (forward and self.front_right_current[0] <= self.front_right_target[self.set1_target_index][0]) or \
                    (not forward and self.front_right_current[0] >= self.front_right_target[1][0]):
                         self.update_servos()

                    else:
                        if forward:
                            #self.get_logger().info("HIT")
                            self.front_right_current[0] = self.front_right_target[self.set1_target_index][0]
                            self.back_left_current[0] = self.back_left_target[self.set1_target_index][0]

                            self.set1_walk_index = 2
                            self.set1_target_index = 3
                        else:
                            self.front_right_current[0] = self.front_right_target[self.set1_walk_index][0]
                            self.back_left_current[0] = self.back_left_target[self.set1_walk_index][0]
                            self.set1_walk_index = 0
                            self.set1_target_index = 1
                
                elif self.set1_walk_index == 2:
                    #self.get_logger().info('set1 walk index = 2')

                    if forward:
                        self.front_right_current[2] += walk_speed
                        self.back_left_current[2] += walk_speed
                        self.front_left_current[0] -= (walk_speed / speed_factor)
                        self.back_right_current[0] -= (walk_speed / speed_factor)
                    else:
                        self.front_right_current[2] -= walk_speed
                        self.back_left_current[2] -= walk_speed
                        self.front_left_current[0] += (walk_speed / speed_factor)
                        self.back_right_current[0] += (walk_speed / speed_factor)

                    if (forward and self.front_right_current[2] <= self.front_right_target[self.set1_target_index][2]) or \
                        (not forward and self.front_right_current[2] >= self.front_right_target[2][2]):
                            #self.check_fail_set2()
                            self.update_servos()
                            
                    else:
                        #self.get_logger().info('ELSE HIT')
                        
                        if forward:
                            self.front_right_current[2] = self.front_right_target[self.set1_target_index][2]
                            self.back_left_current[2] = self.back_left_target[self.set1_target_index][2]

                            self.set1_walk_index = 3
                            self.set1_target_index = 0
                        elif not forward:
                            self.front_right_current[2] = self.front_right_target[self.set1_walk_index][2]
                            self.back_left_current[2] = self.back_left_target[self.set1_walk_index][2]

                            self.set1_walk_index = 1
                            self.set1_target_index = 2
                      

                       # self.check_fail_set2()

                        if forward:

                            self.front_left_current[0] = self.front_left_target[self.set2_target_index][0]
                            self.back_right_current[0] = self.back_right_target[self.set2_target_index][0]
                            self.set2_walk_index = 1
                            self.set2_target_index = 2

            elif self.set2_walk_index in (1,2,3):
                speed_factor = 2.0
                if self.set2_walk_index == 1:
                    #self.get_logger().info('set2 walk index = 1')

                    if forward:
                        self.front_left_current[2] -= walk_speed
                        self.back_right_current[2] -= walk_speed
                        self.front_right_current[0] -= (walk_speed / speed_factor)
                        self.back_left_current[0] -= (walk_speed / speed_factor)
                    else:
                        self.front_left_current[2] += walk_speed
                        self.back_right_current[2] += walk_speed
                        self.front_right_current[0] += (walk_speed / speed_factor)
                        self.back_left_current[0] += (walk_speed / speed_factor)

                    if (forward and self.front_left_current[2] >= self.front_left_target[self.set2_target_index][2]) or \
                    (not forward and self.front_left_current[2] <= self.front_left_target[1][2]):
                        self.update_servos()
                    else:
                        #self.get_logger().info('ELSE HIT')
                        if forward:
                            self.front_left_current[2] = self.front_left_target[self.set2_target_index][2]
                            self.back_right_current[2] = self.back_right_target[self.set2_target_index][2]

                            self.set2_walk_index = 2
                            self.set2_target_index = 3
                        else:
                            self.front_left_current[2] = self.front_left_target[self.set2_walk_index][2]
                            self.back_right_current[2] = self.back_right_target[self.set2_walk_index][2]
                            self.set2_walk_index = 0
                            self.set2_target_index = 1


                        if not forward:
                            self.front_right_current[0] = self.front_right_target[self.set1_walk_index][0]
                            self.back_left_current[0] = self.back_left_target[self.set1_walk_index][0]
                            self.set1_walk_index = 2
                            self.set1_target_index = 3
                
                elif self.set2_walk_index == 2:
                    #self.get_logger().info('set2 walk index = 2')

                    # SET 2 COORDINATES
                    if forward:
                        self.front_left_current[0] += walk_speed
                        self.back_right_current[0] += walk_speed
                        self.front_right_current[0] -= (walk_speed / speed_factor)
                        self.back_left_current[0] -= (walk_speed / speed_factor)
                    else:
                        self.front_left_current[0] -= walk_speed
                        self.back_right_current[0] -= walk_speed
                        self.front_right_current[0] += (walk_speed / speed_factor)
                        self.back_left_current[0] += (walk_speed / speed_factor)

                    if (forward and self.front_left_current[0] <= self.front_left_target[self.set2_target_index][0]) or \
                        (not forward and self.front_left_current[0] >= self.front_left_target[2][0]):
                            #self.check_fail_set2()
                            self.update_servos()
                    else:
                        #self.check_fail_set2()
                        self.set2_walk_index = 3 if forward else 1
                        self.set2_target_index = 0 if forward else 2

                        if forward:
                            self.front_left_current[0] = self.front_left_target[self.set2_target_index][0]
                            self.back_right_current[0] = self.back_right_target[self.set2_target_index][0]

                            self.set2_walk_index = 3
                            self.set2_target_index = 0
                        else:
                            self.front_left_current[0] = self.front_left_target[self.set2_walk_index][0]
                            self.back_right_current[0] = self.back_right_target[self.set2_walk_index][0]

                            self.set2_walk_index = 1
                            self.set2_target_index = 2

                elif self.set2_walk_index == 3:
                    #self.get_logger().info('set2 walk index = 3')

                    # SET 2 COORDINATES
                    if forward:
                        self.front_left_current[2] += walk_speed
                        self.back_right_current[2] += walk_speed
                        self.front_right_current[0] -= (walk_speed / speed_factor)
                        self.back_left_current[0] -= (walk_speed / speed_factor)
                    else:
                        self.front_left_current[2] -= walk_speed
                        self.back_right_current[2] -= walk_speed
                        self.front_right_current[0] += (walk_speed / speed_factor)
                        self.back_left_current[0] += (walk_speed / speed_factor)

                    if (forward and self.front_left_current[2] <= self.front_left_target[self.set2_target_index][2]) or \
                        (not forward and self.front_left_current[2] >= self.front_left_target[3][2]):
                          #  self.check_fail_set1()
                            self.update_servos()
                    else:
                        #self.get_logger().info('ELSE HIT')
                      #  self.check_fail_set1()
                        # Update set2 indices
                       
                        if forward:
                            self.front_left_current[2] = self.front_left_target[self.set2_target_index][2]
                            self.back_right_current[2] = self.back_right_target[self.set2_target_index][2]
                            self.set2_walk_index = 0
                            self.set2_target_index = 1
                        else:
                            self.front_left_current[2] = self.front_left_target[self.set2_walk_index][2]
                            self.back_right_current[2] = self.back_right_target[self.set2_walk_index][2]
                            self.set2_walk_index = 2
                            self.set2_target_index = 3

                        # Update set1 indices if moving forward
                        if forward:
                            self.front_right_current[0] = self.front_right_target[self.set1_target_index][0]
                            self.back_left_current[0] = self.back_left_target[self.set1_target_index][0]

                            self.set1_walk_index = 0
                            self.set1_target_index = 1

    def clifford_object(self):
        check_dist = self.measure_distance_right()
        #self.get_logger().info(f"What is you doing {check_dist}")
        if check_dist < 20.0 and self.walk_mode == 1:
            # if self.prev_state == 0:
            #     self.prev_state = 1
            #     self.reset_gait()
            #self.get_logger().info("Clifford is moving back")
            self.clifford_walk_back = 1
        else:
            self.clifford_walk_back = 0 
            # if self.prev_state == 1:
            #     self.prev_state = 0
            #     self.reset_gait()
           # self.get_logger().info("Clifford is not moving back")

    def measure_distance_right(self):
        # Set the timeout threshold (in seconds)
        timeout_threshold = 0.02  # Adjust the threshold to match your needs (20 milliseconds)

        # Send a short pulse to trigger the ultrasonic burst
        GPIO.output(TRIG_RIGHT, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(TRIG_RIGHT, False)

        # Wait for the echo response with timeout
        pulse_start = time.time()
        start_time = time.time()

        # Wait for the echo signal to start (GPIO input goes HIGH)
        while GPIO.input(ECHO_RIGHT) == 0:
            pulse_start = time.time()
            if time.time() - start_time > timeout_threshold:
                self.get_logger().info("Ultrasonic sensor timeout: no response from ECHO_RIGHT (waiting for HIGH).")
                return 30.0  # Return an error value or handle the timeout

        # Wait for the echo signal to stop (GPIO input goes LOW)
        pulse_end = time.time()
        start_time = time.time()

        while GPIO.input(ECHO_RIGHT) == 1:
            pulse_end = time.time()
            if time.time() - start_time > timeout_threshold:
                self.get_logger().info("Ultrasonic sensor timeout: no response from ECHO_RIGHT (waiting for LOW).")
                return 30.0  # Return an error value or handle the timeout

        # Calculate the distance based on the time difference
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Sound speed in air (34300 cm/s) divided by 2
        distance = round(distance, 2)  # Round to two decimal places
        
        return distance

    def reset_gait (self):
        self.walk_mode = 1
        self.set1_walk_index = 0
        self.set2_walk_index = 0
        self.set1_target_index = 1
        self.set2_target_index = 1
        self.front_right_current = [-30.43,58.17,157.0]
        self.front_left_current =  [-30.43,58.17,165.0]
        self.back_right_current = [-30.43,58.17,157.0]
        self.back_left_current = [-30.43,58.17,165.0]

    def solve_ik_front_right(self,cords):
            # These kinematics calculations will try to be as descripitional as possible but please refer
            # to sheet of calculations by Cameron Bauman. 
            #UNIT: RADIANS & mm
            x_cord = cords[0] #x cord value
            y_cord = cords[1] #y cord value not really relevant rn.
            z_cord = cords[2] #z cord value

            #Find length B using Pythagorean's Theorem
            b_len = math.sqrt( pow(x_cord,2) + pow(z_cord,2) ) 
            
            # Angle of B
            beta_1 = math.atan(z_cord/x_cord)
            
            #Calculations for 'right_arm' and 'right_wrist' applied through cosine law.

            #This is the angle of which right_arm is set. This is necessary for calculating how the long will be SET
            beta_2 = math.acos( ( pow(self.universal_arm_len,2) + pow(b_len,2) - pow(self.universal_wrist_len,2) ) 
                                    / (2 * self.universal_arm_len * b_len) )

            #This is the angle of which right_wrist is set.
            beta_3 = math.acos( ( pow(self.universal_arm_len,2) + pow(self.universal_wrist_len,2) - pow(b_len,2) ) 
                                    / (2 * self.universal_arm_len * self.universal_wrist_len) )

            #Shouldn't be too relevant to calculations besides for RVIZ, but this is to make the calculations relative to their axes.
           
            if beta_1 < 0:
                theta_2 = abs(beta_1 + beta_2)
            else:
                theta_2 = math.pi - (beta_1 + beta_2)

            theta_3 = math.pi - beta_3

            #FINAL VALUE FOR RVIZ
            #theta_3 = (math.pi/2) - theta_3 #Final value of right_wrist
            #theta_3 = (math.pi/2) + beta_3
            arm_offset = 12
            wrist_offset = 3 

            theta_2 = (theta_2 * (180/math.pi)) + arm_offset
            theta_3 = (theta_3 * (180/math.pi)) + wrist_offset

            return [theta_2,theta_3]
        
    def solve_ik_front_left(self,cords):
        
            # These kinematics calculations will try to be as descripitional as possible but please refer
            # to sheet of calculations by Cameron Bauman. 
            #UNIT: RADIANS & mm
            #self.get_logger().info(f"LEG HAS FAILED AT {cords}")

            x_cord = cords[0] #x cord value
            y_cord = cords[1] #y cord value not really relevant rn.
            z_cord = cords[2] #z cord value

            #Find length B using Pythagorean's Theorem
            b_len = math.sqrt( pow(x_cord,2) + pow(z_cord,2) ) 
            
            # Angle of B
            beta_1 = math.atan(z_cord/x_cord)
            
            #Calculations for 'right_arm' and 'right_wrist' applied through cosine law.

            #This is the angle of which right_arm is set. This is necessary for calculating how the long will be SET
            beta_2 = math.acos( ( pow(self.universal_arm_len,2) + pow(b_len,2) - pow(self.universal_wrist_len,2) ) 
                                    / (2 * self.universal_arm_len * b_len) )

            #This is the angle of which right_wrist is set.
            beta_3 = math.acos( ( pow(self.universal_arm_len,2) + pow(self.universal_wrist_len,2) - pow(b_len,2) ) 
                                    / (2 * self.universal_arm_len * self.universal_wrist_len) )
            
            #Shouldn't be too relevant to calculations besides for RVIZ, but this is to make the calculations relative to their axes.
            if beta_1 < 0:
                theta_2 = math.pi + (beta_1 + beta_2)
            else:
                theta_2 = beta_1 + beta_2
            
            theta_3 = beta_3

            arm_offset = -5 
            wrist_offset = 15

            theta_2 = (theta_2 * (180/math.pi)) + arm_offset
            theta_3 = (theta_3 * (180/math.pi)) + wrist_offset

           # self.get_logger().info(f"THETA_3 before math corrects: {theta_3}")
            
            return [theta_2,theta_3]

    def solve_ik_back_right(self,cords):
            # These kinematics calculations will try to be as descripitional as possible but please refer
            # to sheet of calculations by Cameron Bauman. 
            #UNIT: RADIANS & mm
            x_cord = cords[0] #x cord value
            y_cord = cords[1] #y cord value not really relevant rn.
            z_cord = cords[2] #z cord value

            #Find length B using Pythagorean's Theorem

            b_len = math.sqrt( pow(x_cord,2) + pow(z_cord,2) ) 
            
            # Angle of B
            beta_1 = math.atan(z_cord/x_cord)
            #self.get_logger().info(f"shit broke {beta_1 * (180/math.pi)}")
            
            #Calculations for 'right_arm' and 'right_wrist' applied through cosine law.

            #This is the angle of which right_arm is set. This is necessary for calculating how the long will be SET
            beta_2 = math.acos( ( pow(self.universal_arm_len,2) + pow(b_len,2) - pow(self.universal_wrist_len,2) ) 
                                    / (2 * self.universal_arm_len * b_len) )

            #This is the angle of which right_wrist is set.
            beta_3 = math.acos( ( pow(self.universal_arm_len,2) + pow(self.universal_wrist_len,2) - pow(b_len,2) ) 
                                    / (2 * self.universal_arm_len * self.universal_wrist_len) )

            #self.get_logger().info(f"beta_2 {beta_2 * (180/math.pi)}")
            #self.get_logger().info(f"beta3 {beta_3 * (180/math.pi)}")

            #Shouldn't be too relevant to calculations besides for RVIZ, but this is to make the calculations relative to their axes.

            if beta_1 < 0:
                theta_2 = abs(beta_1 + beta_2)
            else:
                theta_2 = math.pi - (beta_1 + beta_2)


            theta_3 = math.pi - beta_3

            #FINAL VALUE FOR RVIZ
            #theta_3 = (math.pi/2) - theta_3 #Final value of right_wrist
            #theta_3 = (math.pi/2) + beta_3

            arm_offset = 10 
            wrist_offset = 3

            theta_2 = (theta_2 * (180/math.pi)) + arm_offset
            #self.get_logger().info(f"shit broke {theta_2}")
            theta_3 = (theta_3 * (180/math.pi)) + wrist_offset 
            #self.get_logger().info(f"shit broke {theta_3}")
            
            return [theta_2,theta_3]

    def solve_ik_back_left(self,cords):
    
    
        
            # These kinematics calculations will try to be as descripitional as possible but please refer
            # to sheet of calculations by Cameron Bauman. 
            #UNIT: RADIANS & mm
           # self.get_logger().info(f"LEG HAS FAILED AT {cords}")

            x_cord = cords[0] #x cord value
            y_cord = cords[1] #y cord value not really relevant rn.
            z_cord = cords[2] #z cord value

            #Find length B using Pythagorean's Theorem
            b_len = math.sqrt( pow(x_cord,2) + pow(z_cord,2) ) 
            
            # Angle of B
            beta_1 = math.atan(z_cord/x_cord)
            
            #Calculations for 'right_arm' and 'right_wrist' applied through cosine law.
        
            #This is the angle of which right_arm is set. This is necessary for calculating how the long will be SET
            beta_2 = math.acos( ( pow(self.universal_arm_len,2) + pow(b_len,2) - pow(self.universal_wrist_len,2) ) 
                                    / (2 * self.universal_arm_len * b_len) )

            #This is the angle of which right_wrist is set.
            beta_3 = math.acos( ( pow(self.universal_arm_len,2) + pow(self.universal_wrist_len,2) - pow(b_len,2) ) 
                                    / (2 * self.universal_arm_len * self.universal_wrist_len) )
            
            #Shouldn't be too relevant to calculations besides for RVIZ, but this is to make the calculations relative to their axes.
            theta_2 = math.pi + (beta_2 + beta_1)

            if beta_1 < 0:
                theta_2 = math.pi + (beta_1 + beta_2)
            else:
                theta_2 = beta_1 + beta_2

           # self.get_logger().info(f"shit broke {theta_2 * (180/math.pi)}")
            theta_3 = beta_3

            arm_offset = -13
            wrist_offset = 19

            theta_2 = (theta_2 * (180/math.pi)) + arm_offset
           
            theta_3 = (theta_3 * (180/math.pi)) + wrist_offset
            
            return [theta_2,theta_3]

    def solve_pitch(self, coords):
        self.get_logger().info(f"SOLVE FOR PITCH")

        C_value = math.sqrt( ( math.pow(coords[2],2) ) + math.pow(coords[1],2) )
        D_value = math.sqrt( math.pow(C_value,2) - math.pow(self.universal_shoulder_len,2) )
        self.get_logger().info(f"D VALUE: {D_value}")
            

        alpha = math.atan( coords[1] / coords[2] )
        beta = math.atan( D_value / self.universal_shoulder_len )
            
        self.get_logger().info(f"ALPHA VALUE: {alpha}")
        self.get_logger().info(f"BETA VALUE: {beta}")

        omega = alpha + beta
        theta_1 = math.pi - omega
        self.get_logger().info(f"OMEGA VALUE: {omega}")


        #define right shoulder = omega
        coords[2] = D_value #update only the z value

        theta_2,theta_3 = self.solve_ik_left(coords) #returned values of just z updated   
        theta_1 = theta_1 * (180/math.pi)

        return [theta_1,theta_2,theta_3]

    def update_servos(self):
         
        self.front_right_arm.angle, self.front_right_wrist.angle = self.solve_ik_front_right(self.front_right_current)
        self.back_left_arm.angle, self.back_left_wrist.angle = self.solve_ik_back_left(self.back_left_current)

        self.front_left_arm.angle, self.front_left_wrist.angle = self.solve_ik_front_left(self.front_left_current)   
        self.back_right_arm.angle, self.back_right_wrist.angle = self.solve_ik_back_right(self.back_right_current)

    def check_fail_set1 (self):
        if self.front_left_current[0] <= self.front_right_target[0][0]:
            self.front_right_current[0] = self.front_right_target[0][0]

        if self.back_left_current[0] <= self.back_left_target[0][0]:
            self.back_left_current[0] = self.back_left_target[0][0]

    def check_fail_set2(self):
        if self.front_left_current[0] <= self.front_left_target[1][0]:
            self.front_left_current[0] = self.front_left_target[1][0]

        if self.back_right_current[0] <= 0:
            self.back_right_current[0] = self.back_right_target[1][0]

    def stand_up(self):
        self.front_right_current[2] += 2.5
        self.front_left_current[2] += 2.5
        self.back_left_current[2] += 2.5
        self.back_right_current[2] += 2.5
        self.update_servos()

    def lay_down(self):
        self.front_right_current[2] -= 2.5
        self.front_left_current[2] -= 2.5
        self.back_left_current[2] -= 2.5
        self.back_right_current[2] -= 2.5
        self.update_servos()
    
    def tilt_back(self):
        self.back_left_current[2] -= 0.5
        self.back_right_current[2] -= 0.5
        self.update_servos()
        
    def tilt_forward(self):
        self.front_right_current[2] -= 0.5
        self.front_left_current[2] -= 0.5
        self.update_servos()

    def side_left_tilt(self):
        self.front_left_current[2] -= 1.5
        self.back_left_current[2] -= 1.5
        self.update_servos()

    def side_right_tilt(self):
        self.front_right_current[2] -=1.5
        self.back_right_current[2] -= 1.5
        self.update_servos()

    def shutdown_rpi(self):
        os.system('sudo shutdown -h now')

def main(args=None):
    rclpy.init(args=args)
    driveServos = ServoDriver()
    rclpy.spin(driveServos)
    driveServos.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()