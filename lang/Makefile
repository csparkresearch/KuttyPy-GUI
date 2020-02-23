DESTDIR =
TS_FILES = $(shell ls *.ts)
QM_FILES = $(patsubst %.ts, %.qm, $(TS_FILES))
SOURCES = $(shell ls ../*py ../utilities/*.py)
FORMS = $(shell ls ../utilities/templates/*.ui)
PYLUPDATE ?= pylupdate5

all: $(QM_FILES)

$(QM_FILES): $(TS_FILES)
	lrelease -qt5 kpy.pro

$(TS_FILES): kpy.pro
	$(PYLUPDATE) kpy.pro

kpy.pro: $(SOURCES)
	echo "# GENERATED FILE, DO NOT EDIT" > $@
	echo "SOURCES = $(SOURCES)" >> $@
	echo "FORMS = $(FORMS)" >> $@
	echo "TRANSLATIONS = $(TS_FILES)"  >> $@

clean:
	rm -f *~ $(QM_FILES) kpy.pro

install:

.PHONY: all clean install


