#include "mh-utils.c"
 
int main()
{
DDRD = 48; // PD4, PD5 output
TCCR1A = 179;
TCCR1B=1;

OCR1BH=1;
OCR1BL=255;

OCR1AH=1;
OCR1AL=255;

for(;;);
}
