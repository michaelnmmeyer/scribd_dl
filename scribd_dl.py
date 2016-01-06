#!/usr/bin/env python3

import os, sys, re, requests, subprocess, tempfile, shutil
import unicodedata

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

# https://html2-f.scribdassets.com/7uazckj1ds380hol/images/29-93d362946c.jpg -> 29
def extract_page_num(link):
	return int(link.rsplit("/", 1)[1].split("-", 1)[0])

# There must be at least one link (at least one page), and one link per page.
# Checking for an interval is not enough because there could be several aliases
# for the same page (say 29-93d362946c and 29-bfc3187991), so we must also check
# the real number of pages.
def check_links(links):
	assert links, "no links found"
	page_nums = set()
	num_pages = 0
	for link in links:
		page_num = extract_page_num(link)
		page_nums.add(page_num)
		if page_num > num_pages:
			num_pages = page_num
	assert len(page_nums) == num_pages, "missing pages"

def download_image(url):
	print(url, file=sys.stderr)
	r = requests.get(url, stream=True)
	assert r.status_code == 200, "can't download image at '%s'" % url
	return r.raw.read()

def download_pages(links, out_dir):
	files = []
	for link in links:
		page_num = extract_page_num(link)
		out_file = os.path.join(out_dir, "%03d.jpg" % page_num)
		image = download_image(link)
		with open(out_file, "wb") as fp:
			fp.write(image)
		files.append(out_file)
	files.sort()
	return files

def images_to_pdf(files, pdf_path):
	subprocess.check_call(["convert"] + files + ["pdf:%s" % pdf_path])

def extract_filename(page):
	title = re.findall(r"<title>(.+?)</title>", page, re.I)
	assert len(title) == 1, "can't extract the book title"
	title = unicodedata.normalize("NFKC", title[0])
	# Don't assume the file name is legit.
	return title.replace("/", "_") + ".pdf"

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print("Usage: %s <link> [book_path]" % os.path.basename(__file__), file=sys.stderr)
	exit(1)

link = sys.argv[1]
r = requests.get(link)
assert r.status_code == 200, "can't download page at '%s'" % link

if "docManager.addFont" in r.text:
   me = os.path.basename(sys.argv[0])
   print("%s: PDFs with embedded text not supported" % me, file=sys.stderr)
   print("%s: Try https://github.com/tobiasBora/Scribd-downloader/blob/master/scribd_download.sh" % me, file=sys.stderr)
   sys.exit(1)

links = extract_links(r.text)
check_links(links)

pdf_path = len(sys.argv) > 2 and sys.argv[2] or extract_filename(r.text)
out_dir = tempfile.mkdtemp()
try:
	files = download_pages(links, out_dir)
	images_to_pdf(files, pdf_path)
finally:
	shutil.rmtree(out_dir)
