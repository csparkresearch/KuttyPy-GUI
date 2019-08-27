/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Count pulses on PB1 per 400mS
*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include "mh-uart.c"
  
// TIMER1 overflow interrupt service routine
ISR(TIMER1_COMPA_vect)
{
    // Send the total count. reset both timer and counter
    uart_send_byte(TCNT0);
    TCNT0 = 0;
    TCNT1 = 0;
}

int main()
{
DDRB = 0;

uart_init(57600);

TCCR1B = (1 << CS12)|(1 << CS10);   // Normal mode, with 8MHz/1024 clock. 128uS step.
//OCR1A = 3125; //400e-3/128e-6   . Run ISR Every 400mS
OCR1A = 15625; //2000e-3/128e-6   . Run ISR Every 2S
//OCR1A = 31250; //400e-3/128e-6   . Run ISR Every 4S


OCR1B = 0xffff;
TIMSK = (1 <<  OCIE1A);   // Enable compare match interrupt
TIFR = (1 << OCF1A); 
TCNT1 = 0;
//------------

TCCR0 = 0b111; //rising edge on T0 (PB0) pin . 110 for rising edge.
TCNT0 = 0;

sei();   				//enable interrupt

for(;;) ;  // infinite loop. ISR does everything
}


