This directory contains the Optiboot small bootloader for AVR
microcontrollers, enhanced to include the KuttyPy AVR Training
utility developed by jithin B.P @ [CSpark Research Pvt Ltd](https://csparkresearch.in).

What is KuttyPy?
---

![Screenshot](../blink.gif?raw=true "Write Python code to blink all of PORT D")

An Open-Hardware microcontroller board with a python GUI companion
that allows real-time manipulation and reading of registers
in the processor. It allows a glimpse into the brain of
the processor (m32), if you may .

The hardware is designed by the [ExpEYES Project](http://expeyes.in/kuttypy/index.html).

The python-gui is authored by jithin B.P (jithinbp@gmail.com),
and is hosted on [github](https://github.com/csparkresearch/kuttypy-gui) by <a href="https://csparkresearch.in" target="_blank">CSpark Research</a>

KuttyPy Specific Enhancements:
---

The bootloader UART listener has been modified to listen
to the KUTTYPY_VERSION,KUTTYPY_READ,KUTTYPY_WRITE commands,
and if any of these are detected, it jumps into a loop
which can be exited by a reset.

Glitches exist, and need to be worked out. Until then,
kuttypy.hex is uploaded into the application section,
and a simple stk500v1 bootloader is provided.

------------------------------------------------------------
Building and uploading bootloader for KuttyPy. Tested on Ubuntu 18.04
with avr-gcc .

```Bash
$ make atmega32
$ avrdude -B10 -c <your programmer : usbasp/arduino/parallel> -patmega32 -U flash:w:optiboot_atmega32.hex 
```

The KuttyPy-GUI can now communicate with bootloader.
Please keep the RST jumper connected in order to enable the 
RTS based automatic software reset by the GUI trying to enter the loop.

To upload hex files compiled with avr-gcc, 
```
$ avrdude -b 38400 -P <serial port> -pm32 -c arduino -U flash:w:yourhex.hex 
```

The kuttypy GUI will soon have features for uploading hex files without
avrdude, and skipping the execution vector directly to the application code .

-----------------
Optiboot is more fully described here: http://code.google.com/p/optiboot/
and is the work of Peter Knight (aka Cathedrow), building on work of Jason P
Kyle, Spiff, and Ladyada.  Arduino-specific modification are by Bill
Westfield (aka WestfW)


------------------------------------------------------------

