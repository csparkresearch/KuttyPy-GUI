# Read ADC Values and plot them
import time
#from kuttyPy import *
from matplotlib import pyplot as plt

setReg('ADMUX', (1<<6) | 0b01011) #REF_AVCC | A1-A0 x200
for a in range(50): 
    setReg('ADCSRA', 196)
    cl = getReg('ADCL')
    ch = getReg('ADCH')
    plt.scatter(a, (ch<<8)|cl ,s=5)
    plt.pause(0.01) #Wait 10 mS
