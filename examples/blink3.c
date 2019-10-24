#include "mh-uart.c"

int main (void)
  {
	uart_init(57600);
	while(1){
	    	uart_send_byte('a');
		}
	return 0;
}
