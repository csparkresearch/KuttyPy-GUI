; program add.S
; No Output visible


      .section .text  		  ; denotes code section
      .global main

main:  
     LDI    R16,  4     ; load R16 with 2
     LDI    R17,  3      ; load R17 with 4
     ADD  R16, r17    ; R16 <- R16 + R17
     .END
