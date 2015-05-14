#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.bike24.de/'
	w = pq(req["html"])

	last_page = w("td.contentbold[align='right']>a.contentbold:last").eq(0).text().strip()
	current_page = w("a.redbold").eq(0)
	if last_page:
		last_page_no = int(last_page)
		if current_page:
			current_page_no = int(current_page.text().strip())
			if current_page_no < last_page_no:
				urls.add(domain + current_page.attr("href").replace("page=" + str(current_page_no), "page=" + str(current_page_no + 1)) + + ';lang=2')

	bikes = w("h1>a")
	for item in bikes:
		item = pq(item)
		urls.add(domain + item.attr("href")+ ';lang=2')
	return list(urls)

def extract_data(req):
	data = bike
	domain = 'http://www.bike24.de/'
	w = pq(req["html"])

	is_bike = w(".pd-headline>h1")
	if is_bike:
		name = w(".pd-headline>h1").text().strip()
		if name:
			data["name"] = name
		data["currency"] = "EUR"
		image = w("a#zoom1").attr("href")
		if image:
			data["image"] = image
		old_price = w("span.price")
		if old_price:
			old_price = old_price.text().strip()
			actual_price = re.match(r"(\d+\.*\d+\,\d+).*", old_price)
			data["price"] = actual_price.group(1).replace(".", "").replace(",", ".")
			data["discounted_price"] = actual_price.group(1).replace(".", "").replace(",", ".")
		availability = w("select.selectbox option")
		size = list()
		for item in availability:
			content = w(item)
			if "cm" in content.text():
				data["size_measure"] = "cm"
			else:
				data["size_measure"] = "inch"
			size.append(content.text()[:2]) 
		bike_specs = w("table.content tbody tr")
		for item in bike_specs:
			item = pq(item)
			#print item
			label = item.find('td.pd-datasheet-label').text().strip()
			item_data = item.find('td').eq(1).text().strip()
			if label == "Manufacturer:":
				data["brand"] = item_data
			if label == "Item Code:":
				data["id"] = item_data
			if label == "Frame:":
				data["frame"] = item_data
			if label == "Tires:":
				data["wheelset"] = item_data
			if label == "Year:":
				data["year"] = item_data
			if label == "Shifter:":
				data["gearset"] = item_data
		
		desc = w("div.pd-description").text().strip()
		if desc:
			data["description"] = desc
		data["provider_id"] = domain
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
