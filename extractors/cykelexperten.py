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
		print next_page.attr("href")
		urls.add(next_page.attr("href"))

	bikes = w(".shop-catalog-product-title a")
	for item in bikes:
		item = pq(item)
		print item.attr("href")
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.cykelexperten.dk'
	w = pq(req["html"])

	is_bike = w("h1.shop-product-title")
	if is_bike:
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

		bike_specs = w(".shop-product-description")
		if bike_specs:
			data["description"] = bike_specs.text().strip()
		desc = w("shop-product-short-description").text().strip()
		if desc:
			data["description"] = data["description"] + desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
