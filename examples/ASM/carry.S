
#include <avr/io.h>
      .section .text    ; denotes code section
      .global main
main:
     LDI    R16, 255     
     STS    DDRB, R16    ; All bits of port B as output
     STS    DDRD, R16    ; All bits of port D as output

     LDI    R16, 255      ; load R16 and R17 with  some values
     LDI    R17,  0     
     ADD    R16,  R17    ; R16 <- R16 + r17
     
     STS    PORTB, R16   ; Sum to port B

     LDS    R16, SREG    ; Load the Status register
     STS    PORTD, R16   ; display it on port D
.END
