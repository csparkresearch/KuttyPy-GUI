This directory contains the KuttyPy AVR Training
utility firmware. Author: jithin B.P @ [CSpark Research Pvt Ltd](https://csparkresearch.in).

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

To upload the firmware, 
```
$ avrdude -b 38400 -P <serial port> -pm32 -c arduino -U flash:w:kuttyPy.hex 
```
This is only required if you reprogrammed it with your own hex files at some point.


