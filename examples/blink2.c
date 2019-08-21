#include "mh-utils.c"


int main (void)
  {
  DDRD = 255;		// Data Direction Register for port B
DDRC = 255;
  for(;;)
    {
    PORTD = 255;	
    delay_ms(500);
    PORTC = 255; 
    PORTD = 0;
    delay_ms(500);
    PORTC = 0 ;
  }
return 0;
}
