#include "mh-utils.c"
volatile int pwm=1,dir=1, combo=0;

void delay_ms_spl (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {
    	x=1500; while (x--);
    	pwm+=dir;
    	if(pwm==1023){
		dir=-1;
		}
    	else if(pwm==0){
		dir=1;
		combo++;
		if(combo==7)combo=0;
		}


if(combo==0){
    	OCR0 = (1023-pwm)>>2;
}else if(combo==1){
    	OCR2 = (1023-pwm)>>2;
}else if(combo==2){
    	OCR1AH = (1023-pwm)>>8;
    	OCR1AL = (1023-pwm)&0xFF;
}else if(combo==3){
    	OCR2 = (1023-pwm)>>2;
}else if(combo==4){
    	OCR0 = (1023-pwm)>>2;
    	OCR1AH = (1023-pwm)>>8;
    	OCR1AL = (1023-pwm)&0xFF;
}else if(combo==5){
    	OCR2 = (1023-pwm)>>2;
    	OCR1AH = (1023-pwm)>>8;
    	OCR1AL = (1023-pwm)&0xFF;
}else if(combo==6){
    	OCR0 = (pwm)>>2;
    	OCR1AH = (1023-pwm)>>8;
    	OCR1AL = (1023-pwm)&0xFF;
}

    	}
    }

void blinkforward(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
    PORTB = (1<<i)&(~8);
    PORTD = (1<<i)&(~8);
    delay_ms_spl(20);
  }

}

void blinkreverse(void){
uint8_t i;
  for(i=0;i<8;i++)
    {
    PORTB = 1<<(7-i);
    PORTB = (1<<(7-i))&(~196);
    delay_ms_spl(20);
  }

}

int main (void)
  {
  char i;
  DDRB = 255;		// Data Direction Register for port B
DDRD=255;
TCCR2 = 105;
TCCR0 = 105;
TCCR1A=131;
TCCR1B=1;

OCR1AH=255;OCR1AL=255;
OCR0=255;OCR2=255;

PORTB=255;PORTD=255;
delay_ms(1500);
PORTB=0;PORTD=0;

delay_ms_spl(100);

while(1){
	blinkforward();  
	blinkreverse();  

}
return 0;
}
