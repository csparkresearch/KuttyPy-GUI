#include "mh-utils.c"

#define DELAY 10
#define STEPS 90
int main (void)
  {
DDRB = 15;  //For controlling the stepper motor
uint16_t pos = 0;
  for(;;)
	{
	for(pos=0;pos<STEPS;pos++){
		PORTB=3;
		delay_ms(DELAY);
		PORTB=6;
		delay_ms(DELAY);
		PORTB=12;
		delay_ms(DELAY);
		PORTB=9;
		delay_ms(DELAY);
		}
	for(pos=0;pos<STEPS;pos++){
		PORTB=12;
		delay_ms(DELAY);
		PORTB=6;
		delay_ms(DELAY);
		PORTB=3;
		delay_ms(DELAY);
		PORTB=9;
		delay_ms(DELAY);
		}
  }
return 0;
}
