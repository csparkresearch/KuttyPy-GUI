## KuttyPy Interactive Playground [ Microcontroller Training Utility ]

![Screenshot](/docs/main.gif?raw=true "Recording of the User Interface")

---
The kuttyPy (/kʊtipʌɪ/) Microcontroller training utility allows real-time manipulation of the registers in microcontrollers via a connected computer containing its python library.  setReg and getReg function calls act as a real-time debugging and monitoring utility, and combined with Python's visualization and analytical utilities, this approach has immense pedagogical potential for beginners. 

The kuttyPy (/kʊtipʌɪ/) hardware is an ATMEGA32 microcontroller development board developed by the [ExpEYES](http://expeyes.in) project, and is currently supported by this software. It contains the kuttyPy firmware, but can also be used to run other programs via its bootloader.

## Simple blink.py example
![Screenshot](/docs/blink.gif?raw=true "Write Python code to blink all of PORT D")

![Screencast](/docs/monitor.gif?raw=true "Monitor your code!")

Monitor your code's activity while it executes

![Screencast](/docs/custom_registers.gif?raw=true "Add Register widgets, twiddle bits, and see what happens!")

Add custom register blocks, twiddle bits, and observe!
In this demo, the ADC is read by first setting the bits in the ADCSRA(control and status register), then reading back ADCL(8LSB)+ADCH(2MSB), and also checking the new status of ADCSRA after the operation.

### Plotting ADC values using matplotlib
![Screenshot](/docs/code.gif?raw=true "Recording of the ADC logging example")

![Screencast](/docs/monitor.gif?raw=true "Monitor your code!")

![Screencast](/docs/hall_sensor.webp?raw=true "Hall sensor!") ![Screencast](/docs/servo_motor.webp?raw=true "Hall sensor!")

Plug and play various accessories such as this Hall Sensor, & servo motor.

### Seamless switching between the KuttyPy monitor, and user uploaded hex file.
---

This functionality is undergoing alpha testing, and is not applicable for existing KuttyPy
boards where the user uploaded file overwrites the kuttypy monitor hex.
![App Switching](/docs/switch.gif?raw=true "App Switching")

This example shows how to skip to an LED scanning code written in C, and uploaded using
the bootloader to the application section of the KuttyPy. To regain control, the kuttypy-gui
simply triggers a reset.

![Screencast](/docs/pov_display.webp?raw=true "POV display!")

A persistence of vision display made with C code! Write text in thin air using 8 LEDs on PORTB.

### Installing on Ubuntu
+ sudo apt-get install python3 python3-pyqt5 python3-serial
---
+ python3 KuttyPyGUI.py

### Installing on windows.
+ This code can be run from source, provided python3 and pyqt5 are installed.
+ [Download Bundled Installer](https://drive.google.com/uc?export=download&id=1giJuDNIql8X5oaIcOLFACXD05-hmkBAy)



License: MIT



---
Developed by Jithin B.P @CSpark Research, 2018.  
Special thanks to Georges Khazanadar for Debianizing efforts.
