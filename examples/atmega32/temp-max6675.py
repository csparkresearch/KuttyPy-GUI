# Read MAX6675 temperature Values and plot them
import time
#from kuttyPy import *
from matplotlib import pyplot as plt
import numpy as np

#Outputs, pin definitions
PIN_SCK = 7; PIN_MOSI = 5 ; PIN_SS = 4
#$0D ($2D) SPCR : SPIE SPE DORD MSTR CPOL CPHA SPR1 SPR0 
SPE = 6 ; MSTR = 4 ; SPR0 = 0
PORTBvalue = 0
#Initialize things
setReg('DDRB', (1 << PIN_SCK) | (1 << PIN_MOSI) | (1 << PIN_SS)) #SCK MOSI CS/LOAD/SS
setReg('SPCR', (1 << SPE) | (1 << MSTR)| (1<<SPR0) ) #SPI Master Mode.

plt.ion() #Interactive plot
x=[] ; y = []
start_time = time.time() #Staring time noted
for a in range(5): #Get 50 readings 
	t = time.time() - start_time #Elapsed time

	PORTBvalue &= ~(1<<PIN_SS) # CS Low
	setReg('PORTB', PORTBvalue)

	setReg('SPDR', 0xFF)
	time.sleep(0.001)#Wait until transfer is complete . //while (!(SPSR & (1 << SPIF)));
	v1 = getReg('SPDR')

	setReg('SPDR', 0xFF)
	time.sleep(0.001)#Wait until transfer is complete . //while (!(SPSR & (1 << SPIF)));
	v2 = getReg('SPDR')

	PORTBvalue |= (1<<PIN_SS) #CS High
	setReg('PORTB', PORTBvalue)
	temp = (v1<<8)|v2
	if temp&0x4: #Invalid reading. thermocouple disconnected. Continue the loop from the top.
		continue
	temp = (temp >>3 )*0.25 #Right shift and discard first 3 bits. Divide by 4 to get Celcius equivalent


	print(t,temp)
	plt.scatter(t, temp , s=5) #Scatter plot (x= point number, y = temperature)
	x.append(t); y.append(temp)
	plt.pause(0.2) #Wait 200 mS 
print('press any key/button to close')
np.savetxt('tmp.txt',np.column_stack([x,y]),fmt='%1.2f')
plt.waitforbuttonpress()
