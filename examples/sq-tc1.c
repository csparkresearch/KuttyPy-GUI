#include <avr/kp.h>


uint8_t csb = 2;           // Clock select bits 
uint16_t ocra = 50000;    // Output Compare register vaule

int main() 
{ 
sqwave_tc1(csb, ocra);
}