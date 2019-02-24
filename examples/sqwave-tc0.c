// Generates a squarewave on PB3 using Timer/Counter0
#include "mh-timer.c"

uint8_t csb = 2;       // Clock select bits
uint8_t ocrval = 99;   // Output Compare register vaule

int main()
{
sqwave_tc0(csb, ocrval);  // Output on PB3, 5kHz
return 0;
}
