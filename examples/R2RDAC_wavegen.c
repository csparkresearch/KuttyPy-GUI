#include "mh-utils.c"

//DAC table for 8 bit dac. PORTC only has a 6 bit configuration(PC0,PC1 are reserved)
// for I2C comms. so 2 lsb will be discarded.
// You can monitor the output of this sine wave on an oscilloscope or ExpEYES/SEELab devices
uint16_t table[] = {127,130,133,136,140,143,146,149,152,155,158,161,164,167,170,173,176,179,182,185,188,190,193,196,198,201,203,206,208,211,213,215,218,220,222,224,226,228,230,232,234,235,237,238,240,241,243,244,245,246,247,248,249,250,251,252,252,253,253,254,254,254,254,254,254,254,254,254,254,253,253,252,252,251,250,249,248,247,246,245,244,243,241,240,238,237,235,234,232,230,228,226,224,222,220,218,215,213,211,208,206,203,201,198,196,193,190,188,185,182,179,176,173,170,167,164,161,158,155,152,149,146,143,140,136,133,130,127,124,121,118,114,111,108,105,102,99,96,93,90,87,84,81,78,75,72,69,66,64,61,58,56,53,51,48,46,43,41,39,36,34,32,30,28,26,24,22,20,19,17,16,14,13,11,10,9,8,7,6,5,4,3,2,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,2,3,4,5,6,7,8,9,10,11,13,14,16,17,19,20,22,24,26,28,30,32,34,36,39,41,43,46,48,51,53,56,58,61,64,66,69,72,75,78,81,84,87,90,93,96,99,102,105,108,111,114,118,121,124,127};


int main (void)
  {
  uint16_t value=0,position = 0;
  DDRC = 255;		// Data Direction Register for port B

  for(;;)
    {
    value = table[position++];
    if(position==255){position=0;}
    /* WRITE VALUE TO DAC PORTC which should have a R2R DAC ladder*/
    PORTC=value;
  }
return 0;
}
