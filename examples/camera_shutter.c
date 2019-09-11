/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Toggle the camera shutter and IR secondary shutter using PD2,3,4,5

*/

#include "mh-utils.c"
#define DELAY 10


int main (void)
  {
  DDRD = 255;		// Data Direction Register for port B
  for(;;)
    {
    PORTD = 1<<2;  //PD2 High. PD3 Low. Shutter opened	
    delay_ms(DELAY);
    PORTD = (1<<2)|(1<<5);  //PD2 High. PD3 Low. Shutter opened	. PD5 HIGH, PD4 LOW -> IR shutter open
    delay_ms(DELAY);
    PORTD = (1<<2)|(1<<4);  //PD2 High. PD3 Low. Shutter opened	. PD4 HIGH, PD5 LOW -> IR shutter close
    delay_ms(DELAY);


    PORTD = 0;
    delay_ms(DELAY);
  }
return 0;
}
