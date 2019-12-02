/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Outputs integers from 0 to 10000 on the serial port in ASCII.
Terminated by newline.
*/

#include <avr/io.h>
#include <stdlib.h>

#define CPU_CLOCK	8000000		// 8 MHz clock is assumed
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



int main()
{
uint16_t x=0;
uint8_t cnt=0;
char buffer[20];
uart_init(38400);

while(1){
	for(x=0;x<=10000;x++){
		utoa(x,buffer,10); //10 means decimal.
		// Send in plain text. digit by digit, followed by newline character.
		for(cnt = 0;buffer[cnt]!='\0';cnt++){
			uart_send_byte(buffer[cnt]);
			if(cnt>10)break;
		}
		uart_send_byte('\n');	
	}
	
}
}


