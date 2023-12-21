# Compile for 32, generate .hex, .map and .lst files
avr-gcc  -Wall -O2 -mmcu=atmega32 -Wl,-Map,$1.map -o $1 $1.c
avr-objcopy -j .text -j .data -O ihex $1 $1_32.hex
#avr-objdump -S $1 > $1.lst

