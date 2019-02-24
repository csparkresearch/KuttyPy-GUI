/* 
Program : kuttyPy.c
author  : Ajith Kumar (bpajith@gmail.com)
modified on 17-Dec-2018 by jithinbp@gmail.com
License : GNU GPL version 3 or above
A program to read/write the microcontroller registers from Python running on PC
*/

#include <avr/io.h>

#define VERSION   99     
#define GETVER    1

#define READB     2
#define WRITEB    3

void delay_ms (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {x=532; while (x--);}
    }


int main (void)
{
uint8_t cmd, data, *port;

  // Initialize the RS232 communication link to the PC 38400, 8, 1, N
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;
  UBRRL = 12;						// At 8MHz clock (12 =>38400 baudrate)
  UCSRC = (1 <<URSEL) | (1 << UCSZ1) | (1 << UCSZ0); 	// 8,1,N

  // Watchdog timer
  DDRD=32; PORTD=32; delay_ms(300);
  DDRD=0; PORTD=0;  
  WDTCR = (1<<WDE)|(1<<WDP2)|(1<<WDP1); 		// 1 second

  for(;;)			 			// Infinite loop waiting for commands from PC
    {
    while ( !(UCSRA & (1<<RXC)) ){asm("WDR");}		// wait for command from PC
    cmd = UDR;						// Store the received byte 
    if(cmd == GETVER)
		{
		UDR = VERSION;
		}
    else if(cmd == READB)
        {
        while ( !(UCSRA & (1<<RXC)) ) ;			// wait
		port = UDR;				// get the port address		
		UDR  = *port;
		}
	else if(cmd == WRITEB)
		{
		while ( !(UCSRA & (1<<RXC)) ) ;		// wait
		port = UDR;				// get the register address		
		while ( !(UCSRA & (1<<RXC)) ) ;		// wait
		data = UDR;				// get the data
		*port = data;				// write data to the port address
		}

	// Invalid commands are ignored silently
    }
}

