## KuttyPy Interactive Playground [ Microcontroller Training Utility ]

![Screenshot](/docs/main.gif?raw=true "Recording of the User Interface")

---
The kuttyPy (/kʊtipʌɪ/) Microcontroller training utility allows real-time manipulation of the registers in microcontrollers via a connected computer containing its python library.  setReg and getReg function calls act as a real-time debugging and monitoring utility, and combined with Python's visualization and analytical utilities, this approach has immense pedagogical potential for beginners. 

The kuttyPy (/kʊtipʌɪ/) hardware is an ATMEGA32 microcontroller development board developed by the [ExpEYES](http://expeyes.in), and is currently supported by this software. It contains the kuttyPy firmware, but can also be used to run other programs via its bootloader.

## Simple blink.py example
![Screenshot](/docs/blink.gif?raw=true "Write Python code to blink all of PORT D")

![Screencast](/docs/monitor.gif?raw=true "Monitor your code!")
Monitor your code's activity while it executes

![Screencast](/docs/custom_registers.gif?raw=true "Add Register widgets, twiddle bits, and see what happens!")
Add custom register blocks, twiddle bits, and observe!
In this demo, the ADC is read by first setting the bits in the ADCSRA(control and status register), then reading back ADCL(8LSB)+ADCH(2MSB), and also checking the new status of ADCSRA after the operation.

## Plotting ADC values using matplotlib
![Screenshot](/docs/code.gif?raw=true "Recording of the ADC logging example")



### Installing on Ubuntu
+ sudo apt-get install python3 python3-pyqt5 python3-serial


---
+ python3 KuttyPy.py


License: MIT



---
Developed by Jithin B.P @CSpark Research, 2018
