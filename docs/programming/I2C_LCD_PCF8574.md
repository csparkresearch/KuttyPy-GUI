## 16 Character LCD with I2C interface

This display uses a PCF8574 module which is an I2C I/O expander to stand as an
intermediary between a 16 character LCD display and the kuttypy.

The below example shows how to use it.


!!! tip "examples/C/test-i2c-lcd.c"
	```python
	#include <avr/kp.h>   // Include file for I/O operations
	
	int main (void)
	{
	i2c_lcd_init();
	
	i2c_lcd_clear();
	i2c_lcd_put_string("row  one!",1);
	i2c_lcd_put_string("row  two!",2);
	
	}
	```


