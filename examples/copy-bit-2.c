
#include <avr/io.h>   // Include file for I/O operations


int main (void)
{
  DDRA = 0;             // Port A as Input
  PORTA = 1;          // Enable pullup on PORTA, bit 0
  DDRB = 1;             // Pin 0 of Port B as output

for(;;)
   if(PINA & 1)        // If PA0 is set
       PORTB |= 1;     // Set PB0, by ORing with 00000001b
   else                // otherwise clear PB0
       PORTB &= ~1;    // by ANDing with 11111110b (~00000001b)


}
