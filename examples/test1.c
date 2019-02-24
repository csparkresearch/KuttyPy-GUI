#include "mh-lcd.c"
#include "mh-uart.c"

int main(void)
{
uint8_t data, x;

UCSRB = (1<<RXEN) | (1<<TXEN);
UBRRH = 0;
UBRRL = 12;		// At 8MHz (12 =>38400) 
UCSRC = (1<<URSEL) | (1<<UPM1) | (1<<UCSZ1) | (1<<UCSZ0); // 8,1,E

for(;;)
	{
	while ( !(UCSRA & (1<<RXC)) ) ;		// wait 
	data = UDR & 255;					// get the register address	
	for(x = 0; x <data;++x)
  		{
    		while( !(UCSRA & (1 <<UDRE) ) );
		UDR = 65+x;
  		}
	}
}
