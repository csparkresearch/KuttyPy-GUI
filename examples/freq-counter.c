// Connect the pulse  output set on PD7 to the input PB1

#include <avr/kp.h>   // Include file libkp

int main()
{
uint32_t f;

set_sqr_tc2(1000);    // Set a square wave on TC2 output (PD7)
lcd_init();
while(1)
   {
   f = measure_freq();   // Measures on T1 (PB1)
   lcd_clear();
   lcd_put_string("f=");
   lcd_put_long(f);
   delay_ms(200);
   }
}
