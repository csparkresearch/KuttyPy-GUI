#include <avr/kp.h>

//extern void uart_init(uint16_t baud); 
//extern void uart_send_byte(uint8_t c);

int main (void) 
  { 
  uint8_t data = 'A';

  uart_init(38400);

  while(data <= 'z') uart_send_byte(data++); 
}