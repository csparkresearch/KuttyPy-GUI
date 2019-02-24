#include "mh-timer.c"
#include "mh-utils.c"

uint8_t  csb = 1;            // Clock select bits
uint8_t  ocrval = 63;   // Output Compare register  OCR0 , decides duty cycle

int main()
{
pwm_tc0(csb, ocrval);    // 25% duty cycle PWM output on pin PB3 (OC0)
}
