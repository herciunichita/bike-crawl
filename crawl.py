#!/usr/bin/env python
# coding: utf-8

from json import loads, dumps
#from sys import stdin, stdout, stderr
from collections import deque
from pyquery import PyQuery as pq
import requests
import re
import os
import sys

def input():
	for line in sys.stdin:
		line = line.rstrip("\n")
		if not line: continue
		yield loads(line)


def start_crawling(start_url, domain, bike_type):
	session = requests.Session()
	urls = deque()
	visited_urls = set()
	visited_urls.add(start_url)
	urls.append(start_url)
	while urls:
		data = {"domain": domain, "type": bike_type}
		req = dict()

		url = urls.popleft()
		try:
			res = session.request("GET", url, timeout=15, cookies = None, verify=False,
				headers = {
					"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16",
					"Accept-Language":"en-US,en;q=0.8,de-DE;q=0.6,de;q=0.4,en;q=0.2",
					"Accept-Charset":"utf-8;q=0.7,*;q=0.7"
			})

		except requests.exceptions.RequestException as ex:
			print >>sys.stderr, ex
			print >>sys.stderr, url
			continue
		
		if res is None: continue	
		
		req["url"], req["html"] = res.url, res.text
		data["url"] = res.url

		try:
			extractor = __import__(domain)
		except ImportError as ex:
			print >>sys.stderr, ex
			continue

		try:
		
			crawled = extractor.extract_urls(req)
		except:
			continue
		for page in crawled:
			if page not in visited_urls:
				visited_urls.add(page)
				urls.append(page)

		try:
			data["data"] = extractor.extract_data(req)
		except:
			continue

		if data["data"]:
			sys.stdout.write(dumps(data) + "\n")


if __name__ == '__main__':

	sys.path.append(os.path.join(os.path.dirname(__file__), "extractors"))

	for req in input():
		start_crawling(req["url"], req["domain"], req["type"])


