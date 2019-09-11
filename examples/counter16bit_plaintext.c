/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Count pulses on PB1
*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>

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


volatile uint16_t overflow_count=0;
volatile uint16_t cnt = 0;
volatile char buffer[20];

// TIMER0 overflow interrupt service routine
ISR(TIMER0_OVF_vect)
{

    cnt = TCNT1;
    overflow_count +=1;
    if (overflow_count > 309){ // 1 overflow_count = 255*128e-6 = 32.64mS . 309 = 10Seconds
	        // Send the total count. reset both timer and counter
		utoa(cnt,buffer,10); //10 means decimal.
		// Send in plain text. digit by digit, followed by newline character.
		for(cnt = 0;buffer[cnt]!='\0';cnt++){
			uart_send_byte(buffer[cnt]);
			if(cnt>10)break;
		}
		uart_send_byte('\n');
		overflow_count=0;
		TCNT1 = 0;
		}
    
}

int main()
{
DDRB = 0;
PORTB = 3; //Pullup resistor on PB0, PB1. Otherwise 50 counts per second will appear due to 50Hz noise pickup.

uart_init(38400);

TCCR1B = (1 << CS12)|(1 << CS11);   // T1 Pin . Falling edge.
OCR1A = 0; //   No overflow recording. Count up to 16bit (65535)
OCR1B = 0xffff;
TCNT1 = 0;
//------------
//TIFR = (1 << OCF1A); 

TIMSK |= 1<<TOIE0; //Timer 0 overflo interrrupt enabled
 
// Keep time using Timer 0
TCCR0 = (1 << CS02)|(1 << CS00);   // 1024 prescaler
TCNT0 = 0;


/*--Enable PD7 PWM output(Blue LED) . For a test signal output. Connect PB0 to PD7 with a wire to record counts. */
TCCR2 = 104+7; DDRD = 128; OCR2=127;  //310 counts in 10 Second interval.
//TCCR2 = 104+2; DDRD = 128; OCR2=127;    // 39676 counts in 10 second interval. (HF is more prone to error. Use short wire)
/*--------------------*/


sei();   				//enable interrupt

for(;;) ;  // infinite loop. ISR does everything
}


