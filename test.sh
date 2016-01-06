#!/usr/bin/env bash

set -e

echo 'Early failure if we cannot download the PDF.' 
./scribd_dl.py 'https://www.scribd.com/doc/141757042/Atlas-de-Patologia-Del-Complejo-Bucal' 2>&1 | grep -q 'embedded text not supported'

echo 'Ensure all pages are extracted.'
./scribd_dl.py 'https://www.scribd.com/doc/209105154/Schlegel' Book.pdf
pdfinfo Book.pdf | egrep -q '^Pages:[ ]+10$$'
rm Book.pdf

echo 'Ensure the correct file name is extracted.'
./scribd_dl.py 'https://www.scribd.com/doc/6073806/Moliendo-cafe'
test -f 'Moliendo café.pdf'
rm 'Moliendo café.pdf'

echo "Ensure a PDF file is produced even if the output filename doesn't have an extension."
./scribd_dl.py 'https://www.scribd.com/doc/6073806/Moliendo-cafe' foobar
test -f foobar
rm foobar

echo "Ensure whe can use spaces in the output file name."
./scribd_dl.py 'https://www.scribd.com/doc/6073806/Moliendo-cafe' 'foo  bar'
test -f 'foo  bar'
rm 'foo  bar'

exit 0
