# Compile for ATmega328p, generate .hex, .map and .lst files
avr-gcc  -Wall -O2 -mmcu=atmega328p -Wl,-Map,$1.map -o $1 $1.c
avr-objcopy -j .text -j .data -O ihex $1 $1_328p.hex
#avr-objdump -S $1 > $1.lst

