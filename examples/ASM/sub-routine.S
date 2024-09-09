
#include <avr/io.h>


.section .text    ; denotes code section
.global main
  
disp:  	               ; subroutine 
    STS PORTB, R17       ; send R1 PORTB 
    RET

.global main                           
main:
     LDI  R16, 255
     STS  DDRB, R16     ; DDRB 

     LDI R17, 3              

     RCALL disp        ; relative call
     CALL  disp    ; direct call
.end
