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
		urls.add(domain + next_page.attr("href"))

	bikes = w(".adv-search-item-container>a")
	for item in bikes:
		item = pq(item)
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
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "GBP"
		image = w("a.MIV[rel='1']").attr("href")
		if image:
			data["image"] = domain + image
		
		brand = w("div.brandImg img").attr("alt")
		if brand:
			data["brand"] = brand
		new_price = w("#ProductDetail21_pricing1_lblSalePrice").text().strip()
		old_price = w('#ProductDetail21_pricing1_lblPrice').text().strip()
		if old_price:
			data["price"] = old_price[1:].replace(",", "")
			data["discounted_price"] = new_price[1:].replace(",", "")
		else:
			data["price"] = new_price[1:].replace(",", "")
			data["discounted_price"] = new_price[1:].replace(",", "")
		
		external_source_id = w("li.store>div").eq(0).attr("title")
		if external_source_id:
			data["external_source_id"] = external_source_id

		availability = dict()
		sizes = w("ul.clAttributeGrid")
		for size in sizes:
			item = pq(size)
			size = item.find("li.name").text().strip()
			available = item.find("li.stock").text().strip()
			availability[size.split(",")[0]] = available
		
		data["availability"] = availability
		
		bike_specs = w(".container").eq(1).find("li")
		for item in bike_specs:
			label = pq(item).text().strip()
			if "Frame" in label:
				data["frame"] = label
			if "Shifters" in label:
				data["gearset"] = label
			if "Tires" in label:
				data["wheelset"] = label
		
		desc = w(".container.prodDesc").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
