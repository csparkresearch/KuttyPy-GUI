PYUIC?=pyuic5
PYRCC?=pyrcc5
PY_VERSION ?= 2

UI_FILES = $(shell ls *.ui)
RC_FILES = $(shell ls *.qrc)

UI_COMPILED = $(patsubst %.ui, ui_%.py, $(UI_FILES))
RC_COMPILED = $(patsubst %.qrc, %_rc.py, $(RC_FILES))

ifeq ($(PY_VERSION),3)
	ifneq (,$(findstring pyrcc4,$(PYRCC)))
		override PYRCC += -py3
	endif
endif
$(info PYRCC=$(PYRCC))

 
all: $(UI_COMPILED) $(RC_COMPILED)

clean:
	rm -f $(UI_COMPILED) $(RC_COMPILED)
	rm -rf *.pyc *~ __pycache__

ui_%.py:  %.ui
	$(PYUIC) --from-import $< -o $@


# rcc -g python (Qt6) places -o before the input file and emits PySide6 imports;
# pyrcc5/pyrcc4 place the input before -o and emit PyQt5/PyQt4 imports.
%_rc.py: %.qrc
	if echo "$(PYRCC)" | grep -q "rcc -g"; then \
		$(PYRCC) -o $@ $<; \
		sed -i \
		  -e 's/^from PySide6 import QtCore$$/from pyqtgraph.Qt import QtCore/' \
		  -e 's/^import PySide6\.QtCore$$/from pyqtgraph.Qt import QtCore/' \
		  -e 's/PySide6\.QtCore\./QtCore./g' \
		  $@; \
	else \
		$(PYRCC) $< -o $@; \
	fi

.PHONY: all clean
