#include "mh-utils.c"
int pwm=0,dir=1;
int combo =0;

void delay_ms_spl (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {
    	x=532; while (x--);
    	pwm+=dir;
    	if(pwm==1023)dir=-1;
    	else if(pwm==0){
			dir=1;
			combo++;
			if(combo==3)combo=0;
		}
		
		if(combo==0){
			OCR2 = (1023-pwm)>>2;
			OCR1AH = (1023-pwm)>>8;
			OCR1AL = (1023-pwm)&0xFF;
		}else if(combo==1){
			OCR1AH = (1023-pwm)>>8;
			OCR1AL = (1023-pwm)&0xFF;
			OCR0 = (1023-pwm)>>2;

		}else if(combo==2){
			OCR0 = (1023-pwm)>>2;
			OCR2 = (1023-pwm)>>2;

		}




    	}
    }

void blinkb(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
	if(i!=3)
		PORTB = (1<<i);
    delay_ms_spl(20);
  }

}

void blinkd(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
	if(i!=0 && i!=2)
		PORTD = 1<<(7-i);
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

TCCR0 = 105;

delay_ms_spl(100);

while(1){
	blinkb();  
	blinkd();  

}
return 0;
}
