#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.boc24.de'
	w = pq(req["html"])
	next_page = w("div.right_arrow_container a.reloadSearchContentPerAjaxLink").eq(0)
	if next_page:
		url = "https://www.boc24.de/webapp/wcs/stores/servlet/" + next_page.attr("rel")
		print url
		urls.add(url)

	bikes = w(".product_description a")
	for item in bikes:
		item = pq(item)
		print item.attr("href")
		urls.add(item.attr("href"))
	return list(urls)

def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.boc24.de'
	w = pq(req["html"])

	is_bike = w("h1.prod-detail-title")
	if is_bike:
		data["provider_store"] = domain
		data["external_source_id"] = w(".prod-detail-left").clone().children().remove().end().text().replace("(Art-Nr:", "").replace(")", "")
		name = w("h1.prod-detail-title").text().strip()
		if name:
			data["name"] = name
			data["brand"] = name.split(" ")[0]
		data["currency"] = "EUR"
		image = w("div.prod-image-box img").attr("src")
		if image:
			data["image"] = domain + image
		old_price = w("c_product_detail_price_old").text().strip()
		if old_price: 
			data["price"] = old_price[1:].replace(".", "").replace(",", ".")
			data["discounted_price"] = w("span#c_product_detail_price").text().strip().replace(".", "").replace(",", ".")
		else:
			data["discounted_price"] = w("span#c_product_detail_price").text().strip().replace(".", "").replace(",", ".")
			data["price"] = data["discounted_price"]

		availability = dict()
		wheel_sizes = w("div.c_variations_button_div tr")
		for size in wheel_sizes:
			content = w(size).text()
			if content != "":
				availability[content] = "Available to Order"

		data["availability"] = availability
		bike_specs = w("div.c_tabcontainer_attribute_row")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('.c_tabcontainer_attribute_name').text().strip()
			item_data = item.find('.c_tabcontainer_attribute_value').text().strip()
			if label == "Modelljahr":
				data["year"] = item_data
			if label == "Rahmen":
				data["frame"] = item_data
			if label == "Schaltwerk":
				data["gearset"] = item_data
			if "Reifen" in label:
				data["wheelset"] = item_data
		
		desc = w("p.text_small_normal").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
