# You'll need some packages
# pip3 install --user --upgrade setuptools wheel twine
# Change the version number in setup.py or it will get rejected.
#
# To test, open a venv (dependences: numpy, pyserial will be installed)
# python3 -m pip install --upgrade kuttyPy
#

rm -rf dist build

# Prepare the graphical library package called kuttyPy

rm -rf kuttyPy
mkdir kuttyPy
touch kuttyPy/__init__.py
cp ../utilities/REGISTERS.py kuttyPy/
cp ../KuttyPyLib.py kuttyPy/__init__.py
cat autoimport.py >> kuttyPy/__init__.py
sed -i "s/^from utilities import REGISTERS.*$/from . import REGISTERS/g" kuttyPy/__init__.py

# Prepare the graphical app package called kuttyPyGui
rm -rf kuttyPyGui
mkdir kuttyPyGui
touch kuttyPyGui/__init__.py
cp ../*.py kuttyPyGui/
mkdir kuttyPyGui/utilities
mkdir kuttyPyGui/utilities/templates
mkdir kuttyPyGui/examples
mkdir kuttyPyGui/examples/atmega32
mkdir kuttyPyGui/examples/atmega328p
touch kuttyPyGui/examples/__init__.py
touch kuttyPyGui/examples/atmega32/__init__.py
touch kuttyPyGui/examples/atmega328p/__init__.py
touch kuttyPyGui/utilities/templates/__init__.py

cp ../examples/*.c kuttyPyGui/examples/
cp ../examples/atmega32/*.py kuttyPyGui/examples/atmega32/
cp ../utilities/*.py kuttyPyGui/utilities/
cp ../utilities/templates/ui_*.py kuttyPyGui/utilities/templates/
cp ../utilities/templates/*_rc.py kuttyPyGui/utilities/templates/
cp ../utilities/templates/gauge.py kuttyPyGui/utilities/templates/
cp -R ../utilities/themes kuttyPyGui/utilities/

sed -i "s/from utilities/from .utilities/g" kuttyPyGui/KuttyPyGUI.py
sed -i "s/import KuttyPyLib/from . import KuttyPyLib/g" kuttyPyGui/KuttyPyGUI.py
sed -i "s/import constants/from . import constants/g" kuttyPyGui/KuttyPyGUI.py


sed -i "s/from utilities/from .utilities/g" kuttyPyGui/KuttyPyNano.py
sed -i "s/import KuttyPyLib/from . import KuttyPyLib/g" kuttyPyGui/KuttyPyNano.py
sed -i "s/import constants/from . import constants/g" kuttyPyGui/KuttyPyNano.py


sed -i "s/^from utilities/from .utilities/g" kuttyPyGui/KuttyPyLib.py

#sudo python3 setup.py install

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*


