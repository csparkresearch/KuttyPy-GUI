
#include <avr/io.h>      

.section .text    ; denotes code section
.global main
main:
    LDI R16, 255      
    STS DDRB, R16

    ;JMP skip
    LDI R16, 15
skip: 
    STS PORTB, R16
.end
