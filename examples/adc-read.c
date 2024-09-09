#include <avr/kp.h>   // Include file for I/O operations
#include <stdlib.h>   // include the utoa() function prototype


int main (void)
{
uint16_t data;
char a[6], *p;

DDRB = 255;             // Configure port B as output  
adc_enable();
uart_init(38400);

while (1)
    {
     data = read_adc(0);
     PORTB = data >> 2;    // convert 10 bit in to 8 bit
     utoa(data, a, 10);    // convert to ASCII string
     p = a;
     while(*p) uart_send_byte(*p++);
     uart_send_byte('\n');
     delay_ms(500);
    }
}
