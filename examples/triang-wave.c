// Generates a 
#include "mh-utils.c"

int main (void)
{
DDRB = 255;		// Data Direction Register for port B
uint16_t k;

while(1)
	{
    k = 0;
    while(k < 256) PORTB = k++;
    --k;
    while(k >0) PORTB = k--;
    }
}
