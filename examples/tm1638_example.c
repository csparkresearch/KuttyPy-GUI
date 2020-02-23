// adapted for atmega32 from https://github.com/moozzyk/TM1638/blob/master/TM1638_demo/TM1638_demo.ino
//

#include "mh-utils.c"

#define COUNTING_MODE 0
#define SCROLL_MODE 1
#define BUTTON_MODE 2

#define PIN_STROBE 2
#define STROBE1             PORTB |= (1<<PIN_STROBE)
#define STROBE0             PORTB &= ~(1<<PIN_STROBE)

#define PIN_CLK 1
#define CLK1             PORTB |= (1<<PIN_CLK)
#define CLK0             PORTB &= ~(1<<PIN_CLK)

#define PIN_DATA 0
#define DATA1             PORTB |= (1<<PIN_DATA)
#define DATA0             PORTB &= ~(1<<PIN_DATA)

#define DATAOUT             DDRB |= (1<<PIN_DATA)
#define DATAIN             DDRB &= ~(1<<PIN_DATA)


uint8_t shiftIn(void)
{
    uint8_t i,val=0;

    for (i = 0; i < 8; i++)  {
        CLK1;
        asm("nop");asm("nop");asm("nop");
        CLK0;        
	asm("nop");asm("nop");
    	val<<=1;
    	if(PINB & (1 << PIN_DATA) ) val|=1;

    }
    return val;
}

void shiftOut(uint8_t val)
{
    uint8_t i;

    for (i = 0; i < 8; i++)  {
    	if(val & (1 << i))DATA1;
    	else DATA0;
	asm("nop");asm("nop");
        CLK1;asm("nop");asm("nop");asm("nop");
        CLK0;        
    }
}

void sendCommand(uint8_t value)
{
  STROBE0;
  shiftOut( value);
  STROBE1;
}

void reset()
{
  sendCommand(0x40); // set auto increment mode
  STROBE0;
  shiftOut( 0xc0);   // set starting address to 0
  for(uint8_t i = 0; i < 16; i++)
  {
    shiftOut( 0x00);
  }
  STROBE1;
}

void setup()
{
  DDRB = (1<<PIN_STROBE)|(1<<PIN_CLK)|(1<<PIN_DATA);

  sendCommand(0x8f);  // activate
  reset();
}




uint8_t counting()
{
                       /*0*/ /*1*/ /*2*/ /*3*/ /*4*/ /*5*/ /*6*/ /*7*/ /*8*/ /*9*/
  uint8_t digits[] = { 0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f };

  static uint8_t digit = 0;

  sendCommand(0x40);
  STROBE0;
  shiftOut( 0xc0);
  for(uint8_t position = 0; position < 8; position++)
  {
    shiftOut( digits[digit]);
    shiftOut( 0x00);
  }

  STROBE1;

  digit = ++digit % 10;
  return digit == 0;
}

uint8_t scroll()
{
  uint8_t scrollText[] =
  {
    /* */ /* */ /* */ /* */ /* */ /* */ /* */ /* */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    /*H*/ /*E*/ /*L*/ /*L*/ /*O*/ /*.*/ /*.*/ /*.*/
    0x76, 0x79, 0x38, 0x38, 0x3f, 0x80, 0x80, 0x80,
    /* */ /* */ /* */ /* */ /* */ /* */ /* */ /* */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    /*H*/ /*E*/ /*L*/ /*L*/ /*O*/ /*.*/ /*.*/ /*.*/
    0x76, 0x79, 0x38, 0x38, 0x3f, 0x80, 0x80, 0x80,
  };

  static uint8_t index = 0;
  uint8_t scrollLength = sizeof(scrollText);

  sendCommand(0x40);
  STROBE0;
  shiftOut( 0xc0);

  for(int i = 0; i < 8; i++)
  {
    uint8_t c = scrollText[(index + i) % scrollLength];

    shiftOut( c);
    shiftOut( c != 0 ? 1 : 0);
  }

  STROBE1;

  index = ++index % (scrollLength << 1);

  return index == 0;
}

uint8_t readButtons(void)
{
  uint8_t buttons = 0;
  STROBE0;
  shiftOut( 0x42);

  DATAIN;

  for (uint8_t i = 0; i < 4; i++)
  {
    uint8_t v = shiftIn() << i;
    buttons |= v;
  }

  DATAOUT;
  STROBE1;
  return buttons;
}

void setLed(uint8_t value, uint8_t position)
{
  DATAOUT;

  sendCommand(0x44);
  STROBE0;
  shiftOut( 0xC1 + (position << 1));
  shiftOut( value);
  STROBE1;
}

void buttons()
{
  uint8_t promptText[] =
  {
    /*P*/ /*r*/ /*E*/ /*S*/ /*S*/ /* */ /* */ /* */
    0x73, 0x50, 0x79, 0x6d, 0x6d, 0x00, 0x00, 0x00,
    /* */ /* */ /* */ /* */ /* */ /* */ /* */ /* */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    /*b*/ /*u*/ /*t*/ /*t*/ /*o*/ /*n*/ /*S*/ /* */
    0x7c, 0x1c, 0x78, 0x78, 0x5c, 0x54, 0x6d, 0x00,
    /* */ /* */ /* */ /* */ /* */ /* */ /* */ /* */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  };

  static uint8_t block = 0;

  uint8_t textStartPos = (block / 4) << 3;
  for(uint8_t position = 0; position < 8; position++)
  {
    sendCommand(0x44);
    STROBE0;
    shiftOut( 0xC0 + (position << 1));
    shiftOut( promptText[textStartPos + position]);
    STROBE1;
  }

  block = (block + 1) % 16;

  uint8_t buttons = readButtons();

  for(uint8_t position = 0; position < 8; position++)
  {
    uint8_t mask = 0x1 << position;
	
    setLed(buttons & mask ? 1 : 0, position);
  }
}


void main()
{
static uint8_t mode = COUNTING_MODE;
setup();
//for(;;){buttons();delay_ms(100);}
	for(;;){

		switch(mode)
		{
		case COUNTING_MODE:
		mode += counting();
		break;
		case SCROLL_MODE:
		mode += scroll();
		break;
		case BUTTON_MODE:
		buttons();
		break;
		}

		delay_ms(100);
	}
}



