#include <avr/io.h>
      .section .text    ; denotes code section
      .global main
main:
    LDI     R16, 255        
    STS    DDRB, R16    ; set all bits of port B as output
    LDI     R16, 2        
     LDI    R17, 4       ; load R17 with 4
    SUB   R16,  R17
     LDS   R16, SREG
     STS    PORTB, R16
     .END
