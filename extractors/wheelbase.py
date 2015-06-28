#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.wheelbase.co.uk'
	w = pq(req["html"])

	next_page = w("a.button.next.i-next")
	if next_page:
		urls.add(next_page.attr("href"))

	bikes = w(".product-name>a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.wheelbase.co.uk'
	w = pq(req["html"])

	is_bike = w(".col-sm-4.product-shop>h1")
	if is_bike:
		name = w(".col-sm-4.product-shop>h1").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "GBP"
		
		brand = w("span.brand").text().strip()
		if brand:
			data["brand"] = brand
		image = w(".product-image.no-gallery>a>img").attr("src")
		if image:
			data["image"] = image
		old_price = w("span.finance-cost-of-goods").text().strip()
		if old_price:
			data["price"] = old_price
			data["discounted_price"] = old_price

		availability = dict()
		sizes = w("#super-product-table tbody tr")
		for size in sizes:
			item = pq(size)
			size = item.find("td").eq(0).text().strip()
			availability[size] = item.find("td").eq(1).text().strip()
		data["availability"] = availability

		bike_specs = w("#product-attribute-specs-table>tbody>tr")
		tech_specs = str()
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('.label').text().strip()
			item_data = item.find('.data').text().strip()
			tech_specs += label + ":" + item_data + "||"
			if "SKU" in label:
				data["external_source_id"] = item_data
			if "Frame" in label:
				data["frame"] = item_data
			if "Tyre" in label:
				data["wheelset"] = item_data
			if "Shifter" in label:
				data["gearset"] = item_data
		data["tech_specs"] = tech_specs
		desc = w(".tab-section").eq(0).text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
