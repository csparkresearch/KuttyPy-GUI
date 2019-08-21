import time
#from kuttyPy import *
setReg('DDRB',255)

while 1:
	for x in range(20):
		for a in [3,6,12,9]:    
			setReg('PORTB', a)
			time.sleep(0.1)

	for x in range(20):
		for a in [12,6,3,9]:    
			setReg('PORTB', a)
			time.sleep(0.1)

setReg('PORTB', 0)
