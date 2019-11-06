
## Using PIP 
[![PyPI version](https://badge.fury.io/py/kuttyPy.svg)](https://badge.fury.io/py/kuttyPy)
### Windows

Python3 must be installed. kuttyPy package will install other dependencies such as PyQt5, qtconsole, numpy, scipy, pyqtgraph etc

```
py -3 -m pip install kuttyPy
kuttypy
```

### Ubuntu

run as superuser in order to install the `kuttypy` library, and application entry point in /usr/bin/
```
sudo pip3 install kuttyPy
kuttypy
```

!!!warning "setting permissions"
	Accessing the hardware on linux requires certain permissions to be set.
	Due to an apparent bug with pip3, the install script may fail to do this.

	As a workaround, you can run the program as root to verify the permissions issue
	```
	sudo kuttypy
	```
	For a more permanent fix for regular users, please download and execute this
	[post installation script](../assets/postinst.sh)
	
	```bash
	chmod +x postinst.sh
	sudo ./postinst.sh
	kuttypy
	```

	*If this is too hard, please install the deb file linked in the following section*

---

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
![Ubuntu package](https://img.shields.io/ubuntu/v/kuttypy?color=darkgreen&style=plastic)

+ sudo apt install kuttypy

!!! warning "not up to date"
	this version may not be up to date because this is very recent work, and several changes were made over the past few months

## Installing on windows.

+ The best option is to use pip as shown in the first section.
+ This code can be run from source, provided python3 and pyqt5 are installed.
+ [Download Bundled Installer](https://drive.google.com/uc?export=download&id=1giJuDNIql8X5oaIcOLFACXD05-hmkBAy)

!!! warning "Bundled"
	This was prepared with PyInstaller, so Python will not be installed into the path. But you can run code
	in the built-in ipython-qtconsole. A better option would be to use pip to fetch PyQT5, qtconsole, pyserial, pyqtgraph, scipy and run from source code.


License: MIT
