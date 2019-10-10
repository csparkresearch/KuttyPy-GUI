'''
For Malus Law experiment
Connect stepper motor to PB0, PB1, PB2, PB3 (A+,B+,A-,B-)
Connect TSL2561 sensor to I2C
LASER Beam -> Polarizer -> Analyzer mounted on stepper motor -> TSL2561
'''
#from kuttyPy import *
from matplotlib import pyplot as plt
TSL2561_init()
TSL2561_gain(1)
TSL2561_timing(0)
setReg('DDRB',15)
steps=[3,6,12,9]
points = 0
Y=[]
for a in range(50):
	for b in steps:
		setReg('PORTB',b)
		plt.pause(0.1)
		lux = TSL2561_all()
		if lux is not None:
			print(points,lux)
			plt.scatter(points,lux[0])
			points+=1
		
	
