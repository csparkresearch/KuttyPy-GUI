#include  "mh-utils.c"

int main (void)
  {
  DDRA = 15;	              	// Data Direction Register for port A

PORTA = 1+4;                            // Power in one direction
delay_ms(100);

 PORTA = 0;                            // OFF
delay_ms(1000);

PORTA = 2+8;                            // other direction
delay_ms(100);

 PORTA = 0;                            // OFF
}
