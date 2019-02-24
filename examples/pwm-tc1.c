#include "mh-timer.c"
#include "mh-adc.c"
#include "mh-utils.c"

uint8_t  csb = 1;         // 2 is divide by 8 option, 1MHz clock in
uint16_t  ocra = 1024/3;  // around 33% duty cycle set

 
int main()
{
pwm10_tc1(csb, ocra);     // Generates 10 bit PWM on OC1A (PD5)
}
