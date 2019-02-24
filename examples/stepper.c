#include "mh-utils.c"


int main (void)
  {
DDRA = 255;  //For controlling the stepper motor
DDRB = 0;    //input jumpers
PORTB=255;    //internal pullups
unsigned char high_torque_steps[4] = {3,6,12,9},low_torque_steps[4] = {1,2,4,8},pos = 0;
  for(;;)
	{
    if(!(PINB&128)){ //check state of D7( = 2^7).  high torque clockwise
		PORTA = high_torque_steps[pos];	
		delay_ms(100);
		if(pos>0)pos--;
		else pos=3;
	}
	else if(!(PINB&64)){//check state of D6.  high torque anticlockwise
		PORTA = high_torque_steps[pos];	
		delay_ms(100);
		pos++;
		if(pos==4)pos=0;
	}
	else if(!(PINB&32)){//check state of D6.  low torque clockwise
		PORTA = low_torque_steps[pos];	
		delay_ms(30);
		if(pos>0)pos--;
		else pos=3;
	}
	else if(!(PINB&16)){//check state of D6.  low torque anticlockwise
		PORTA = low_torque_steps[pos];	
		delay_ms(30);
		pos++;
		if(pos==4)pos=0;
	}
  }
return 0;
}
