all:

check:
	./scribd_dl.py 'https://www.scribd.com/doc/209105154/Schlegel' Book.pdf
	pdfinfo Book.pdf | egrep -q '^Pages:[ ]+10$$'
	rm -f Book.pdf
