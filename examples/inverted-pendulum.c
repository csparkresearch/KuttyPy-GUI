// Inverted pendulum control

#include "mh-uart.c"
#include "mh-adc.c"
#include "mh-utils.c"

void pushcw(int);
void pushcw(int);
void oscillate();
void feedback_loop();

main()
{

adc_enable();
DDRC=255;

while(1){
	oscillate();
	feedback_loop();
	PORTB=255;
PORTC=127>>1;
	delay_ms(1500);
}

}

//ADC
// Center is 250
// Max is 540. Strange 280 present between 540 and 0


void oscillate(){
	int direction=0;
	int lastval;
	int data;
		data = read_adc(0);
lastval = read_adc(0);
	uart_send_string("swing\n");
	pushcw(100);direction=1; // 1=clockwise, 0 = counterclockwise 
	while(1){
		data = read_adc(0);
 // When the motor spins clockwise, the bob goes the other way(ADC >0 , <280)
		if(direction==1 && data>0 && data<250 && data<lastval-5){
	uart_send_string("swing CW\n");

pushccw(10);direction=0; lastval=data;//the bob is returning from a clockwise push. counter clockwise push
}
else if(direction==0 && data<540 && data>270){ // bob is returning from a counter clockwise push.
	uart_send_string("swing CCW\n");

pushcw(10);direction=1;lastval=data;
}else{

if(direction==1){ // clockwise push was given. data will be rising from 0 to 150
   if(data>lastval)lastval=data;
}else if(direction==0){ // ccw push. data falling from 540 to 270
}
 if(data<lastval)lastval =data;

}


		if(data>250 && data<270){//abort . within range
			PORTC = 127>>1; // Set to 0 Volts
			uart_send_string("at the top\n\n");
			break;
		}
	}
	return;
}

void pushccw(int d){
	PORTC=127 ; // PUSH CW
	delay_ms(d);
	PORTC=127>>1; // STOP
}
void pushcw(int d){
	PORTC=0 ; // PUSH CW
	delay_ms(d);
	PORTC=127>>1; // STOP
}


void feedback_loop(){
	int data, integral=0,distance=0,direction=0;
	int x=127;
	uint8_t cnt=0,MID=129;
	char buffer[20];
	uart_init(38400);
	DDRB=255; // For LED array display
	uart_send_string("start\n");
	while(1){
		data = read_adc(0);
		if(data>280 || data<220){//abort
			PORTC = 127>>1; // Set to 0 Volts
			uart_send_string("lost balance\n");
			break;
		}else{			
			x = 255 - (data>>1); // X is 104 to 380. center 250

			if(x<MID){
				x-=50;x-=distance/10;
				if(x<0)x=0;
				if(direction==0)
					distance++;
				else{
					distance=0; // Direction changed. reset distance variable
					direction=0;
				}
			} // Compensation
			else if(x>MID){
				x+=50;x+=distance/10;

				if(x>255)x=255;
				if(direction==1)
					distance++;
				else{
					distance=0; // Direction changed. reset distance variable	
					direction=1;
				}	
			}
			
			if(distance>1000){
				PORTC=127>>1;
				uart_send_string("continuous\n");
				break;//continuous rotation			
			}

			x>>=1; // Convert 0-255 to 0-127 [0-5V to 0-2.5V]


		}

		PORTB = (1<<(x>>4)); // indicator
		PORTC = x;	// Only 0-2.5 on level shifter		
		//utoa(data,buffer,10); //10 means decimal.
		// Send in plain text. digit by digit, followed by newline character.
		//for(cnt = 0;buffer[cnt]!='\0';cnt++){
		//	uart_send_byte(buffer[cnt]);
		//	if(cnt>10)break;
		//}
		uart_send_byte('\n');
		delay_us(100);	
		//delay_ms(1000);			
	}
return;
}
