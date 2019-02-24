// Generates a RAMP on the R-2R DAC connected to port B
#include "mh-utils.c"

int main (void)
{
uint16_t k;
DDRB = 255;		// Data Direction Register for port B

while(1) for (k=0; k <= 255; ++k)  PORTB = k;
}
