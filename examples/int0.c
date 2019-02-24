#include <avr/io.h>
#include <avr/interrupt.h>

volatile uint8_t i=0;

ISR(INT0_vect)   // Interrupt Service Routine, called when PD2 (INT0) is grounded
{
PORTB = ++i;
}

int main (void)
  {
  DDRB = 255;
  PORTD = (1 << PD2);              // enable pull-up on PD2
  GICR |= (1 << INT0);               // enable INT0 interrupt
  MCUCR = ( 1 << ISC01);       // interrupt on falling edge 

  sei();    // enable interrupts globally

  for(;;)  ;   // wait loop , is a must
}
