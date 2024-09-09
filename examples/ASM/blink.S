
#include <avr/io.h>

.section .text    ; denotes code section
.global main 
main:      

LDI R16, 255
STS DDRB, R16

LDI R16, 1

lab:
      ; send some output
    STS PORTB, R16
    ROR R16
    CALL DEL

    jmp lab

DEL:              ; delay loop
   LDI R22, 100 
L1:  
   LDI R21, 100 
L2:  
   LDI R20, 100 
L3:  
   DEC R20      
   BRNE L3
   DEC R21
   BRNE L2
   DEC R22
   BRNE L1
   RET
.end