import time
#from kuttyPy import *
setReg('DDRD',255)

for a in range(5):   #Run this loop 5 times. 
	setReg('PORTD', 255)
	time.sleep(0.5)
	setReg('PORTD', 0)
	time.sleep(0.5)
