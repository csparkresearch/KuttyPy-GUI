#include <avr/kp.h>

 
uint8_t csb = 2;           // Clock select bits 
uint16_t ocra = 63;       // Output Compare register vaule

int main() 
{ 
pwm10_tc1(csb, ocra);
}