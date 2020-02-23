#include "mh-uart.c"
int pwm=0,dir=1;
char mychar = 'a';

void delay_ms_spl (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {
    	x=532; while (x--);
    	pwm+=dir;
    	if(pwm==1023)dir=-1;
    	else if(pwm==0)dir=1;
    	OCR2 = (1023-pwm)>>2;
    	OCR1AH = pwm>>8;
    	OCR1AL = pwm&0xFF;
    	}
    	uart_send_byte(mychar++);
    	if(mychar=='z'+1)
    		{mychar = 'a';uart_send_byte('\n');}
    }

void blinkforward(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
    PORTB = 1<<i;
    delay_ms_spl(5);
  }

}

void blinkreverse(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
    PORTB = 1<<(7-i);
    delay_ms_spl(20);
  }

}

int main (void)
  {
  char i;
  DDRB = 255;		// Data Direction Register for port B
DDRD=255;
TCCR2 = 105;

TCCR1A=131;
TCCR1B=1;
OCR1AH=1;


uart_init(38400);
delay_ms_spl(100);

while(1){
	blinkforward();  
	blinkreverse();  

}
return 0;
}
