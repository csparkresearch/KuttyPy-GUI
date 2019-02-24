/* 
Version of lcd.c handles floating point numbers in a crude manner, without using the
formatting functions of C library. Including this increases the program size a lot.
Use only if really necessary.
*/

#include "mh-lcd.c"


void lcd_put_float(float val, uint8_t ndec)
{
uint32_t  ival;
uint16_t  mf, dec;
uint8_t   k;
if(val < 0)
	{
	val = -val;
	lcd_put_char('-');
	}
if (ndec > 3) ndec = 3;  // maximum 3 decimals
mf = 1;
for(k =0; k < ndec; ++k) mf *= 10;
ival = val * mf + .5;         // multiply by 10^ndec
dec = ival % mf;
ival = ival / mf;
lcd_put_long(ival);
lcd_put_char('.');
lcd_put_int(dec);
}


