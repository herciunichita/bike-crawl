#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.winstanleysbikes.co.uk'
	w = pq(req["html"])

	# ugly hack for testing purposes. avoid this 'if'
	if req["url"] == "http://www.winstanleysbikes.co.uk/category/336/Bikes":
		cats = w("table#catprods_hdr td.column_main a.links_main")

		for item in cats:
			item = pq(item)

			urls.add(domain + item.attr("href"))
		return list(urls)

	next_page = w("input.buttonstyle[name='next']")
	if next_page:
		urls.add(next_page.attr("onclick").replace("parent.location.href=", "").replace("'", ""))

	bikes = w("table#catprods_tbl a.links_main")
	for item in bikes:
		item = pq(item)

		urls.add(domain + item.attr("href"))

	return list(urls)


def extract_data(req):
	data = bike
	w = pq(req["html"])

	is_bike = w("table#prod_tbl.sectionborder_main img")
	if is_bike:
		name = w("table#item_Tbl.column_main tr:first").find("td").eq(1).text()
		data["name"] = name
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
