# The kuttyPy firmware

This is based on the optiboot bootloader, and has added functions for Registry R/W .
The bootloader's programming functions are retained, and in addition, the kuttyPy
while in bootloader mode can toggle register values.
 
![Screenshot](images/difference.png "difference")


## Compiling and uploading for Atmega32 boards

get the [firmware files here](https://github.com/csparkresearch/KuttyPy-GUI/) , and navigate to the firmware directory.

### dependencies
+ `gcc-avr` compiler
+ `avrdude` for uploading

### Make

The following command will output optiboot_atmega32.hex

```commandline
make atmega32
```

### Flash this bootloader

Connect a USBASP parallel programmer, and flash the bootloader firmware

```commandline
avrdude -B10 -c usbasp -patmega32 -U flash:w:optiboot_atmega32.hex
```

### set fuse to 0xDA

```commandline
avrdude -B10 -c usbasp -patmega32 -U lfuse:w:0xff:m -U hfuse:w:0xda:m
```

### Upload a hex file to test.

```commandline
avrdude -b 38400 -P /dev/ttyUSB0 -pm32 -c arduino -U flash:w:blink.hex
```

### Test the GUI (if it's installed)

```commandline
kuttypyplus
```

## For Arduino Uno and Nano boards

make
```commandline
make atmega328
```

upload : some Arduino Nano boards may work with -patmega328pb instead of -patmega328p.
```commandline
avrdude -B10 -c usbasp -patmega328p -U lfuse:w:0xff:m -U hfuse:w:0xda:m
```![Screenshot from 2024-09-20 08-34-18.png](../../../../Pictures/Screenshots/Screenshot%20from%202024-09-20%2008-34-18.png)