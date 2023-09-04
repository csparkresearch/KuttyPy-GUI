// Reads ADC channel 0 and diplays the result on the LCD 

#include "mh-uart.c"
#include "mh-adc.c"

main()
{
uint16_t data;
uint16_t x=0;
uint8_t cnt=0;
char buffer[20];
uart_init(38400);

adc_enable();
DDRC=255;

while(1){
	for(x=0;x<=10000;x++){
			PORTC=x%255;
		data = read_adc(0);
		utoa(data ,buffer,10); //10 means decimal.
		// Send in plain text. digit by digit, followed by newline character.
		for(cnt = 0;buffer[cnt]!='\0';cnt++){
			uart_send_byte(buffer[cnt]);
			if(cnt>10)break;
		}
		uart_send_byte('\n');	
	}
	
}


}
