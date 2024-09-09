#include <avr/kp.h> 


int main(void) 
{ 
uint8_t data;

DDRB = 255;
PORTB = 15;
uart_init(38400);

for(;;)   
     {
      data = uart_recv_byte();
      PORTB = data;
      uart_send_byte(data + 1);
     }
} 
