#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re
from sys import stderr

def extract_urls(req):
	urls = set()

	domain = 'http://www.chainreactioncycles.com'
	w = pq(req["html"])

	next_page = w(".pagination>a:last")
	active = w(".pagination>a:last").attr("class")
	if active != "active":
		if next_page:
			urls.add(domain + next_page.attr("href"))

	bikes = w("#show_grid_list .description>a")
	for item in bikes:
		item = pq(item)
		urls.add(domain + item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.chainreactioncycles.com'
	w = pq(req["html"])

	is_bike = w(".product_title h1")
	if is_bike:
		name = w(".product_title h1").text().strip()
		if name:
			data["name"] = name
			data["year"] = re.search(r"(\d{4})", name).group(1) if re.search(r"(\d{4})", name) else "N/A"
			data["brand"] = name.split(" ")[0]
		data["currency"] = "EUR"
		external_source_id = w("input.showfitguidepopup").attr("value")
		if external_source_id:
			data["external_source_id"] = external_source_id.replace("prod", "")
		image = w(".s7thumb[state='selected']").attr("style")
		if image:
			data["image"] = re.search(r"(url\(.*\))", image).group(1).replace("url(\"", "").replace("?fit=constrain,1&wid=56&hei=56&fmt=jpg\")", "")
		old_price = w("li.rrpamount span").text().strip()
		if old_price:
			actual_price = re.search(r"(\d+\.\d+)", old_price)
			data["price"] = actual_price.group(1)
			disc_price = w("span#crc_product_rp").text().strip()
			disc_price = re.search(r"(\d+\.\d+)", disc_price)
			data["discounted_price"] = disc_price.group(1)
		else:
			price = w("span#crc_product_rp").text().strip()
			price = re.search(r"(\d+\.\d+)", price)
			if price:
				data["price"] = price.group(1)
				data["discounted_price"] = price.group(1)

		availability = dict()
		sizes = w("#FramesSize div.size_countbox")
		for size in sizes:
			item = pq(size)
			outofstock = w("p.out_stock inventorystatus")
			if outofstock:
				availability[item.text().replace('"', '').strip()] = "Out of Stock"
			else:
				availability[item.text().replace('"', '').strip()] = "In Stock"
		
		data["availability"] = availability

		specs = w(".short_desc li")
		tech_specs = str()
		for item in specs:
			content = w(item)
			tech_specs += content.text().strip() + "||"
			if "Frame" in content.text():
				data["frame"] = content.text().strip()
			elif "Tyres" in content.text():
				data["wheelset"] = content.text().strip()
			elif "Cassette" in content.text():
				data["gearset"] = value

		data["tech_specs"] = tech_specs
		desc = w(".short_desc p").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
