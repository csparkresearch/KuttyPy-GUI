#include <avr/io.h>

     .global main
main:
     LDI r16, 255      ; load r16 with 255
     STS DDRB, r16   
   
          
     LDI R16, 0
     LDI R17, 253
     STS  PORTB, R17 

loop:
     ;STS  PORTB, R16  ; display it on port A
     
     
     ;STS  PORTB, R17  ; display it on port A
     
     RJMP loop
