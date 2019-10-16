import time
#from kuttyPy import *
setReg('DDRB',1<<5)

for a in range(5):   #Run this loop 5 times. 
	setReg('PORTB', 1<<5)
	time.sleep(0.5)
	setReg('PORTB', 0)
	time.sleep(0.5)
