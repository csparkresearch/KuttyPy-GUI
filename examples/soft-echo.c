/*
 Testing of the soft-serial functions makes PD2 and PD3 as Rx and Tx
 Waits for a byte on PD2, the soft serial Rx and sends it back on PD3, the soft serial Tx
*/

#include "mh-soft-uart.c"
#include "mh-lcd.c"

int main()
{
  uint8_t x=0;

  lcd_init();
  enable_uart(9600); // 2400,4800, 9600 & 19200 allowed

  for(;;)
	{
	 while( !ubcount) ;  // wait for Rx data
	x = uart_read();
	lcd_put_char(x);
	uart_write(x);
	} 
}
