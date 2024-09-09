#include <avr/io.h>

int main(void)
{
  uint8_t data;

  DDRB = 255;
  UCSRB = (1 << RXEN) | (1 << TXEN);
  UBRRH = 0;             ////38400 baudrate, 8 databit, 1 stopbit, No parity
  UBRRL = 12;            // At 8MHz (12 =>38400)
  UCSRC = (1<<URSEL) | (1<<UCSZ1) | (1<< UCSZ0); 

  for(;;)
     {
     while ( !(UCSRA & (1<<RXC)) );  //wait on Rx
     data = UDR;                     // read a byte
     PORTB = data;
     while ( !(UCSRA & (1<<UDRE)) ); // Rx Empty ?
     UDR = data + 1;
  }
}