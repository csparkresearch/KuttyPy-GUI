/* 
Program : cro.c
author  : Ajith Kumar (ajith@iuac.res.in)
License : GNU GPL version 3 or above
On receiving a single byte command,reads ADC channel 0 500 times, with 100 usec timegap
and returns a 'D' followed by 500 bytes of data. No error checking implemented.
*/

#include <avr/io.h>

#define	READBLOCK	 1	//  code for readblock is 1
#define NS	500 	//  Maximum 1800 for ATmega32, with 2K RAM
#define TG	100  	//  100 usec between samples

uint8_t		tmp8, dbuffer[NS];	
uint16_t	tmp16;


int main (void)
{
  // Initialize the RS232 communication link to the PC 38400, 8, 1, N
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;
  UBRRL = 12;	// At 8MHz clock (12 =>38400 baudrate)
  UCSRC = (1 <<URSEL) | (1 << UCSZ1) | (1 << UCSZ0); // 8,1,N
  ADCSRA = (1 << ADEN);		// Enable the ADC

  for(;;)		// Infinite loop waiting for commands from PC
    {
    while ( !(UCSRA & (1<<RXC)) ); 	// wait for data from PC
    if(UDR == 1)			// '1' is our command
      {
      TCCR1B = (1 << CS11);	// TC1 in Normal mode, 8 MHz/8, 1 usec per count
      ADMUX = (1 << REFS0) |(1 << ADLAR) | 0; // 8 bit mode, AVCC ref, channel 0
      ADCSRA |= ADIF; 		    	// reset ADC DONE flag
      for(tmp16 = 0; tmp16 < NS; ++tmp16) 	// Digitize nsamples times
	 {
           TCNT1 = 1;
	 ADCSRA |= (1 << ADSC) | 1;   // Start AD conversion, ADC clock divider is 1
	 while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for conversion to complete
           dbuffer[tmp16] = ADCH;		// Collect Data and store it
	 ADCSRA |= ADIF;			// reset ADC DONE flag
           while(TCNT1L < TG) ;	// Wait on counter for the specified time gap
	 }
	// Why we are NOT sending data inside the above loop. Think about it. 
        
	 while( !(UCSRA & (1 <<UDRE) ) );       // Wait for transmit buffer empty flag
	 UDR = 'D';	     	          // Send the response byte in all cases
	 for(tmp16=0; tmp16 < NS; ++tmp16)	// Send the collected data to the PC
	    {
	    while( !(UCSRA & (1 <<UDRE) ) );
	    UDR = dbuffer[tmp16];
	   }
         }
    }
}
