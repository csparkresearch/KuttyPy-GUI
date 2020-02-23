/* Author: jithinbp@gmail.com 
*  GPL v3
* Adapted from the microHope library, and modified to dump float values over the serial port
*
* Distance measurement using an ultrasound echo module HY-SRF05 , 
* Trigger is connected to PB0 and the echo is connected to PB1.
*/

#include <stdlib.h>
#include "mh-utils.c"
#include "mh-timer.c"
#include "mh-uart.c"

int vsby2 = 17;                          // velocity of sound = 34 mS/cm 
int main()
{
uint32_t x,id,fd;
char buffer[20],cnt=0;
float distance=0;

DDRB |=  (1 << PB0);  // set PB0 as output   
DDRB &= ~(1 << PB1);  // and PB1 as input   
uart_init(38400);

while(1)
	{
	PORTB |=  (1 << PB0);         // Send a 100 usec wide HIGH TRUE Pulse on PB0 
	delay_10us(2);
	PORTB &=  ~(1 << PB0); 

	while( (PINB & 2) == 0 ) ;   // Wait for the Echo signal from the module
	start_timer();                        // start the timer using Timer/Counter1
	while( (PINB & 2) != 0 ) ;   // Wait for the Echo signal from the module
	x = read_timer() + 400;

	distance = x*vsby2/1000.;           // distance is time x velocity of sound / 2
	id = (int)distance;
	fd = (int)((distance-id)*100);
	utoa(id,buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>10)break;
	}
	uart_send_byte('.'); // decimal point	

	utoa(fd,buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>3)break;
	}
	uart_send_byte('\n');
	delay_ms(1);

	}
return 0;
}
