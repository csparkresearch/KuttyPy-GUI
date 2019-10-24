#include "mh-utils.c"

void showchar(uint8_t c[]){
  uint8_t x;
  for(x=0;x<8;x++)
   {
   PORTB=c[x];
   delay_100us(3);
   }
  PORTB=0;
  delay_ms(1);
}
 

main(){
  uint8_t ca[]={128+64,64+32+16,16+8+4,19,19,16+8+4,16+32+64,128+64};
  uint8_t ch[]={255,255,24,24,24,24,255,255};
  uint8_t ci[]={0,0,129,255,255,129,0,0};
  uint8_t cj[]={128+64+1,128+1,128+1,128+1,255,1,1,1};
  uint8_t ck[]={255,24,36,102,66,128,128,0};
  uint8_t cn[]={255,3,14,24,16+32,64+32,64+128,255};
  uint8_t cs[]={134,137,137,137,137,137,137,97};
  uint8_t ct[]={1,1,1,255,255,1,1,1};
  uint8_t cv[]={1+2,2+4+8,16+8+4,19,19,16+8+4,2+4+8,1+64};
  
  uint8_t x;
  
  DDRB=255;
 
  for(;;){
        delay_ms(2);
        showchar(ch);
        showchar(ca);
        showchar(ci);
        delay_ms(8);
  }
}
