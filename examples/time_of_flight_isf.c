/* time of flight measurement of a falling object. 
 * A 5V relay is opened, and the electromagnet is exposed. Its input pin is connected to C0.
 * the electromagnet is energized by turning on PIN_RELAY(PC0).
 * The user now fixes this relay at a fixed height from the floor/table, and attaches
 * a small steel ball to it.
 * A switch is connected from A0 to GND. When it is pressed, the relay is turned off, and the steel ball
 * will automatically fall down. It should hit a contact switch made with 2 metal
 * plates connected between PB1 and GND. 
 * 
 * The microcontroller starts a timer when the relay is turned off, and stops it when the contact switch
 * is triggered, thereby measuring the time taken for the ball to travel the known distance.
 * Results shown on MAX7219 display connected via SPI with B4 as chip select pin 
 * Author: jithinbp@gmail.com
 * License : gpl-v3
 * Date 10 december 2019

   Copyright (C) 2019 Jithin B.P, CSpark Research,
   New Delhi 

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

 */

// 8MHz clock
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include "mh-utils.c"

#define F_CPU 8000000UL

// Outputs, pin definitions
#define PIN_SCK                   7
#define PIN_MOSI                  5
#define PIN_SS                    4

#define ON                        1
#define OFF                       0

#define MAX7219_LOAD1             PORTB |= (1<<PIN_SS)
#define MAX7219_LOAD0             PORTB &= ~(1<<PIN_SS)

#define MAX7219_MODE_DECODE       0x09
#define MAX7219_MODE_INTENSITY    0x0A
#define MAX7219_MODE_SCAN_LIMIT   0x0B
#define MAX7219_MODE_POWER        0x0C
#define MAX7219_DIGIT0            0x01
#define MAX7219_CHAR_BLANK        0xF 

// CONNECT RELAY's control pin to PC0
#define PIN_RELAY 0
#define RELAY_OFF   PORTC |= (1<<PIN_RELAY)
#define RELAY_ON  PORTC &= ~(1<<PIN_RELAY)

// CONNECT trigger switch on PA0
#define INPUT_HIGH  PINA&(1)

//CONNECT detector switch pin to PC1
#define SWITCH_HIGH  PINC&(1<<1)

#define GREEN_ON   PORTD |= 255
#define GREEN_OFF  PORTD = 0

char digitsInUse = 8;

void spiSendByte (char databyte)
{
    // Copy data into the SPI data register
    SPDR = databyte;
    // Wait until transfer is complete
    while (!(SPSR & (1 << SPIF)));
}

void MAX7219_writeData(char data_register, char data)
{
    MAX7219_LOAD0;
        // Send the register where the data will be stored
        spiSendByte(data_register);
        // Send the data to be stored
        spiSendByte(data);
        delay_ms(1);
    MAX7219_LOAD1;
}

void MAX7219_clearDisplay() 
{
    char i = 8;
    do {
        MAX7219_writeData(i, MAX7219_CHAR_BLANK);
    } while (--i);
}

void MAX7219_displayNumber(volatile long number,volatile char offset) 
{
    if (number == 0) {
        MAX7219_writeData(MAX7219_DIGIT0+offset, 0);
        return;
    }
    
    char i = 0; 
    do {
        MAX7219_writeData(offset+(++i), number % 10);
        number /= 10;
    } while (number);
}

volatile uint16_t HIWORD;

ISR(TIMER1_COMPA_vect)	// TIMER1 Compare Match A Interrupt
{
TCNT1 = 0;
++HIWORD;
}

void start_timer()
{
/*
When TCNT1 reaches OCR1A, the ISR will run. It will clear TCNT1 and increment HIWORD.
The total time elapsed between start_timer and get_timer = HIWORD * 50000 + TCNT1
*/
 TCCR1B = (1 << CS11);   // Normal mode, with 1MHz clock
 HIWORD = 0;
 OCR1A = 50000;        
 OCR1B = 0xffff;
 TIMSK = (1 <<  OCIE1A);   // Enable compare match interrupt
 TIFR = (1 << OCF1A); 
 TCNT1 = 0;
 sei();
}

uint32_t read_timer()
{
 uint32_t x;
 
 TCCR1B = 0;    // stop TC1 clock
 x = HIWORD * 50000 + TCNT1;
 cli();
 return x;
}

int main(void)
{
uint32_t x;
double distance=0;

// SCK MOSI CS/LOAD/SS
DDRB |= (1 << PIN_SCK) | (1 << PIN_MOSI) | (1 << PIN_SS) ;

DDRD = 255; //Green LEDs flashing.
PORTD = 0; // All off
PORTA = 1 ; //pullups on PA0 for user input switch

DDRC=1; // output on C0 . for relay. C1 is the detector input
PORTC=1; // relay off

// SPI Enable, Master mode. SPI is a communication bus to send data
// to the display
SPCR |= (1 << SPE) | (1 << MSTR)| (1<<SPR0);
delay_ms(50);
MAX7219_writeData(MAX7219_MODE_DECODE, 0xFF);
delay_ms(50);

// Scan limit runs from 0.
MAX7219_writeData(MAX7219_MODE_SCAN_LIMIT, digitsInUse - 1);
MAX7219_writeData(MAX7219_MODE_INTENSITY, 8);
MAX7219_writeData(MAX7219_MODE_POWER, ON);
delay_ms(50);


MAX7219_clearDisplay();

while(1){
	RELAY_ON;
	while(INPUT_HIGH){GREEN_ON;delay_ms(50);GREEN_OFF;delay_ms(100);} ;   // Wait for user to press PD7 switch
	
	RELAY_OFF;             // Turn off the RELAY, thereby dropping the metal ball
	start_timer();         // start the timer using Timer/Counter1
	while(SWITCH_HIGH) ;   // Wait for the ball to hit the switch between PB0 and GND
	x = read_timer();      // Store the value of the timer into a variable called x

	distance = (float)(x)/1000.;   //this is actually the time in mS
	MAX7219_clearDisplay();
	// Show the timer value(mS) on the first 4 digits of the screen
	MAX7219_displayNumber((uint32_t)distance,4); 

	// Show the distance value(mm) on the last 4 digits of the screen
	distance = 0.5*981*distance*distance/1000./1000.; // S = 0.5 * g *  t^2
	MAX7219_displayNumber((uint32_t)(distance*10),0); //distance in mm
	}

}





