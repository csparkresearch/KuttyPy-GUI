# Control a robotic arm via PCA9685 PWM, with an MPU6050 accelerometer as user input.
# MPU6050 Ax range: Servo1 range, Ax Range to Servo2 Range, Ay range to Servo3 range for slope, intercept calculations
# 9700 - 16700 : 64 - 138 , 9700 -> 16700 : 131 - 33  -10K -> 10K   : 20 - 160 

#from kuttyPy import *
PCA9685_init()
MPU6050_init()
MPU6050_kalman_set(1)

m1 = (138-64.)/(16700-9700)
c1 = 64. - 9700*m1
m2 = (33-131.)/(16700-9700)
c2 = 131. - 9700*m2
m3 = (160-20.)/(10000. + 10000)
c3 = 20. + 10000*m3

while(1):
	x = MPU6050_all()
	if x is not None:
		PCA9685_set(1, int(m1*x[0]+c1))
		PCA9685_set(2, int(m2*x[0]+c2))
		PCA9685_set(3, int(m3*x[1]+c3))
