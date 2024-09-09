
#include <avr/io.h>   // Include file for I/O operations

#define BITVAL(bit) (1 << (bit))
#define CLRBIT(sfr, bit) (_SFR_BYTE(sfr) &= ~BITVAL(bit))
#define SETBIT(sfr, bit) (_SFR_BYTE(sfr) |= BITVAL(bit))
#define GETBIT(sfr, bit) (_SFR_BYTE(sfr) & BITVAL(bit))

int main (void)
{
  uint8_t  val;
  DDRA = 0;             // Port A as Input
  PORTA = 1;          // Enable pullup on PORTA, bit 0
  DDRB = 1;             // Pin 0 of Port B as output

  for(;;)
    {
    val = GETBIT(PINA, 0);
    if (val != 0)
       SETBIT(PORTB, 0);
    else
       CLRBIT(PORTB, 0);
    }

}
