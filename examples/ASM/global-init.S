
ddrb = 0x17  
portb = 0x18 
ddrd = 0x11
portd = 0x12 


.section .text    ; denotes code section
  .global __do_clear_bss  ; and setup stack pointer

  .global main
  main: 	
     LDI R16, 0xff        ; load r16 with 255    
     OUT ddrb, R16        ; make all bits of port B as output 
     OUT ddrd, R16        ; make all bits of port D as output

     LDI R16, 1           
     PUSH R16             ; push R16 content to the stack
     INC R16
     PUSH R16             ; push the incremented value
     POP R17              ; should pop the last pushed value
     POP R18              ; shoul pop the previous

     OUT portb, R17       ; display on port B
     OUT portd, R18       ; display on port D
.end