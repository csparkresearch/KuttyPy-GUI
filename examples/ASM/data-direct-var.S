
ddrb = 0x17 
portb = 0x18

.section .data  
var1:

.section .text    ; denotes code section

.global main 

main: 
   LDI R16, 0xff   ; load r16 with 255
   OUT ddrb, R16   ; make all bits of port B as output

   LDI R16, 15     ; load R16 with a number 
   STS var1, R16   ; Store R16 to location var1
   LDS R17, var1   ; Load R17 from var1

   OUT portb, R17  ; display R17 contents

.end
