#include <avr/io.h>
      .section .text    ; denotes code section
      .global main
main:
     LDI     R16, 255        
     STS    DDRB, R16    ; All bits of port B as output
     STS    DDRA, R16    ; All bits of port A as output
     LDI    R17, 3             ; load R17 with 1
     ADD  R16,  R17        ; R16 <- R16 + r17
     STS    PORTB, R16  ; Sum to port B
     LDS   R16, SREG      ; Load the Status register
     STS    PORTA, R16  ; display it on port A
     .END
