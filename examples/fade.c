#include "mh-utils.c"
int pwm=0,dir=1;

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
    }

void blinkb(void){
PORTA=0;
uint8_t i;
  for(i=0;i<8;i++)
    {
    PORTB = 1<<i;
    delay_ms_spl(20);
  }

}

void blinka(void){
uint8_t i;
PORTB=0;
  for(i=0;i<8;i++)
    {
    PORTA = 1<<(7-i);
    delay_ms_spl(20);
  }

}

int main (void)
  {
  char i;
  DDRB = 255;		// Data Direction Register for port B
DDRD=255;
DDRA=255;
TCCR2 = 105;

TCCR1A=131;
TCCR1B=1;
OCR1AH=1;

delay_ms_spl(100);

while(1){
	blinkb();  
	blinka();  

}
return 0;
}
