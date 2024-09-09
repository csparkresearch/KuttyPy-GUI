# The IDE

Kuttypy software has an IDE with many examples for learning embedded systems

## Examples

* [BMP180](programming/BMP180.md) : Read values from a BMP180 sensor and dump them to the serial port.


## Controls

* Process
  * Compile
  * Upload
  * Run

!!! info "Compilation"
	This uses the AVR-GCC compiler to create a hex file. the map and lst files are also shown in new tabs
	![Screenshot](images/ide/compile.png)

!!! info "uploading"
	Upload the compiled hex file to the hardware. 
	![Screenshot](images/ide/upload.png)

!!! info "executing"
	Execute the uploaded program. Any information sent by the firmware over UART is shown in the serial monitor(38400 BAUD)
	![Screenshot](images/ide/run.png)
	
