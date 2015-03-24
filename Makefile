BIN_PATH = /usr/local/bin/scribd_dl

all:

install:
	cp scribd_dl.py $(BIN_PATH)

uninstall:
	rm -f $(BIN_PATH)

check:
	./scribd_dl.py 'https://www.scribd.com/doc/209105154/Schlegel' Book.pdf
	pdfinfo Book.pdf | egrep -q '^Pages:[ ]+10$$'
	rm -f Book.pdf

.PHONY: all install uninstall check
