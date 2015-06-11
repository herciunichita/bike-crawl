#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'www.wiggle.co.uk'
	w = pq(req["html"])

	next_pages = w("div.pagination-links>a")
	for next_page in next_pages:
		next_page = w(next_page)
		if ">" == next_page.text().strip():
			urls.add(next_page.attr("href"))

	bikes = w("div.list-detail a.productlink")
	for item in bikes:
		item = pq(item)

		urls.add(item.attr("href"))

	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.wheelbase.co.uk'
	w = pq(req["html"])

	is_bike = w("h1#product-display-name")
	if is_bike:
		name = w("h1#product-display-name").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "EUR"
		data["external_source_id"] = w("span#hidden-id").text().strip()
		brand = w("span[itemprop='manufacturer']").text().strip()
		if brand:
			data["brand"] = brand
		image = w(".zoomPad>img").attr("src")
		if image:
			data["image"] = image[2:]
		old_price = w("div.was-price").text().strip()
		if old_price:
			data["price"] = old_price[1:].replace(",", "")
			data["discounted_price"] = w("div.unit-price").text().strip()[1:].replace(",", "")
		else:
			data["discounted_price"] = w("div.unit-price").text().strip()[1:].replace(",", "")
			data["price"] = w("div.unit-price").text().strip()[1:].replace(",", "")

		availability = dict()
		sizes = w("select.product-options>option")
		for size in sizes:
			item = pq(size)
			size = item.attr("data-size")
			if size:
				if item.attr("data-is-in-stock") == "True":
					availability[size] = "In Stock"
				else:
					availability[size] = "Out of Stock"
		data["availability"] = availability

		bike_specs = w("table.product-attributes tr")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('th').text().strip()
			item_data = item.find('tr').text().strip()
		
			if "Model Year" in label:
				data["year"] = item_data
			if "Frame" in label:
				data["frame"] += item_data
			if "Wheelset" in label:
				data["wheelset"] += item_data
			if "Tyres" in label:
				data["wheelset"] += item_data
			if "Derailleur" in label:
				data["gearset"] += item_data
		data["gearset"] = data["gearset"].replace("N/A", "")
		data["wheelset"] = data["gearset"].replace("N/A", "")
		data["gearset"] = data["gearset"].replace("N/A", "")
		
		desc = w("div.proddesc").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
