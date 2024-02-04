#include "mh-lcd.c"
#include "mh-uart.c"

int main(void)
{
uint8_t data;
DDRB=255;
//lcd_init();
uart_init(38400);

for(;;)
  {
    data = uart_recv_byte();
    PORTB=data;
    uart_send_byte(data+1);
  }
}
