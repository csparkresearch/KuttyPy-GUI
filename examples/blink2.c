#include "mh-utils.c"


int main (void)
  {
  DDRD = 255;		// Data Direction Register for port B
  for(;;)
    {
    PORTD = 255;	
    delay_ms(50);
    PORTD = 0;
    delay_ms(50);
  }
return 0;
}
