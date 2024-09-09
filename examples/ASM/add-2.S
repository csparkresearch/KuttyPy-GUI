; program add.S

DDRB  = 0x37      ; memory mapped address of DDRB, use STS instruction
PORTB = 0x38

.section .text    ; denotes code section
.global main
main:  
     LDI    R16, 255     ; load R16 with 255
     STS    DDRB, R16    ; set all bits of port B as output

     LDI    R16,  1     ;  load R16 with 11
     LDI    R17,  4      ;  load R17 with 4
     ADD    R16, R17    ;  R16 <- R16 + R17


     STS    PORTB, R16    ; result to port B, 4 LSBs should be on
.END
