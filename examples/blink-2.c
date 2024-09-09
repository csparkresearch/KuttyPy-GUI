#include <avr/io.h>   // Include file for I/O operations

extern void delay_ms (uint16_t k);

int main (void)
{
DDRB = 255;             // Configure port B as output  

while (1)
    {
     PORTB = 255;
     delay_ms(200);
     PORTB = 0;
     delay_ms(200);
    }

}
