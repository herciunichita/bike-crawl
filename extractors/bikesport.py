#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.bikesport.dk'
	w = pq(req["html"])

	next_page = w("a.next.i-next")
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w("div#amshopby-page-container h2.product-name>a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.bikesport.dk'
	w = pq(req["html"])

	is_bike = w(".product-name>h1>strong")
	if is_bike:
		data["provider_store"] = domain
		name = w(".product-name>h1>strong").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
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
				data["brand"] = item_data
			if label == "Varenummer":
				data["external_source_id"] = item_data
			if label == "Ramme":
				data["frame"] = item_data
			if label == "Kassette":
				data["gearset"] = item_data
			if label == "Hjulsæt":
				data["wheelset"] = item_data

		desc = w("div.std").text().strip()
		if desc:
			data["description"] = desc
		bike_sizes = w(".jqTransformSelectWrapper>ul>li")
		sizes = dict()
		if bike_sizes:
			for size in bike_sizes:
				content = w(size)
				size_regex = re.search(r"(\d+)(\w{2})", content.text())
				availability = content.find("img").attr("src")
				if "stock_green" in availability:
					available = "Available"
				if "stock_yellow" in availabilty:
					available = "Available to Order"
				if "stock_red" in availability:
					available = "Out of Stock"
				if size_regex:
					sizes[size_regex.group(1)] = available
				data["size_measure"] = size_regex.group(2) if size_regex.group(2) == "cm" else "inch"
		data["availability"] = sizes
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
