#include "mh-utils.c"

int main (void)
  {
  DDRB = 255;		// Data Direction Register for port B
  for(;;)
    {
    PORTB = 15;	
    delay_ms(500);
    PORTB = 240;
    delay_ms(500);
  }
return 0;
}
