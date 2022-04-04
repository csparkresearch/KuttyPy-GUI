#include <avr/io.h>
           .section .text    ; code section starts
disp:                             ; our  subroutine
           STS    PORTB, R1     ; display R1 on port B
           INC    R1                      ; increments it
           RET                                ; and return

           .global main
main:
           LDI         R16, 255
           STS        DDRB, R16
           MOV     R1, R16
loop:
           RCALL  disp          ; relative call
           CALL    disp           ; direct call
           RJMP    loop
           .end