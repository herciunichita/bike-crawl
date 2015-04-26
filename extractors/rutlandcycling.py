#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.rutlandcycling.com'
	w = pq(req["html"])

	next_page = w("a#lnkNextTop")
	if next_page:
		print domain + next_page.attr("href")	
		urls.add(domain + next_page.attr("href"))

	bikes = w(".adv-search-item-container>a")
	for item in bikes:
		item = pq(item)
		print domain + item.attr("href")
		urls.add(domain + item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.rutlandcycling.com'
	w = pq(req["html"])

	is_bike = w(".nameBox>div>h1")
	if is_bike:
		name = w(".nameBox>div>h1").text().strip()
		if name:
			data["name"] = name
		data["currency"] = "GBP"
		image = w(".flexsliderMIV .flex-active-slide>a").attr("href")
		if image:
			data["image"] = image
		new_price = w("#ProductDetail21_pricing1_lblSalePrice").text().strip()
		old_price = w('#ProductDetail21_pricing1_lblPrice').text().strip()
		if old_price:
			data["price"] = old_price[1:].replace(",", "")
			data["discounted_price"] = new_price[1:].replace(",", "")
		else:
			data["price"] = new_price[1:].replace(",", "")
			data["discounted_price"] = new_price[1:].replace(",", "")
		
		desc = w(".container").eq(1).text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
