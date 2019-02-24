// Reads ADC channel 0 and diplays the result on the LCD 

#include "mh-lcd-float.c"
#include "mh-adc.c"
#include "mh-utils.c"

int main()
{
uint16_t data;
double   v;

lcd_init();
adc_enable();
while(1)
    {
    data = read_adc(0);   // Read voltage at PA0
    v = 5.0/1023 * data;
    lcd_clear();
    lcd_put_float(v, 3);
    delay_ms(500);
    }
}
