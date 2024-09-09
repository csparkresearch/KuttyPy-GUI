
#include <avr/kp.h>

int main()
{
lcd_init();
lcd_put_string("A ");
lcd_put_float(45.3, 1);
lcd_put_char(' ');
lcd_put_byte(255);
lcd_put_char(' ');
lcd_put_int(65534);
lcd_put_char(' ');
lcd_put_long(100000);
}