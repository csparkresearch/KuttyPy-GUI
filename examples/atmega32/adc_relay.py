# Read ADC Values and enable a relay if the value exceeds
# the midpoint value of 512.
# This simple demo can be used to make a thermostat

import time
#from kuttyPy import *
setReg('DDRC',1)
setReg('ADMUX', (1<<6) | 5) #REF_AVCC | Channel 5
for a in range(50): 
    setReg('ADCSRA', 196)
    cl = getReg('ADCL')
    ch = getReg('ADCH')
    val = (ch<<8)|cl
    if(val>512):setReg('PORTC',1)
    else: setReg('PORTC',0)
    print(val)
    time.sleep(0.1)
    
