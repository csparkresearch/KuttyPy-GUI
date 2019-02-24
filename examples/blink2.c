#include "mh-utils.c"


int main (void)
  {
  DDRD = 255;		// Data Direction Register for port B
  for(;;)
    {
    PORTD = 255;	
    delay_ms(500);
    PORTD = 0;
    delay_ms(500);
  }
return 0;
}
