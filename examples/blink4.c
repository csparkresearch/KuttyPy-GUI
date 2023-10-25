#include "mh-utils.c"

int main (void)
  {
  DDRD = 255;		// Data Direction Register for port B
  for(;;)
    {
for(int i=0;i<8;i++){
    PORTD = 1<<i;	
    delay_ms(200);

}
  }
return 0;
}
