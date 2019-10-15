#include "mh-utils.c"

uint16_t table[] = {2047,2148,2249,2350,2450,2548,2646,2742,2836,2929,3019,3107,3192,3275,3354,3431,3504,3573,
3639,3700,3758,3812,3861,3906,3946,3981,4012,4038,4059,4076,4087,4093,4094,4091,4082,4068,4049,4026,3997,3964,
3926,3884,3837,3785,3730,3670,3606,3539,3468,3393,3315,3234,3150,3063,2974,2883,2789,2694,2597,2499,2400,2300,
2199,2098,1996,1895,1794,1694,1595,1497,1400,1305,1211,1120,1031,944,860,779,701,626,555,488,424,364,309,257,
210,168,130,97,68,45,26,12,3,0,1,7,18,35,56,82,113,148,188,233,282,336,394,455,521,590,663,740,819,902,987,1075,
1165,1258,1352,1448,1546,1644,1744,1845,1946,2047};



int main (void)
  {
  uint16_t timeout,value=0,position = 0;
  DDRB = 255;		// Data Direction Register for port B
TWSR=0x00; TWBR=0x46 ; TWCR=0x04; //Init I2C
PORTC = 3; //Enable SCL/SDA Pull up	


  for(;;)
    {
    value = table[position++];
    if(position==128){position=0;}
/* WRITE VALUE TO DAC */
timeout = 10000;
//Send ADDRESS
TWCR = 0xA4;                                                // send a start bit on i2c bus
while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
TWDR = 0x60<<1;                                             // load address of i2c device
TWCR = 0x84;                                                // transmit
while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit


//Send Register to write to
TWDR = 0x40;
TWCR = 0x84;                                                // transmit
while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit



//Data MSB
TWDR = (value>>4)&0xFF;
TWCR = 0x84;                                                // transmit
while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit

//DATA LSB
TWDR = (value&0xF)<<4;
TWCR = 0x84;                                                // transmit
while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit



//STOP
TWCR = 0x94;                                                // stop bit



  }
return 0;
}
