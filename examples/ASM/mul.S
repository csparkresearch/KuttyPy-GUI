; program mul.S
; Load 2 registers with some values and multiply them. Display result on port B

#include <avr/io.h>

      .section .text    ; denotes code section
      .global main
main:  
     LDI    R16, 255    ; load R16 with 255
     STS    DDRB, R16    ; set all bits of port B as output

     LDI    R16,  4     ; load R16 with 2
     LDI    R17,  3      ; load R17 with 4
     MUL    R16, R17    ; R16 <- R16 + R17

     STS    PORTB, R0   ; MUL result low byte is put in R0

   .END
