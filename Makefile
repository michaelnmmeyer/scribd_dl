# Installation path.
BIN_PATH = /usr/local/bin/scribd_dl

all:

install:
	cp scribd_dl.py $(BIN_PATH)

uninstall:
	rm -f $(BIN_PATH)

check:
	./test.sh

commit: check
	git add . && git commit

.PHONY: all install uninstall check commit
