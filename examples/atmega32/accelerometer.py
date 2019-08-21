import time
#from kuttyPy import *
print(I2CScan())
MPU6050_init()
for a in range(10):
	print(MPU6050_all())
	time.sleep(0.1)
