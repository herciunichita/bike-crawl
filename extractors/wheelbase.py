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
		data["currency"] = "GBP"
		image = w(".product-image.no-gallery>a>img").attr("src")
		if image:
			data["image"] = image
		old_price = w("span.finance-cost-of-goods").text().strip()
		if old_price:
			data["price"] = old_price
			data["discounted_price"] = old_price

		bike_type = w(".container>ul>li").eq(3).text().strip()
		if bike_type:
			data["type"] = bike_type
		bike_specs = w(".product-attribute-specs-table>tbody>tr")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('.label').text().strip()
			item_data = item.find('.data.last').text().strip()
			if label == "SKU / GTIN":
				data["id"] = item_data
			if label == "FRAME":
				data["frame_name"] = item_data
		
		desc = w(".tab-section").eq(0).text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
