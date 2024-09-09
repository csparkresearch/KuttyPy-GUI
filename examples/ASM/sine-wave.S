; generates sine wave on the R-2R DAC connected on port C

#include <avr/io.h>

      .section .data    
      .global stab
stab:	; sine table
	.byte 128 , 150 , 171 , 191 , 209 , 223 , 234 , 240 , 242 , 240 , 234 , \
	223 , 209 , 191 , 171 , 150 , 128 , 105 , 84 , 64 , 46 , 32 , 21 ,\
         15 , 13 , 15 , 21 , 32 , 46 , 64 , 84 , 105 , 127
	
.section .text             ; code section
.global __do_copy_data
.global __do_clear_bss

.global  TIMER0_COMP_vect
TIMER0_COMP_vect:       ; ISR
    ld  r24, X+         ; value from the sine table, increment pointer
    sts PORTC, r24	    ; write it to PORTC
    inc	r22	    ; increment r22
    CPSE	r20,r22	    ; is it 32 ?
    reti		    ; if not equal return, else skip reti
    clr	r22	    ; set it back to 0
    subi	r26,32	    ; subtract 32 from XL, set X to beginning of the table
    reti

        .global main                           
main:
         ldi    r16, 255         
         sts   DDRC, r16

	 ldi   r16,  (1 << WGM01) |  1  ; Set TCCR0 in the CTC mode
  	 sts  TCCR0 , r16
         ldi   r16, 50
         sts  OCR0, r16

         ldi   r16, (1 << OCIE0)  ; set TC0 compare interrupt enable bit
         sts  TIMSK, r16
         ldi   r16, (1 << OCF0)   ; interrupt enable bit
         sts  TIFR, r16 

	ldi		XL, lo8(stab)	      ; point X to the sine table
	ldi		XH, hi8(stab)
	clr		r22		  	  		  ; R22 will keep track of the  location in table
	ldi		r20,32                ; Store size of the table in R20

         sei
loop:
         rjmp loop
	.end
	
