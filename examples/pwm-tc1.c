#include "mh-utils.c"
 
int main()
{
DDRD = 128;
TCCR2 = 109; //100uS pulse every 5mS
OCR2 = 4;
for(;;);
}
