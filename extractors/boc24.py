#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.boc24.de'
	w = pq(req["html"])

	next_page = w(".right_arrow.sprite.arrow-next").eq(0)
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w(".product_description a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.westbrookcycles.co.uk'
	w = pq(req["html"])

	is_bike = w("span#product_title")
	if is_bike:
		name = w("span#product_title").text().strip()
		if name:
			data["name"] = name
		data["currency"] = "GBP"
		image = w("a#product_zoom_image").attr("href")
		if image:
			data["image"] = domain + image
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
				data["brand"] = item_data
			if label == "Varenummer":
				data["id"] = item_data
			if label == "Ramme":
				data["frame_material"] = item_data
			if label == "Cykel Type":
				data["type"] = item_data
		
		desc = w("div.std").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
