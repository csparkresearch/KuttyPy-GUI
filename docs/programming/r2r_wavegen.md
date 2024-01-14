# R2R DAC based sine wave generator

``` quote
A simple resistor ladder Digital to Analog Convertor(DAC) was connected to PORTB.
Then, a C code was written to vary the output in a sinusoidal pattern by writing
a periodic sequence of values to PORTB
```


!!! tip "KuttyPy with R2R DAC Connected to ExpEYES17 oscilloscope"
	![](../images/r2r_conn.jpg "R2R DAC")

!!! tip "ExpEYES17 oscilloscope window showing the 0-5V waveform"
	![](../images/r2r_out.jpg "R2R DAC")
	Scipy based sine fitting reveals the frequency to be 1958.7Hz


Since calculation of sine values is resource intensive, a set of 128 values
between 0 and 255 were generated beforehand and saved in the form of a table
into the C code. This task is very easy with Python.

## Create the sine table with Python
* Create an x axis from 0 to 2*pi
* Calculate sine of each point (Output between -1 and 1)
* Scale these values (-1 to 1) to 0-255 
* round off to integers and print

### Python Code

=== "code to generate table"
	```python 
	import numpy as np
	x = np.linspace(0,np.pi*2,128) #128 points between 0 and 2*pi
	y = 255*(np.sin(x) + 1)/2.
	print([int(a) for a in y])
	```

=== "Output"
	```c
	[127, 133, 140, 146, 152, 158, 164, 170, 176, 182, 188, 193, 198, 203, 208, 213, 218, 222,
	226, 230, 234, 237, 240, 243, 245, 247, 249, 251, 252, 253, 254, 254, 254, 254, 254, 253, 
	252, 250, 248, 246, 244, 241, 238, 235, 232, 228, 224, 220, 215, 211, 206, 201, 196, 190, 
	185, 179, 173, 167, 161, 155, 149, 143, 136, 130, 124, 118, 111, 105, 99, 93, 87, 81, 75,
	69, 64, 58, 53, 48, 43, 39, 34, 30, 26, 22, 19, 16, 13, 10, 8, 6, 4, 2, 1, 0, 0, 0, 0, 0,
	1, 2, 3, 5, 7, 9, 11, 14, 17, 20, 24, 28, 32, 36, 41, 46, 51, 56, 61, 66, 72, 78, 84, 90,
	96, 102, 108, 114, 121, 127]
	```

## The final C code for sine waves

This iterates repeatedly through our sine table , and the output can be connected to any oscilloscope
for viewing

```c
#include <avr/io.h>

// The table we made earlier using Python
uint16_t table[] = {127,130,133,136,140,143,146,149,152,155,158,161,164,167,170,173,176,179,182,185,188,190,193,196,198,201,203,206,208,211,213,215,218,220,222,224,226,228,230,232,234,235,237,238,240,241,243,244,245,246,247,248,249,250,251,252,252,253,253,254,254,254,254,254,254,254,254,254,254,253,253,252,252,251,250,249,248,247,246,245,244,243,241,240,238,237,235,234,232,230,228,226,224,222,220,218,215,213,211,208,206,203,201,198,196,193,190,188,185,182,179,176,173,170,167,164,161,158,155,152,149,146,143,140,136,133,130,127,124,121,118,114,111,108,105,102,99,96,93,90,87,84,81,78,75,72,69,66,64,61,58,56,53,51,48,46,43,41,39,36,34,32,30,28,26,24,22,20,19,17,16,14,13,11,10,9,8,7,6,5,4,3,2,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,2,3,4,5,6,7,8,9,10,11,13,14,16,17,19,20,22,24,26,28,30,32,34,36,39,41,43,46,48,51,53,56,58,61,64,66,69,72,75,78,81,84,87,90,93,96,99,102,105,108,111,114,118,121,124,127};


int main (void)
  {
  uint16_t value=0,position = 0;
  DDRB = 255;		// Data Direction Register for port B

  for(;;)
    {
    value = table[position++];
    if(position==255){position=0;}
    /* WRITE VALUE TO DAC PORTB which should have a R2R DAC ladder*/
    PORTB=value;
  }
return 0;
}

```

* Save this code to example.c 
* Open it using the kuttyPy software
* Compile and upload!


## Exercises

* Make a triangular wave
* Make any arbitrary waveform by modifying the table generator code supplied in the beginning
