#include <avr/io.h>

int main (void)
  {
  DDRD = 128;//PD7 is output.
  TCCR2 = 105;
  TCNT2 = 0;
  OCR2 = 10;
return 0;
}
