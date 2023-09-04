/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

Outputs floats with 1 decimal precision from 0 to 1000 on the serial port in ASCII.
Terminated by newline.
Simply for testing serial monitor's data logger and plotting
*/

#include <avr/io.h>
#include <stdlib.h>
#include <math.h>
#include "mh-utils.c"

#define CPU_CLOCK	8000000		// 8 MHz clock is assumed
#define COMPUTE_BAUD(b) ((uint32_t)(CPU_CLOCK)/((uint32_t)(b)*16) - 1)

//Outputs, pin definitions
#define PIN_SCK 7
#define PIN_MOSI 5
#define PIN_SS 4

//$0D ($2D) SPCR : SPIE SPE DORD MSTR CPOL CPHA SPR1 SPR0 
#define SPE 6
#define MSTR 4
#define SPR1 1
#define SPR0 0


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

uint16_t x=0,RTD_ADC_Code;
uint8_t cnt=0,dec=0;
float 	a = .00390830, b = -.000000577500, c = -0.00000000000418301;
float Res_RTD, R_REF, Res0,temp_C; 

R_REF=430.0;
Res0 = 101.7;

char buffer[10];
uart_init(38400);

//Initialize things
DDRB = (1 << PIN_SCK) | (1 << PIN_MOSI) | (1 << PIN_SS); //SCK MOSI CS/LOAD/SS

// SPI setting
/* Enable SPI, Master, set mode 3, set clock rate fck/128 */
SPCR =
	(0 << SPIE) |
	(1 << SPE)  |	// SPI enabled
	(0 << DORD) |
	(1 << MSTR) |	// Master
	(0 << CPOL) |	// Clock polarity
	(1 << CPHA) |	// Clock phase
	(0 << SPR1) |	// 
	(1 << SPR0);	// 

delay_ms(10);


PORTB &= ~(1<<PIN_SS);  //CS Low
SPDR = 0x80; //write to address 0
while(!(SPSR & (1<<SPIF)));	/* Wait till transmission complete */

SPDR = 0xC3; //value C3 . 50Hz filtering. continuous measurement mode. Bias always active
while(!(SPSR & (1<<SPIF)));	/* Wait till transmission complete */
PORTB |= (1<<PIN_SS);  //CS High


while(1){


	PORTB &= ~(1<<PIN_SS);  //CS Low

	// Start. Read configuration register.
	SPDR = 0x00; //read from address 0
	while(!(SPSR & (1<<SPIF)));	// Wait till transmission complete 
	SPDR = 0x00; //read from address 0
	while(!(SPSR & (1<<SPIF)));	// Wait till transmission complete 


	SPDR = 0x00; //read from address 0
	while(!(SPSR & (1<<SPIF)));	// Wait till transmission complete 
	RTD_ADC_Code = SPDR;

	SPDR = 0x00;
	while(!(SPSR & (1<<SPIF)));	// Wait till transmission complete
	RTD_ADC_Code = ((RTD_ADC_Code<<8)|SPDR );

	PORTB |= (1<<PIN_SS);  //CS High

	RTD_ADC_Code >>=1;

	Res_RTD = (((double)RTD_ADC_Code) * R_REF) / 32768.0; //PT100 Resistance
	temp_C = -(a*Res0) + sqrt(a*a*Res0*Res0 - 4*(b*Res0)*(Res0 - Res_RTD));
	temp_C = temp_C / (2*(b*Res0));
	if (temp_C < 0){
		temp_C = (RTD_ADC_Code/32) - 256;
		}


	// Send in plain text. digit by digit, followed by newline character.

	utoa((int)temp_C,buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>10)break;
		}
	uart_send_byte('.'); // decimal point	
	utoa(((int)(temp_C*100)%100),buffer,10); //10 means decimal.
	for(cnt = 0;buffer[cnt]!='\0';cnt++){
		uart_send_byte(buffer[cnt]);
		if(cnt>10)break;
		}


	uart_send_byte('\n');

	delay_ms(60);
	
	}

}
