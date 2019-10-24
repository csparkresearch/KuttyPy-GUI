# Welcome to KuttyPy's documentation

The kuttyPy (/kʊtipʌɪ/) Microcontroller training utility allows live manipulation of the registers in microcontrollers via a connected computer containing its python library.

setReg and getReg function calls act as debugging and monitoring tools, and combined with Python's visualization 
and analytical utilities, this approach has immense pedagogical potential for beginners to the microcontroller world. 

The kuttyPy hardware is an ATMEGA32 microcontroller development board developed by the [ExpEYES](http://expeyes.in) project, and is currently supported by this software. It contains the kuttyPy firmware, but can also be used to run other programs via its bootloader.
It is being extended to support other microcontrollers as well, such as the 328p found on Arduino Nano boards.

![Screenshot](images/main.gif?raw=true "Recording of the User Interface")

---



---
## What can I use it for?

+ It's an atmega32 development board with a bootloader supporting the 'arduino' protocol
+ The bootloader also allows real-time manipulation of registers through commmands sent via the serial port.
+ This is done by the associated Python library and companion GUI
    + You can monitor every input
    + Toggle every output
    + Deal with Peripherals such as PWMs and Counters
    + View ADC readings via an analog gauge
    + Scan for sensors connected to the I2C Bus
    + Monitor readings from [sensors](sensors)
+ Compile code to hex with the avr-gcc compiler
+ Upload hex via the built-in uploader
+ Rapidly prototype and debug educational projects. For example, you can verify ADC input values before handing over control to the uploaded hex file which will likely have very limited debugging capabilities.
+ Learn how registers are the key to microcontroller operation, as opposed to the Arduino ecosystem which prefers obfuscation of these details underneath abstraction layers.

## Python library and Graphical utility

The graphical window featured in the cover animation allows exploring the functions of each pin of the hardware live, and also
viewing the corresponding register manipulations executed for each change. This knowledge can then be applied while writing C programs.
![Screenshot](images/blink.gif?raw=true "Write Python code to blink all of PORT D")

The python library has setReg and getReg functions calls to manipulate and read registers, in addition to a host of high level functions
to access sensors, ADC etc.
```python
from kuttyPy import * #Import the library. also automatically connects to any available kuttypy hardware.
setReg('DDRD',160) #0b10100000 PD7(BLUE LED) and PD5(GREEN LED) made output type
setReg('PORD',160) # PD5 and PD7 set to HIGH. Both LEDs start glowing
```

## Monitor I2C Sensors

You can plug and play a variety of support I2C sensors such as accelerometers, pressure sensors etc via the I2C pins (PC0:SCL, PC1:SDA).
[Details here](sensors)

![Screenshot](images/mpu6050.gif?raw=true "6 DOF inertial measurement unit MPU6050")

Data from a 6 DOF inertial measurement unit MPU6050 shown with beautiful analog guages. A data logger is also built-in, and
this includes analytical functions to select plot regions and fit against sinusoidal or damped sinusoidal functions for 
feature extraction and physics experiments.

## 7 channel voltmeter [ 0-5000mV without analog frontend ]
![Screenshot](images/voltmeter.gif?raw=true "Voltmeter")

PA0 - PA7 are ADC enabled pins. The graphical utility allows for their monitoring. This makes it easy to record expected input
values from analog sensors before hard-coding them into C programs.

## Plotting ADC values using matplotlib
![Screenshot](images/code.gif?raw=true "Recording of the ADC logging example")


Hall Sensor|Servo Motor
---|---
![Screencast](images/hall_sensor.webp?raw=true "Hall sensor!") | ![Screencast](/images/servo_motor.webp?raw=true "Hall sensor!")

Plug and play various accessories such as this Hall Sensor, & servo motor.

![Screencast](images/custom_registers.gif?raw=true "Add Register widgets, twiddle bits, and see what happens!")

Add custom register blocks, twiddle bits, and observe!
In this demo, the ADC is read by first setting the bits in the ADCSRA(control and status register), then reading back ADCL(8LSB)+ADCH(2MSB), and also checking the new status of ADCSRA after the operation.

## C Code compilation and uploading

### Seamless switching between the KuttyPy monitor, and user uploaded hex file.
---
The KuttyPy monitor code is part of the bootloader. This allows users to upload their own Hex files without losing the training utility features.

![App Switching](images/switch.gif?raw=true "App Switching")

This example shows how to skip back and forth to an LED scanning code (which also prints letters to the serial port) written in C and uploaded.

In the animation, after fiddling a little with the PWM controls on the monitor, the 'user app' button is clicked. This triggers the following:
+ Within a few ten milliseconds the user uploaded hex file starts executing
+ The console turns into a serial monitor, and shows any text sent by the user uploaded hex.

The user can switch back to the monitoring utility in a snap!

![Screencast](images/pov_display.webp?raw=true "POV display!")

A persistence of vision display made with C code! Write text in thin air using 8 LEDs on PORTB.


###Contributions:
+ Special thanks to Georges Khazanadar for Debianizing efforts.

We welcome packaging efforts for other linux distributions.

## Supporting KuttyPy

KuttyPy is an open source project. Its ongoing development is made possible thanks to the support by 
people who purchase the hardware. We do not yet have a Patreon campaign or equivalent.

---
Developed by Jithin B.P @CSpark Research, 2018. 
