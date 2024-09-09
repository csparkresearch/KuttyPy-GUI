#include <avr/io.h>   // Include file for I/O operations
#include <stdlib.h>

extern uint32_t measure_freq(void);

extern void uart_init(uint16_t baud);
extern void uart_send_byte(uint8_t c);
extern void delay_ms (uint16_t k);

int main (void)
{
uint16_t data;
char a[6], *p;

DDRB = 255;             // Configure port B as output  
uart_init(38400);

while (1)
    {
     data =  measure_freq();
     PORTB = data >> 2;    // convert 10 bit in to 8 bit
     utoa(data, a, 10);    // convert to ASCII string
     p = a;
     while(*p) uart_send_byte(*p++);
     uart_send_byte('\n');
     delay_ms(500);
    }
}
