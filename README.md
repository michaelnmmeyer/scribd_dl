# scribd_dl

Download ebooks from Scribd.

## Dependencies

*	python3
*	requests
*	imagemagick

On Debian-like systems, you can install all of the above with:

	sudo apt-get install python3 python3-requests imagemagick


## Howto

	./scribd_dl.py https://www.scribd.com/doc/209105154/Schlegel Article.pdf

The script downloads all pages separately and joins them back to
create the final ebook file. A drawback is that the generated PDFs
tend to be much larger than usual.
