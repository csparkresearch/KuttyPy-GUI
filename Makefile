QT_VERSION?=PyQt5
PY_VERSION?=3
export QT_VERSION


ifeq ($(QT_VERSION),PyQt5)
  PYUIC = pyuic5
  PYRCC = pyrcc5
  PYLUPDATE = pylupdate5
else ifeq ($(QT_VERSION),PyQt4)
  PYUIC = pyuic4
  PYRCC = pyrcc4
  PYLUPDATE = pylupdate4
else ifeq ($(QT_VERSION),PySide)
  PYUIC = pyside-uic
  PYRCC = pyside-rcc
  PYLUPDATE = pylupdate4
else
  PYUIC = pyuic4
  PYRCC = pyrcc4
  PYLUPDATE = pylupdate4
endif

SUBDIRS = utilities

all: recursive_all

recursive_all:
	@echo '?. Using QT Version:' $(QT_VERSION)  $(PYUIC) $(PYRCC)  $(PYLUPDATE) $(PY_VERSION)
	@echo "QT_VERSION = '$(QT_VERSION)'\nPY_VERSION = $(PY_VERSION)\n" > utilities/build_details.py
	for d in $(SUBDIRS); do make PYUIC=$(PYUIC) PYRCC=$(PYRCC) PYLUPDATE=$(PYLUPDATE) PY_VERSION=$(PY_VERSION) -C $$d all; done

clean: recursive_clean
	rm -rf *.pyc *~ __pycache__

recursive_clean:
	for d in $(SUBDIRS); do make -C $$d clean; done

.PHONY: all recursive_all clean recursive_clean
