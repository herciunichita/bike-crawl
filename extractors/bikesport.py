#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.bikesport.dk'
	w = pq(req["html"])

	# ugly hack for testing purposes. avoid this 'if'
	if req["url"] == "http://www.bikesport.dk/cykler/":
		cats = w(".amshopby-cat.amshopby-cat-level-1>a")

		for item in cats:
			item = pq(item)
			urls.add(item.attr("href"))
		return list(urls)

	next_page = w("a.next.i-next")
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w("div#amshopby-page-container h2.product-name>a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = bike
	domain = 'http://www.bikesport.dk'
	w = pq(req["html"])

	is_bike = w(".product-name>h1>strong")
	if is_bike:
		name = w(".product-name>h1>strong").text().strip()
		if name:
			data["name"] = name
		data["currency"] = "DKK"
		image = w(".slides>li>img").eq(0).attr("src")
		if image:
			data["image"] = image
		old_price = w(".price-box p.old-price span.price").text().strip()
		if old_price:
			actual_price = re.match(r"(\d+\.*\d+\,\d+).*", price)
			data["price"] = actual_price.group(1).replace(".", "").replace(",", ".")
			disc_price = w(".price-box p.special-price span.price").text().strip()
			disc_price = re.match(r"(\d+\.*\d+\,\d+).*", disc_price)
			data["discounted_price"] = disc_price.group(1).replace(".", "").replace(",", ".")
		else:
			price = w(".price-box span.regular-price").text().strip()
			price = re.match(r"(\d+\.*\d+\,\d+).*", price)
			data["price"] = price.group(1).replace(".", "").replace(",", ".")
			data["discounted_price"] = price.group(1).replace(".", "").replace(",", ".")

		bike_specs = w("div.specifications_block ul.data-table li")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('.label').text().strip()
			item_data = item.find('.data').text().strip()
			if label == "Producent":
				data["bike_brand"] = item_data
			if label == "Varenummer":
				data["id"] = item_data
			if label == "Ramme":
				data["frame_material"] = item_data
			if label == "Cykel Type":
				data["type"] = item_data
		
		desc = w("div.std").text().strip()
		if desc:
			data["bike_description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
