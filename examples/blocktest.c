
#include <avr/io.h>

#define	READBLOCK	 1	//  code for readblock is 1
#define NS			500 //	Maximum 1800 for ATmega32, with 2K RAM
#define TG			10  //	100 usec between samples

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

  for(;;)				// Infinite loop waiting for commands from PC
    {
    while ( !(UCSRA & (1<<RXC)) ) ;		// wait for data from PC
    if(UDR == READBLOCK)					
         {
	   TCCR1B = (1 << CS11);	// Timer Counter1 in Normal mode, 8 MHz/8, 1 usec per count
	   ADMUX = (1 << REFS0) |(1 << ADLAR) | 0; 		// 8 bit mode, AVCC as reference, channel 0
	   ADCSRA |= ADIF;						    	// reset ADC DONE flag
        
	    while( !(UCSRA & (1 <<UDRE) ) );         // Wait for transmit buffer empty flag
	    UDR = 'D';								 // Send the response byte in all cases
	    for(tmp16=0; tmp16 < NS; ++tmp16)	 // Send the collected data to the PC
	    	{
	    	while( !(UCSRA & (1 <<UDRE) ) );
	    	UDR = tmp16  & 0xff;
		}
           }

    }
}
