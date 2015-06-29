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

	next_page = w("a.next").eq(0)
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w("a.product-image")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.cykelexperten.dk'
	w = pq(req["html"])

	is_bike = w(".product-name h1")
	if is_bike:
		external_source_id = w("input[name='product']").attr("value")
		if external_source_id:
			data["external_source_id"] = external_source_id
		name = w(".product-name h1").text().strip()
		if name:
			data["name"] = name
			data["brand"] = name.split(" ")[0]
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "DKK"
		image = w("p.product-image a").attr("href")
		if image:
			data["image"] = image
		new_price = w("p.special-price span.price").text().strip()
		if new_price:
			data["price"] = new_price.replace(",", "").replace(".", "")[:-5]
			disc_price = w("p.old-price span.price").text().strip()
			disc_price = disc_price.replace(",", "").replace(".", "")[:-5]
			data["discounted_price"] = disc_price
		else:
			price = w("span.regular-price span.price").text().strip()
			price = price.replace(",", "").replace(".", "")[:-5]
			data["price"] = price
			data["discounted_price"] = price
		
		availability = dict()
		sizes = w("select option")
		print sizes
		for size in sizes:
			content = w(size)
			if "venligst" not in content.text().strip():
				availability[content.text().strip()] = "Available to Order"
		
		data["availability"] = availability
		bike_specs = w("div.std p span")
		if bike_specs:
			data["description"] += w(bike_specs).text().strip()
		tech_specs = str()
		for spec in bike_specs:
			content = w(spec)
			tech_specs += content.text().strip() + "||"
			if "frame" in content.text().lower():
				data["frame"] = content.text().strip()
			if "rear derailleur" in content.text().lower():
				data["gearset"] += content.text().strip() + "\n"
			if "front derailleur" in content.text().lower():
				data["gearset"] += content.text().strip() + "\n"
			if "chain" in content.text().lower():
				data["gearset"] += content.text().strip() + "\n"
			if "wheels" in content.text().lower():
				data["wheelset"] += content.text().strip() + "\n"
			if "tires" in content.text().lower():
				data["wheelset"] += content.text().strip() + "\n"
		data["wheelset"] = data["wheelset"].replace("N/A", "")
		data["gearset"] = data["gearset"].replace("N/A", "")
		data["frame"] = data["frame"].replace("N/A", "")
		data["description"] = data["description"].replace("N/A", "")
		data["tech_specs"] = tech_specs
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
