#!/usr/bin/env python3

import os, sys, re, requests, subprocess, tempfile, shutil

def extract_links(html):
	links = set()
	
	# Matches the first 3 pages, e.g.:
	#    https://html2-f.scribdassets.com/7uazckj1ds380hol/images/1-bfc3187991.jpg
	for link in re.findall(r'http://html\.scribd\.com/[^"]+', html):
		links.add(link)
	
	# Matches the remaining pages, of the form:
	#    https://html2-f.scribdassets.com/7uazckj1ds380hol/pages/29-93d362946c.jsonp
	# Must be converted to: 
	#    https://html2-f.scribdassets.com/7uazckj1ds380hol/images/29-93d362946c.jpg
	for link in re.findall(r'https://html[12]-f\.scribdassets\.com/[^/]+/pages/[^"]+', html):
		link = link.replace("/pages/", "/images/")
		link = os.path.splitext(link)[0] + ".jpg"
		links.add(link)
	
	return links

def download_image(url):
	print(url, file=sys.stderr)
	r = requests.get(url, stream=True)
	assert r.status_code == 200
	return r.raw.read()

def download_pages(links, out_dir):
	files = []
	for link in links:
		page_num = link.rsplit("/", 1)[1].split("-", 1)[0]
		out_file = os.path.join(out_dir, "%03d.jpg" % int(page_num))
		image = download_image(link)
		with open(out_file, "wb") as fp:
			fp.write(image)
		files.append(out_file)
	files.sort()
	return files

def images_to_pdf(files, pdf_path):
	subprocess.check_call(["convert"] + files + [pdf_path])

def extract_filename(url):
	return url.rsplit("/", 1)[1] + ".pdf"

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print("Usage: %s <link> [book_path]" % os.path.basename(__file__), file=sys.stderr)
	exit(1)

link = sys.argv[1]
pdf_path = len(sys.argv) > 2 and sys.argv[2] or extract_filename(link)

r = requests.get(link)
assert r.status_code == 200
links = extract_links(r.text)
assert links

out_dir = tempfile.mkdtemp()
try:
	files = download_pages(links, out_dir)
	images_to_pdf(files, pdf_path)
finally:
	shutil.rmtree(out_dir)
