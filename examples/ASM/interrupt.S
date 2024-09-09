
#include <avr/io.h>

.section .text    ; denotes code section

.global __vector_1       ; INT0_vect 
__vector_1:
  INC R1
  STS PORTB, R1
  RETI

.global main
main:
  LDI R16, 255
  STS DDRB, R16           ; port B as output
  LDI R16, 0b11111011
  STS DDRD, R16           ; only pin  PD2 as input

  COM R16                 ; enable Pull-up only on PD2, INT0
  STS PORTD, R16

  LDI R16, 2              ; make INT0 trigger on falling edge
  STS MCUCR, R16

  LDI R16, 0x40      ; enable INT0 enable bit of GICR
  STS GICR, R16   
  CLR R1
  SEI                ; enable interrupts

loop:                ; infinite wait loop
  RJMP loop
.end
