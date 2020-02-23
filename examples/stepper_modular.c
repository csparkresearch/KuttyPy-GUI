#include "mh-utils.c"

#define DELAY 2
#define STEPS 200
//A+ A- B- B+
#define AP 8
#define AN 4
#define BP 1
#define BN 2


int main (void)
{
DDRD=160;
PORTD=0;
DDRB = 255;  //For controlling the stepper motor
uint16_t pos = 0,step=0;
uint8_t seq[4]={AP+BP,AN+BP,AN+BN,AP+BN}; //full step sequence. 
for(;;)
	{
		PORTD=32;//green = reverse
		for(step=0;step<STEPS;step++){
			for(pos=0;pos<4;pos++){	
				PORTB=seq[pos];
				delay_ms(DELAY);
			}
		}

		PORTD=128;//blue = fwd
		for(step=0;step<STEPS;step++){
			for(pos=4;pos>=1;pos--){
				PORTB=seq[pos-1];
				delay_ms(DELAY);
			}
		}

	}
return 0;
}
