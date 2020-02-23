/* MAX7219 display based counter. Interval fixed at 3S
 * adapted from : http://www.adnbr.co.uk/articles/max7219-and-7-segment-displays
 * Modified for ATMEGA32 -8MHz. Added code for 16 bit counting 
 * Author: jithinbp@gmail.com
 */

// 8MHz clock
#define F_CPU 8000000UL

// Outputs, pin definitions
#define PIN_SCK                   7
#define PIN_MOSI                  5
#define PIN_SS                    4

#define ON                        1
#define OFF                       0

#define MAX7219_LOAD1             PORTB |= (1<<PIN_SS)
#define MAX7219_LOAD0             PORTB &= ~(1<<PIN_SS)

#define MAX7219_MODE_DECODE       0x09
#define MAX7219_MODE_INTENSITY    0x0A
#define MAX7219_MODE_SCAN_LIMIT   0x0B
#define MAX7219_MODE_POWER        0x0C
#define MAX7219_MODE_TEST         0x0F
#define MAX7219_MODE_NOOP         0x00

#define MAX7219_DIGIT0            0x01
#define MAX7219_DIGIT1            0x02
#define MAX7219_DIGIT2            0x03
#define MAX7219_DIGIT3            0x04
#define MAX7219_DIGIT4            0x05
#define MAX7219_DIGIT5            0x06
#define MAX7219_DIGIT6            0x07
#define MAX7219_DIGIT7            0x08
#define MAX7219_DIGIT8            0x09

#define MAX7219_CHAR_BLANK        0xF 
#define MAX7219_CHAR_NEGATIVE     0xA 

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdlib.h>

#define COMPUTE_BAUD(b) ((uint32_t)(F_CPU)/((uint32_t)(b)*16) - 1)

char digitsInUse = 8;
volatile previous_count = 0;

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




void spiSendByte (char databyte)
{
    // Copy data into the SPI data register
    SPDR = databyte;
    // Wait until transfer is complete
    while (!(SPSR & (1 << SPIF)));
}

void MAX7219_writeData(char data_register, char data)
{
    MAX7219_LOAD0;
        // Send the register where the data will be stored
        spiSendByte(data_register);
        // Send the data to be stored
        spiSendByte(data);
    MAX7219_LOAD1;
}

void MAX7219_clearDisplay() 
{
    char i = 8;
    do {
        MAX7219_writeData(i, MAX7219_CHAR_BLANK);
    } while (--i);
}

void MAX7219_displayNumber(volatile long number,volatile char offset) 
{
    if (number == 0) {
        MAX7219_writeData(MAX7219_DIGIT0+offset, 0);
        return;
    }
    
    char i = 0; 
    do {
        MAX7219_writeData(offset+(++i), number % 10);
        number /= 10;
    } while (number);
}


volatile uint16_t overflow_count=0;
volatile uint16_t cnt = 0;
volatile char buffer[20];

// TIMER0 overflow interrupt service routine
ISR(TIMER0_OVF_vect)
{
	cnt = TCNT1;
	overflow_count +=1;
	MAX7219_clearDisplay();
	MAX7219_displayNumber(cnt,0);
	if(overflow_count>30){
		MAX7219_displayNumber(previous_count,4);
	}else{
		if((overflow_count>>3)%2==0)MAX7219_displayNumber(previous_count,4);
	}
	
	if (overflow_count > 99){ // 1 overflow_count = 255*128e-6 = 32.64mS . 309 = 10Seconds
	        // Send the total count. reset both timer and counter
	        previous_count = cnt;
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



int main(void)
{
    // SCK MOSI CS/LOAD/SS
    DDRB |= (1 << PIN_SCK) | (1 << PIN_MOSI) | (1 << PIN_SS);
    //PORTB = 3; //Pullup resistor on PB0, PB1. Otherwise 50 counts per second will appear due to 50Hz noise pickup.
    // Don't enable pullup for GM counter. Its output is too weak to pull down.
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


/*--Enable PD7 PWM output(Blue LED) . For a test signal output. Connect PB1 to PD7 with a wire to record counts. */
TCCR2 = 104+7; DDRD = 128; OCR2=127;  //310 counts in 10 Second interval.
//TCCR2 = 104+2; DDRD = 128; OCR2=127;    // 39676 counts in 10 second interval. (HF is more prone to error. Use short wire)
/*--------------------*/

sei();   				//enable interrupt


    // SPI Enable, Master mode
    SPCR |= (1 << SPE) | (1 << MSTR)| (1<<SPR0);

    // Decode mode to "Font Code-B"
    MAX7219_writeData(MAX7219_MODE_DECODE, 0xFF);

    // Scan limit runs from 0.
    MAX7219_writeData(MAX7219_MODE_SCAN_LIMIT, digitsInUse - 1);
    MAX7219_writeData(MAX7219_MODE_INTENSITY, 8);
    MAX7219_writeData(MAX7219_MODE_POWER, ON);

    int i = 999;
    while(1);
}
