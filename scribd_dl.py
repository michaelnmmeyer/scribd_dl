#!/usr/bin/env python3

import os, sys, re, requests, subprocess, tempfile

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
	return sorted(files)

def images_to_pdf(files, pdf_path):
	return subprocess.call(["convert"] + files + [pdf_path])


if len(sys.argv) != 3:
	print("Usage: %s <link> <book_path>" % os.path.basename(__file__), file=sys.stderr)
	exit(1)

link, pdf_path = sys.argv[1], sys.argv[2]

r = requests.get(link)
assert r.status_code == 200
links = extract_links(r.text)
assert links

out_dir = tempfile.mkdtemp()
files = []
try:
	files = download_pages(links, out_dir)
	images_to_pdf(files, pdf_path)
finally:
	for file in files:
		try:
			os.remove(file)
		except IOError:
			pass
	try:
		os.rmdir(out_dir)
	except IOError:
		pass
