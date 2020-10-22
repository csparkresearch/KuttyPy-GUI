#include "mh-utils.c"

#define DELAY 10
#define STEPS 40
int main (void)
  {
DDRB = 15;  //For controlling the stepper motor
uint8_t steps[]={0b1100,0b0110,0b0011,0b1001};
uint16_t pos = 0;
  for(;;)
	{
	for(pos=0;pos<STEPS;pos++){
		PORTB=steps[2];
		delay_ms(DELAY);
		PORTB=steps[1];
		delay_ms(DELAY);
		PORTB=steps[0];
		delay_ms(DELAY);
		PORTB=steps[3];
		delay_ms(DELAY);
		}
	for(pos=0;pos<STEPS;pos++){
		PORTB=steps[0];
		delay_ms(DELAY);
		PORTB=steps[1];
		delay_ms(DELAY);
		PORTB=steps[2];
		delay_ms(DELAY);
		PORTB=steps[3];
		delay_ms(DELAY);
		}
  }
return 0;
}
