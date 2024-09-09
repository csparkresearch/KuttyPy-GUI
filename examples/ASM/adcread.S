
#include <avr/io.h>  
.global main
main:

LDI R16, 255
STS DDRB, R16
STS DDRD, R16

LDI R16, 0x87              ; Enable ADC, set clock pre-scaler
STS ADCSRA, R16  

LDI R17, 0x40
STS ADMUX, R17            ;	  AVCC reference, channel 0 	

LDI R16, 0xC7
STS ADCSRA, R16           ;     Start ADC 

L1:
LDS R18, ADCSRA
ANDI R18, 0x10              
BRNE L1                    ;	 wait for ADC conversion


LDS R19, ADCL
STS PORTB, R19
LDS R19, ADCH
STS PORTD, R19
.END