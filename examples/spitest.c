#include <avr/io.h>
#include "mh-utils.c"

#define RST    (1 << PB2)
#define DOC  (1 << PB3)
#define CEN  (1 << PB4)

void spiwrite(uint8_t data)
{
PORTB  &= ~CEN;
SPDR = data; 
delay_100us(1);
PORTB |= CEN;
//while( !(SPSR & (1<<SPIF) ) ) ;
}

int main()
{
int k;

DDRB = (1 <<  PB7) | (1 <<  PB5) | (1 <<  PB4) | (1 <<  PB3) | (1 <<  PB2)  ;    // SCK, MOSI,  CE. D/C  and  RST  outputs
SPCR = (1<<SPE) |  (1<<MSTR) |  (1<<SPR1);				//Enable SPI, Master, set clock rate fck/16 
PORTB &= ~RST;
delay_100us(1);
PORTB =  RST;
spiwrite(0x21);            // extended instruction mode
spiwrite(0x90);           // Vop

//spiwrite(0x14);          // bias to 100b

//spiwrite(0x20);            // normal instruction mode
spiwrite(0x0D);         // normal mode

PORTB |=  DOC;    // enter data mode 

for(;;) //k = 0; k < 5; ++k)
{
spiwrite(0x1f);
spiwrite(0x5);
spiwrite(0x7);
spiwrite(0x0);
}
return 0;
}
