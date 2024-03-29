
/* lcd.c -- routines for handling a text mode LCD display. Not the best ones available.

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi and Pramode C.E, GnuVision.com.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>
#include <stdint.h>

// LCD control bits of Port C on Phoenix MDK. Refer to the Schematic
#define ENBIT 0x20  	
#define RWBIT 0x40  
#define RSBIT 0x80  

void delay(uint16_t k)
{
    volatile uint16_t x = k;
    while(x)
        --x;
}


uint8_t cpos = 0;		// LCD cursor position

void lcd_command (uint8_t cmd)
{
	PORTC &= 16;				// Clear bits used by LCD except PC4
	PORTC |= (cmd >>4 ) & 0x0F;			// Put 4 MSBs, RS, RW & EN Low
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	PORTC &= 16;
	PORTC |= (cmd ) &0x0F;			// Put 4 LSBs 
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	delay (10000);
}


void lcd_init (void)  // This needs rewriting
{
	delay(10000);
	DDRC |= 239;			// Except PC4 all are outputs
	lcd_command (32 + 8 + 4);	// 4 bit data mode
	lcd_command (4 + 2);		// Entry mode
	lcd_command (8 + 4);		// display ON, no cursor
	lcd_command (1);		// Clear
	cpos = 0;			// Set cursor position variable
	delay(10000);
	DDRC |= 239;			// Except PC0 all are outputs
	lcd_command (32 + 8 + 4);	// 4 bit data mode
	lcd_command (4 + 2);		// Entry mode
	lcd_command (8 + 4);		// display ON, no cursor
	lcd_command (1);		// Clear
	cpos = 0;			// Set cursor position variable
}


void lcd_clear (void)
{
	lcd_command(1);
}


void lcd_put_char (char c)
{
	PORTC &= 16;				// Clear bits used by LCD except PC4 0x08
	PORTC |= RSBIT | ((c>>4) & 0x0F);		// Put 4 MSBs, RS High, RW & EN Low
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	PORTC &= 16;
	PORTC |= RSBIT | (c&0x0F);		// Put 4 LSBs 
	PORTC |= ENBIT;  PORTC &= ~ENBIT;	// Pulse on EN pin
	delay(1000);
	++cpos;  if(cpos == 20) 		// change to 20 to 8 for 1x16 character displayy
		lcd_command(128 + 32 + 8);	// 4 x 20 display
}  


void lcd_put_string(char *p)
{
	while(*p) {
		lcd_put_char(*p);
		++p;
	}
}

void lcd_put_byte(uint8_t i)
{
	uint8_t pos100 = 0;

	if(i/100) {
		pos100 = 1;
		lcd_put_char('0' + i/100);
		i %= 100;
	}

	if( (i/10) || pos100) {
		lcd_put_char('0' + i/10);
		i %= 10;
	}
	lcd_put_char('0' + i);
}

void lcd_put_int(uint16_t val)
{
	char 	ss[8];
	uint8_t	k;

	if(val ==0) {
		lcd_put_char('0');
		return;
	}

	k = 0;
	while(val > 0) {
		ss[k++] = '0' + (val % 10);
		val /= 10;
	}
	while(k) {
		lcd_put_char(ss[k-1]);
		--k;
	}
}

void lcd_put_long(uint32_t val)
{
	char 	ss[8];
	uint8_t	k;

	if(val ==0) {
		lcd_put_char('0');
		return;
	}

	k = 0;
	while(val > 0) {
		ss[k++] = '0' + (val % 10);
		val /= 10;
	}
	while(k) {
		lcd_put_char(ss[k-1]);
		--k;
	}
}

