//Distance measurement using an ultrasound echo module HY-SRF05 , Trigger is connected to PB0 and the echo is connected to PB1.

#include "mh-utils.c"
#include "mh-timer.c"
#include "mh-lcd.c"

int vsby2 = 17;                          // velocity of sound = 34 mS/cm 
int main()
{
uint32_t x;

DDRB |=  (1 << PB0);  // set PB0 as output   
DDRB &= ~(1 << PB1);  // and PB1 as inpt   
lcd_init();

while(1)
   {
   PORTB |=  (1 << PB0);         // Send a 100 usec wide HIGH TRUE Pulse on PB0 
   delay_100us(1);
   PORTB &=  ~(1 << PB0); 
   delay_100us(5);                    // wait 500 usecs to avoid false triggers

   start_timer();                        // start the timer using Timer/Counter1
   while( (PINB & 2) != 0 ) ;   // Wait for the Echo signal from the module
   x = read_timer() + 400;
   lcd_clear();
   lcd_put_long(x*vsby2/1000);           // distance is time x velocity of sound / 2
   delay_ms(500);
   }
return 0;
}
