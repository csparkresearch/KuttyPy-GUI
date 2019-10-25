# 8 Channel 10 bit ADC
![Screenshot](images/voltmeter.gif?raw=true "Voltmeter")

PA0 - PA7 are ADC enabled pins on the ATMEGA32, and the graphical utility is capable of monitoring these. 
This makes it easy to record expected input values from analog sensors before hard-coding them into C programs.

<video controls width="600">
    <source src="../images/joystick.webm"
            type="video/webm">
    Sorry, your browser doesn't support embedded videos.
</video>

This 2 axis joystick's output is being monitored on PA6 and PA7. Notice how the values change when
the joystick is tilted along either axis

## Access via Python


```python tab="readADC" hl_lines="1"
def readADC(channel)
reads a voltage value from the specified channel, and returns it

  channel : 0 to 7
  return: 10 bit number( an integer between 0 and 1023 )

```

```python tab="data logger example with matplotlib"  hl_lines="1"
# Read values from Analog to Digital convertor(ADC) channel 5 (PA5), and plot them 
import time
from kuttyPy import *
from matplotlib import pyplot as plt

setReg('ADMUX', (1<<6) | 5) #REF_AVCC | Channel 5
for a in range(50): 
    setReg('ADCSRA', 196)
    cl = getReg('ADCL')
    ch = getReg('ADCH')
    plt.scatter(a, (ch<<8)|cl ,s=5)
    plt.pause(0.01) #Wait 10 mS
```

![Screenshot](images/code.gif?raw=true "Recording of the ADC logging example")

