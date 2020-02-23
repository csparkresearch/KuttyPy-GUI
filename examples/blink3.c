#include "mh-utils.c"

int main (void)
  {
  DDRB=255;
	while(1){
	PORTB=255;
	delay_ms(100);
	PORTB=0;
	delay_ms(100);
		}

}
