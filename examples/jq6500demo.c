/*
Author : Jithin B P, IISER Mohali, jithinbp@gmail.com
License : GPL v3

TSOP4838 IR REceiver connections:
----- PD2
----- blank space
----- 5V
----- GND

JQ6500 Connections
PD3 receives data. Connect TX of JQ6500 to PD3
PD4 transmits. Connect PD4 to RX of JQ6500;

remote notes : SAMSUNG AC remote is 8 bytes
normal cheap 20rs remote is 3 bytes with an extra start bit after that followed by a single bit. No idea why.
coded fr cheap remote. No address checking. 

AED Trainer protoype code.

*/


#include <avr/io.h>
#include <stdlib.h>

#include "mh-utils.c"
#include "mh-uart.c"
#include "mh-soft-uart.c"

#define MP3_EQ_NORMAL     0
#define MP3_EQ_POP        1
#define MP3_EQ_ROCK       2
#define MP3_EQ_JAZZ       3
#define MP3_EQ_CLASSIC    4
#define MP3_EQ_BASS       5

#define MP3_SRC_BUILTIN   4
#define MP3_STATUS_STOPPED 0
#define MP3_STATUS_PLAYING 1
#define MP3_STATUS_PAUSED  2

#define MP3_LOOP_ALL      0
#define MP3_LOOP_FOLDER   1
#define MP3_LOOP_ONE      2
#define MP3_LOOP_RAM      3
#define MP3_LOOP_ONE_STOP 4
#define MP3_LOOP_NONE     4 

#define MP3_STATUS_STOPPED 0
#define MP3_STATUS_PLAYING 1
#define MP3_STATUS_PAUSED  2

#define MP3_CMD_BEGIN 0x7E
#define MP3_CMD_END   0xEF
    
#define MP3_CMD_PLAY 0x0D
#define MP3_CMD_PAUSE 0x0E
#define MP3_CMD_NEXT 0x01
#define MP3_CMD_PREV 0x02
#define MP3_CMD_PLAY_IDX 0x03
    
#define MP3_CMD_NEXT_FOLDER 0x0F
#define MP3_CMD_PREV_FOLDER 0x0F
#define MP3_CMD_PLAY_FILE_FOLDER 0x12
    
#define MP3_CMD_VOL_UP 0x04
#define MP3_CMD_VOL_DN 0x05
#define MP3_CMD_VOL_SET 0x06
    
#define MP3_CMD_EQ_SET 0x07
#define MP3_CMD_LOOP_SET 0x11    
#define MP3_CMD_SOURCE_SET 0x09
#define MP3_CMD_SLEEP 0x0A
#define MP3_CMD_RESET 0x0C
    
#define MP3_CMD_STATUS 0x42
#define MP3_CMD_VOL_GET 0x43
#define MP3_CMD_EQ_GET 0x44
#define MP3_CMD_LOOP_GET 0x45
#define MP3_CMD_VER_GET 0x46
    
#define MP3_CMD_COUNT_SD 0x47
#define MP3_CMD_COUNT_MEM 0x49
#define MP3_CMD_COUNT_FOLDERS 0x53
#define MP3_CMD_CURRENT_FILE_IDX_SD 0x4B
#define MP3_CMD_CURRENT_FILE_IDX_MEM 0x4D
    
#define MP3_CMD_CURRENT_FILE_POS_SEC 0x50
#define MP3_CMD_CURRENT_FILE_LEN_SEC 0x51
#define MP3_CMD_CURRENT_FILE_NAME 0x52

#define CPU_CLOCK	8000000		// 8 MHz clock is assumed
#define COMPUTE_BAUD(b) ((uint32_t)(CPU_CLOCK)/((uint32_t)(b)*16) - 1)

// IR remote with TSOP receiver
#define RXIR PD2
#define   NBYTES   3               // 3 for TV remotes.


void uart_send_bytes(uint8_t *s,char len){
	for(int x =0 ;x<len;x++){
		uart_write(*(s++));
	}
}

int waitUntilAvailable(unsigned int k)
{
while( !uart_rxdata() && k ){k--;delay_ms(1);}
if (uart_rxdata()) {return uart_read();}
else {return 0; }
}

//REMOTE REceive INTERRUP SERVICE ROUTINE
volatile uint8_t value=0,rb=0;
ISR(INT0_vect)		// interrupt triggered on a falling edge on PD2
{
uint16_t time;
time=TCNT1;
TCNT1=0;		

if(time>10000)		// Detected start pulse > 10 msec   ~13.5ms
		{
		rb=0;		//Set bit count to zero
		value=0;		//set receive buffer to zero
		
		return;
		}
else				
	rb+=1;			//increment bit count in case of short pulses

if(time >2000 && time < 2800)		// A binary 1 lies in this time interval of low pulse
	value = (value<<1)|1;
if(time>900 && time < 1500) // A binary zero has around this length acc. to protocol
	value = (value<<1);

if(rb==NBYTES*8) // Recived 1 byte. Display it on PORTB LEDs
	{
	//lcd_clear();
	//lcd_put_byte(val);
	PORTB = value;playTrack(value);
	}
}



void playTrack(uint8_t val){

	 switch(val){
		case 1:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 1 ,  MP3_CMD_END},6 );
		break;
		case 2:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 2 ,  MP3_CMD_END},6 );
		break;
		case 4:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 3 ,  MP3_CMD_END},6 );
		break;
		case 8:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 4 ,  MP3_CMD_END},6 );
		break;
		case 16:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 5 ,  MP3_CMD_END},6 );
		break;


		case 128:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,2, MP3_CMD_VOL_DN ,  MP3_CMD_END},4 );
			uart_send_string("Volume Down!\n");
			delay_ms(100); 
			waitUntilAvailable(100);
		break;

		case 64:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,2, MP3_CMD_VOL_UP ,  MP3_CMD_END},4 );
			uart_send_string("Volume UP!\n");
			delay_ms(100); 
			waitUntilAvailable(100);
		break;


		case 32: //remote R
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 1 ,  MP3_CMD_END},6 );
		break;
		case 128+32: //remote G
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 2 ,  MP3_CMD_END},6 );
		break;
		case 32+64: //remote B
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 3 ,  MP3_CMD_END},6 );
		break;
		case 32+64+128: //remote W
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 4 ,  MP3_CMD_END},6 );
		break;
		case 64+128: //remote ON
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,4, MP3_CMD_PLAY_IDX,  0, 5 ,  MP3_CMD_END},6 );
		uart_send_string("Music (Remote)!\n");
		break;


		case 8+32:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,2, MP3_CMD_VOL_DN ,  MP3_CMD_END},4 );
			uart_send_string("Volume Down (Remote)!\n");
		break;

		case 8+32+128:
			uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,2, MP3_CMD_VOL_UP ,  MP3_CMD_END},4 );
			uart_send_string("Volume UP(remote)!\n");
		break;


		}

		waitUntilAvailable(100);


}

int main()
{
uint8_t val=0,x=0;
DDRB = 255; //RED LED output
DDRA=0; PORTA=255; DDRD=0;
uart_init(38400); //USB UART
enable_uart(9600); // soft uart to music IC

// IR RECEIVE
PORTD |= (1 <<  RXIR);         // Enable  pullup on PD2 (INT0 pin) receive pin
MCUCR |= (1<<ISC01);		  // Falling edge on INT0
GICR |= (1<<INT0);		          // Enable INT0
TCCR1B = (1<<CS01);		// Set TC1 to 1MHz. Divide 8MHz clock by 8. timer initialized!!
TCNT1=0;
sei();


waitUntilAvailable(10);
uart_send_string("initialized\n");

uart_send_string("resetting...");
uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,2, MP3_CMD_RESET,   MP3_CMD_END},4);
delay_ms(500); 
waitUntilAvailable(100);
uart_send_string("RESET!\n");

uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,3, MP3_CMD_VOL_SET, 30,  MP3_CMD_END},5);
waitUntilAvailable(100);

//disable looping // 0x7e,len(cmd+args+terminator. typically 2 with no arg), cmd, args, termin 
//uart_send_bytes((uint8_t []) {MP3_CMD_BEGIN,3, MP3_CMD_LOOP_SET,  MP3_LOOP_NONE,  MP3_CMD_END},5); 
//uart_send_string("looping disabled.\n");
//waitUntilAvailable(100);


while(1){
	val=PINA^255;
	if(val){
	PORTB = val; 
	playTrack(val);
	}
}

}


