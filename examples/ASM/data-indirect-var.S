#include <avr/io.h>
           .section .data    ; data section starts here
var1:  
            .byte  0xEE         ; initialized global variable var1

           .section .text    ; code section
           .global    __do_copy_data    ; initialize global variables
           .global     __do_clear_bss     ; and setup stack pointer
           .global main
main:
           LDS  R1, var1                  ; load R1 using data direct mode
	   STS   DDRA, R1               ; display R1 on port A
           STS   PORTA, R1
           LDI   R26, lo8(var1)        ; load the lower and
           LDI   R27, hi8(var1)        ; higher bytes of the address of var1 to X
           LD    R16, X                           ; Load R16 using data-indirect mode,  data from where X is pointing to
	   STS   DDRB, R16               ; display R16 on port B
           STS   PORTB, R16
   .end