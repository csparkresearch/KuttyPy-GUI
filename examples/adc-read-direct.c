#include <avr/io.h> 

// convert channel 0, set pre-scaler to 7 

int main()
{ 
DDRB = 255;
ADCSRA = (1 << ADEN) |  7;              // Enable ADC, set clock pre-scaler
ADMUX =  (1 << REFS0) | (1 << ADLAR);	// AVCC ref, Left adjust, read channel 0 	

while (1)
   {
   ADCSRA |=  (1 <<ADSC);               // Start ADC 
   while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
   ADCSRA |=  (1 <<ADIF);
   PORTB = ADCH;
   }
}
