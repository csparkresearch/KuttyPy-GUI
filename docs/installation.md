## On Ubuntu:
### Installing from source

+ sudo apt-get install python3-serial python3-pyqt5 python3-pyqt5.qtsvg gcc-avr avr-libc python3-qtconsole python3-scipy python3-pyqtgraph
+ git clone http://github.com/csparkresearch/kuttypy-gui
+ cd kuttypy-gui
+ python3 KuttyPyGUI.py

### Installing from the deb file
+ download the [latest deb](https://csparkresearch.in/kuttypy)
+ use gdebi to install it.

### Installing from the Ubuntu repository
+ sudo apt install kuttypy

!!! warning "not up to date"
	this version may not be up to date because this is very recent work, and several changes were made over the past few months

## Installing on windows.
+ This code can be run from source, provided python3 and pyqt5 are installed.
+ [Download Bundled Installer](https://drive.google.com/uc?export=download&id=1giJuDNIql8X5oaIcOLFACXD05-hmkBAy)

!!! warning "Bundled"
	This was prepared with PyInstaller, so Python will not be installed into the path. But you can run code
	in the built-in ipython-qtconsole. A better option would be to use pip to fetch PyQT5, qtconsole, pyserial, pyqtgraph, scipy and run from source code.


License: MIT
