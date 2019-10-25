# Writing Programs for KuttyPy

## Two options are available

+ Run the kuttypy as an accessory for controlling real world events from a Python code running on your laptop. 
	
	For example, you could use opencv to track an object, and kuttypy to control a robotic arm that interacts with it.

+ Write C code, compile it with avr-gcc, upload it to KuttyPy, and use KuttyPy as an independent processor. Example, a burglar alarm where kuttypy monitors a switch hooked up to a door, and enables an alarm when it is triggered. skip to [the C code section](../../programming/c) for details.


## Python Code Example

### Elementary Example : Blink an LED ( Red onboard LED connected to PB3 )

```python
import time
from kuttyPy import *   # The import statement automatically connects to an available device.

setReg('DDRB',8) # PB3 made output. 0b00001000 = 8

for a in range(5):   #Blink 5 times
	setReg('PORTB', 8) #PB3 to 5 Volt supply. LED turns on
	time.sleep(0.5)    # Wait for 0.5 second
	setReg('PORTD', 0) # PB3 set to 0 . LED is now off
	time.sleep(0.5)    # Wait for another 0.5 second
```
### Slightly Complex Example
Control a MeArm robotic arm via a 16-channel PWM generator(PCA9685), and an MPU6050 accelerometer as user input.
```python
import kuttyPy as kp
kp.PCA9685_init() # Initialize the I2C based 16-channel PWM generator
kp.MPU6050_init() # Init the MPU6050 3-axis accelerometer+ 3-axis gyro
kp.MPU6050_kalman_set(1) #Enable a moving average on MPU6050 to reduce jitter

# We need to map accelerometer values to motor angles of the robot.
# These values were obtained manually via the KuttyPy GUI, and now we'll calculate slopes and offsets
m1 = (138-64.)/(16700-9700)
c1 = 64. - 9700*m1
m2 = (33-131.)/(16700-9700)
c2 = 131. - 9700*m2
m3 = (160-20.)/(10000. + 10000)
c3 = 20. + 10000*m3

while(1):
	x = kp.MPU6050_all() # read values from the MPU6050. total 7 parameters
	if x is not None:    # Ensure no packet drop event
		kp.PCA9685_set(1, int(m1*x[0]+c1)) # Ax controls forearm
		kp.PCA9685_set(2, int(m2*x[0]+c2)) # Ax controls upper arm
		kp.PCA9685_set(3, int(m3*x[1]+c3)) # Ay controls rotation

```

!!! info "Manually controlling a Robotic Arm based on SG90 servos!"
	<video controls >
		<source src="../../images/robot.mp4"
				type="video/mp4">
		Sorry, your browser doesn't support embedded videos.
	</video>
	The robot is being controlled from the KuttyPy GUI by manually adjusting the PWM outputs of the PCA9685 PWM generator IC.
	This is super helpful to note which values correspond to which angles of the robot. 

