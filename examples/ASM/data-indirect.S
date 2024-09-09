
ddrb = 0x17 
portb = 0x18

.section .data  
var1:

.section .text    ; denotes code section
.global main
main: 	
   LDI R16, 0xff   ; load r16 with 255
   OUT ddrb, R16   ; make all bits of port B as output

   LDI  R17, 0b10101010       ; set r17 to 10101010b
   STS  var1, R17             ; store it to RAM at var1
   LDI  R26, lo8(var1)        ; R26 and R27 forms X, the 16 bit address
   LDI  R27, hi8(var1)        
   LD   R16, X                ; Load R16 from location pointed to by X

   OUT portb, R16             ; display R16 contents
.end
