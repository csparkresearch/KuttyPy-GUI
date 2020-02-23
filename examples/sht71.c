#include <stdio.h>
#include <avr/io.h>
#include <stdlib.h>
#include "mh-utils.c"
#include "SHT71.c"

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


void uart_send_string(char *s){
	while(*s!='\0'){
		uart_send_byte(*(s++));
	}
}


void main(void)
{
double temp, hum;

char buffer[20],cnt;
uint32_t x,id,fd;

uart_init(38400);

uart_send_string("STARTED"); 

InitializeSensor(); //
   
  while (1)
      {
//InitializeSensor(); //
	//ReadSensor(&temp, COMMAND_READ_TEMPTERATURE);
	ReadTemperature(&temp);
	ReadHumidity(&hum,temp);
	uart_send_string("READ");

	id = (uint32_t)hum;
	fd = (uint32_t)((hum-id)*100);

	ltoa(id,buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>12)break;
	}
	uart_send_byte('.'); // decimal point	

	utoa(fd,buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>4)break;
	}
	uart_send_byte('\n');
	delay_ms(500);
      };
}
