#include <avr/io.h>

void delay_ms (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {x=532; while (x--);}
    }

void tc1_demo()    // this should be the zero crossing ISR
{
TCNT1 = 0;
// OC1RA should be set according to the ADC output
}

main(){
  TCCR1B = (1 << WGM12) | (1 <<CS11);	// Normal mode, 1 usec with 8MHz Clock
  TCCR1A = (1 << COM1A1) |(1 << COM1A0);    // Set OC1A on match
  OCR1A = 4000;     // Set OC1A (PD5) after 4 milliseconds
  DDRD |= (1 << PD5);   // Set pin OC1A as output
  
  while(1) {
  tc1_demo();
  delay_ms(50);
  }
  
}
