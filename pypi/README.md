# KuttyPy Interactive Playground [ Microcontroller Training Utility ]

[![Documentation Status](https://readthedocs.org/projects/kuttypy/badge/?version=latest)](https://kuttypy.readthedocs.io/en/latest/?badge=latest)

---
The kuttyPy (/kʊtipʌɪ/) Microcontroller training utility allows live manipulation of the registers in microcontrollers via a connected computer containing its python library.  setReg and getReg function calls act as debugging and monitoring tools, and combined with Python's visualization and analytical utilities, this approach has immense pedagogical potential for beginners to the microcontroller world. 

The kuttyPy hardware is an ATMEGA32 microcontroller development board developed by the [ExpEYES](http://expeyes.in) project, and is currently supported by this software. It contains the kuttyPy firmware, but can also be used to run other programs via its bootloader.

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
    + Monitor readings from sensors [TSL2561 luminosity, and MPU6050 IMU supported]
+ Compile code to hex with the avr-gcc compiler
+ Upload hex via the built-in uploader
+ Rapidly prototype and debug educational projects. For example, you can verify ADC input values before handing over control to the uploaded hex file which will likely have very limited debugging capabilities.
+ Learn how registers are the key to microcontroller operation, as opposed to the Arduino ecosystem which prefers obfuscation of these details underneath abstraction layers.

## Monitor I2C Sensors

+ Scan for Sensors
+ Click to monitor via analog gauge
+ List of I2C sensors supported thus far (Minimal data logging. Configuration options via the graphical utility might be incomplete)
  + MPU6050 3 Axis Accelerometer, 3 axis Angular velocity (Gyro)
  + TSL2561 Luminosity measurements
  + BMP280 Pressure and Temperature sensor
  + MCP4725 Single channel DAC
  + PCA9685 PWM controller
  + MLX90614 Passive IR

Programming library and examples : [READ THE DOCS](https://kuttypy.readthedocs.io/en/latest/)


