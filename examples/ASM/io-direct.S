; program io-direct.S to demonstrate direct I/O addressing

.section .text    ; denotes code section         
.global main                           
main: 	
   LDI R16, 255      
   LDI R17, 0b10101010      
   OUT 0x17, R16        ; I/O address of DDRB is 0x17
   OUT 0x18, R17         ; PORTB is at 0x18, alternate LEDs should glow
.end