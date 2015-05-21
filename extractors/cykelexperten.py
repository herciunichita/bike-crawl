#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.cykelexperten.dk'
	w = pq(req["html"])

	next_page = w("a.next-link").eq(0)
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w(".shop-catalog-product-title a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.cykelexperten.dk'
	w = pq(req["html"])

	is_bike = w("h1.shop-product-title")
	if is_bike:
		data["provider_store"] = domain
		external_source_id = w("[name='shop_product_id']").attr("value")
		if external_source_id:
			data["external_source_id"] = external_source_id
		name = w("h1.shop-product-title").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "DKK"
		image = w("a#shop-product-main-image-link").attr("href")
		if image:
			data["image"] = image
		new_price = w("span.shop-product-price-special").text().strip()
		if new_price:
			actual_price = re.match(r"(\d+\.*\d+\,\d+)", new_price)
			data["price"] = actual_price.group(1).replace(".", "").replace(",", ".")
			disc_price = w("span#shop-product-price-with-tax").text().strip()
			disc_price = re.match(r"(\d+\.*\d+\,\d+)", disc_price)
			data["discounted_price"] = disc_price.group(1).replace(".", "").replace(",", ".")
		else:
			price = w("span#price-with-tax-value").text().strip()
			price = re.match(r"(\d+\.*\d+\,\d+)", price)
			data["price"] = price.group(1).replace(".", "").replace(",", ".")
			data["discounted_price"] = price.group(1).replace(".", "").replace(",", ".")

		#availability = dict()
		#sizes = w("select#attribute_1>option")
		#print sizes
		#for size in sizes:
		#	content = w(size)
		#	if "else" not in content.text().strip():
		#		availability[content.text().strip()] = "Available to Order"
		#data["availability"] = availability
		bike_specs = w(".shop-product-description p")
		if bike_specs:
			data["description"] += w(bike_specs).text().strip()
		for spec in bike_specs:
			content = w(spec)
			if "FRAME" in content.text():
				data["frame"] = content.text().strip()
			if "REAR DERAILLEUR" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "FRONT DERAILLEUR" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "CHAIN" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "WHEELS" in content.text():
				data["wheelset"] += content.text().strip() + "\n"
			if "TIRES" in content.text():
				data["wheelset"] += content.text().strip() + "\n"
		desc = w(".shop-product-short-description p")
		if desc:
			data["description"] += w(desc).text().strip()
		for spec in desc:
			content = w(spec)
			if "FRAME" in content.text():
				data["frame"] = content.text().strip()
			if "REAR DERAILLEUR" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "FRONT DERAILLEUR" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "CHAIN" in content.text():
				data["gearset"] += content.text().strip() + "\n"
			if "WHEELS" in content.text():
				data["wheelset"] += content.text().strip() + "\n"
			if "TIRES" in content.text():
				data["wheelset"] += content.text().strip() + "\n"
		data["wheelset"] = data["wheelset"].replace("N/A", "")
		data["gearset"] = data["gearset"].replace("N/A", "")
		data["frame"] = data["frame"].replace("N/A", "")
		data["description"] = data["description"].replace("N/A", "")
		
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
