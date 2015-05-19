#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.bruegelmann.de'
	w = pq(req["html"])

	next_page = w(".next_page.page_num").eq(0)
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w("a.product_title")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.bruegelmann.de'
	w = pq(req["html"])

	is_bike = w("div#ProductsInfo h1")
	if is_bike:
		data["provider_store"] = domain
		name = w("div#ProductsInfo h1").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "EUR"
		brand = ("div#ProductsInfo>a").attr("title")
		image = w("div.center-block.box.root.active img").attr("src")
		if image:
			data["image"] = image
		new_price = w("span.smartFontBold22.red").text().strip()
		if new_price:
			actual_price = re.search(r"(\d+\.*\d+)\.*", price)
			data["discounted_price"] = actual_price.group(1).replace(".", "")
			old_price = w("span.smartFontBold22.oldPrice__invalid").text().strip()
			disc_price = re.search(r"(\d+\.*\d+).*", disc_price)
			data["price"] = disc_price.group(1).replace(".", "")
		else:
			price = w("span.smartFontBold22").text().strip()
			price = re.search(r"(\d+\.*\d+).*", price)
			data["price"] = price.group(1).replace(".", "")
			data["discounted_price"] = price.group(1).replace(".", "")

		external_source_id = w("span.productNo").text().strip()
		external_source_id = re.search(r"(\d+)", external_source_id)
		data["external_source_id"] = external_source_id.group(1)

		availability = dict()
		sizes = w("li.variation.hideItem")
		for size in sizes:
			item = pq(size)
			size = item.text().split(" ")
			if size[1] == "cm":
				data["size_measure"] = "cm"
			else:
				data["size_measure"] = "inch"
			availability[size[0]] = "Available to Order"

		data["availability"] = availability

		bike_specs = w("div#tabs-2 ol")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('lh').text().strip()
			item_data = item.find('li').text().strip()
			if label:
				if "Rahmen" in label:
					data["frame"] = item_data
				if "Reifen" in label:
					data["wheelset"] = item_data
				if "Schaltung" in label:
					data["gearset"] = item_data
		desc = w("p[itemprop='description']").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
