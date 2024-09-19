
??? abstract "Ubuntu"
    * Download the [deb file from here](https://csparkresearch.in/assets/installers/KuttyPy-1.0.25.deb)
    * Navigate to the Downloaded deb file location, and install it. This also fetches dependencies : scipy, qtconsole, avr-gcc etc
    ```
    sudo apt install ./KuttyPy-1.0.25.deb 
    ```
    * launch the kuttyPy GUI from the command prompt using the command
    ```
    kuttypyplus
    ```

    It is also present in the applications menu as `KuttyPy GUI` .
    
    * You can also launch the kuttyPy IDE from the menu, or using the command
    ```
    kuttypyide
    ```



??? abstract "Windows with Python3 installed [![PyPI version](https://badge.fury.io/py/kuttyPy.svg)](https://badge.fury.io/py/kuttyPy)"

    * [Python3](https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe) must be installed, and `pip` should be accessible.
    * Open a command prompt as administrator, and use pip3 to install the KuttyPy package
    ```
    py -3 -m pip install KuttyPy
    ```
    * Download and install the [CH341 USB Driver](../assets/CH341SER.EXE)
    * You will now be able to launch `kuttypyplus` from the prompt, and import the `kuttyPy` library from any Python script.
	* you can also launch `kuttypyide`
    * If you wish to compile C code and upload to the KuttyPy hardware, winavr must be installed, and `avr-gcc` must be accessible from a command prompt.
        * Download and install `winavr` from [winavr.sourceforge.net](https://sourceforge.net/projects/winavr/files/WinAVR/20100110/WinAVR-20100110-install.exe/download)
	* if the commands are not accessible, then you need to add the Scripts folder to the path. [similar docs here](https://csparkresearch.in/installers/install-via-pip.html#install-eyes17-from-pypi)


??? warning "Windows bundled installer"
    * The bundled installer includes Python3 and dependencies and KuttyPy software. Also includes winavr, usb driver.

	[Download Bundled Installer](https://drive.google.com/uc?export=download&id=18PD-Llx12PTfMRWlHA447TCMxTA6smWZ)

	!!! error "Made with Pyinstaller: Python will not be accessible globally"
		Since the installer was made using PyInstaller, Python3 will not be accessible globally, and you will be limited to the ipython console within the KuttyPy software.
		A better option would be to use pip to fetch PyQT5, qtconsole, pyserial, pyqtgraph, scipy , and KuttyPy . Winavr and the driver can be installed separately. Refer to the previous section.



??? abstract "Using Python PIP [![PyPI version](https://badge.fury.io/py/kuttyPy.svg)](https://badge.fury.io/py/kuttyPy) Windows/Linux/Other OSes"

    * Python3 must be installed
    * Open a command prompt as administrator, and use pip3 to install the KuttyPy package
    ```
    pip3 install kuttyPy
    ```
    * You will now be able to launch `kuttypy` from the prompt, and import the `kuttyPy` library from Python.
    * If you wish to compile C code, `avr-gcc` must be accessible from a command prompt. Install it from the package manager of your OS.

    ???warning "setting permissions on Linux based systems "
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
    
    
???abtract " Installing from source code " 
    ```bash
    sudo apt install python3-serial python3-pyqt5 python3-pyqt5.qtsvg gcc-avr avr-libc python3-qtconsole python3-scipy python3-pyqtgraph
    git clone http://github.com/csparkresearch/kuttypy-gui
    cd kuttypy-gui
    python3 KuttyPyPlus.py
    ```
    For setting hardware permissions, refer to the previous section

???abtract " Android App ![Ubuntu package](https://badgen.net/badge/android/kuttypy/blue?icon=googleplay) . Unrelated." 
	The device works with android phones via USB-OTG, but the app is structured very differently from the desktop setup, and these docs do not apply.

	Install from the [Google Play Store](https://play.google.com/store/apps/details?id=com.cspark.kuttypy)



### Installing from the Ubuntu repository
![Ubuntu package](https://badgen.net/badge/ubuntu/stable/green?icon=github)

this version may not be up to date because this is very recent work, and several changes were made over the past few months

+ sudo apt install kuttypy


License: MIT
