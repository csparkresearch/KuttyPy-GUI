#include "mh-utils.c"

#define DELAY 5
int main (void)
  {
DDRB = 15;  //For controlling the stepper motor
uint16_t pos = 0;
  for(;;)
	{
	for(pos=0;pos<50;pos++){
		PORTB=6;
		delay_ms(DELAY);
		PORTB=10;
		delay_ms(DELAY);
		PORTB=9;
		delay_ms(DELAY);
		PORTB=5;
		delay_ms(DELAY);
		}
	for(pos=0;pos<50;pos++){
		PORTB=9;
		delay_ms(DELAY);
		PORTB=10;
		delay_ms(DELAY);
		PORTB=6;
		delay_ms(DELAY);
		PORTB=5;
		delay_ms(DELAY);
		}
  }
return 0;
}
