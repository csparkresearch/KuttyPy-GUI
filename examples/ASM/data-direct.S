
ddrb = 0x17       ; I/O mapped address of register DDRB
portb = 0x18
PORTA = 0x3b      ; memory mapped address of PORTA

.section .text    ; denotes code section
.global main
main: 	
   LDI    R16, 0xff           ; load r16 with 255
   OUT ddrb, R16              ; set port B as output 

   STS PORTA, R16   ; Store R16 to the memory location PORTA
   LDS R17, PORTA    ; read it back to R17
   OUT portb, R17   ; display it on port B LEDs     
.end