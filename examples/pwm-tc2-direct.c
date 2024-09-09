// example : pwm-tc2-direct.c

#include <avr/io.h>

uint8_t csb = 2;              // Clock select bits uint8_t 
uint8_t ocrval = 255/4;      // Output Compare register vaule

int main() 
{ 
// Set TCCR2 in the Fast PWM mode 
TCCR2 =(1 << WGM21) | (1 << WGM20) | (1 << COM21) | csb; 
OCR2 = ocrval; 
TCNT0 = 0; 
DDRD |= (1 << PD7); // Set PD7(OC2) as output 
}