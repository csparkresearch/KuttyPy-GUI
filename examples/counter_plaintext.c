/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Count pulses on PB0 per 2S
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#define CPU_CLOCK	8000000		// 12 MHz clock is assumed
#define COMPUTE_BAUD(b) ((uint32_t)(CPU_CLOCK)/((uint32_t)(b)*16) - 1)


    //Initialise UART: format 8 data bits, No parity, 1 stop bit
void uart_init(uint32_t baud)
{
    UCSRB = (1 << TXEN) | (1 << RXEN);
    UBRRH = (COMPUTE_BAUD(baud) >> 8) & 0xff;
    UBRRL = (COMPUTE_BAUD(baud)) & 0xff;
    UCSRC = (1 << URSEL) | (1 << UCSZ1) | (1 << UCSZ0);
}


uint8_t uart_recv_byte(void)
{
    while( !(UCSRA & (1 <<RXC)) );
    return UDR;
}

void uart_send_byte(uint8_t c)
{
    while( !(UCSRA & (1 <<UDRE) ) );
    UDR = c;
}


  
// TIMER1 overflow interrupt service routine
ISR(TIMER1_COMPA_vect)
{
uint8_t cnt = 0;
    // Send the total count. reset both timer and counter
    cnt = TCNT0;
    TCNT0 = 0;
    TCNT1 = 0;
    
    // Send in plain text. digit by digit, followed by newline character.
    // Easy when using a serial terminal. Otherwise use counter.c which
    // sends only one byte per reading.
    uart_send_byte(cnt/100 + '0');
    cnt = cnt%100;
    uart_send_byte(cnt/10 + '0');
    uart_send_byte(cnt%10 + '0');
    uart_send_byte('\n');
}

int main()
{
DDRB = 0;
PORTB = 3; //Pullup resistor on PB0, PB1. Otherwise 100 counts per 2 seconds will appear due to 50Hz noise pickup.

uart_init(38400);

TCCR1B = (1 << CS12)|(1 << CS10);   // Normal mode, with 8MHz/1024 clock. 128uS step.
//OCR1A = 3125; //   400e-3/128e-6   . Run ISR Every 400mS
OCR1A = 15625; //   2000e-3/128e-6   . Run ISR Every 2S
//OCR1A = 31250; //  400e-3/128e-6   . Run ISR Every 4S

OCR1B = 0xffff;
TIMSK = (1 <<  OCIE1A);   // Enable compare match interrupt
TIFR = (1 << OCF1A); 
TCNT1 = 0;
//------------

// Count using Timer 0
TCCR0 = 0b111; //rising edge on T0 (PB0) pin . 110 for rising edge.
TCNT0 = 0;

sei();   				//enable interrupt

for(;;) ;  // infinite loop. ISR does everything
}


