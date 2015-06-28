#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.westbrookcycles.co.uk'
	w = pq(req["html"])

	next_page = w(".next_page.page_num").eq(0)
	if next_page:
		#print next_page.attr("href")
		urls.add(next_page.attr("href"))

	bikes = w("a.product_title")
	for item in bikes:
		item = pq(item)
		#print item.attr("href")
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.westbrookcycles.co.uk'
	w = pq(req["html"])

	is_bike = w("span#product_title")
	if is_bike:
		name = w("span#product_title").text().strip()
		if name:
			data["name"] = name
			year = re.search(r"(\d{4})", name)
			if year:
				data["year"] = year.group(1)
		data["currency"] = "GBP"
		external_source_id = w("#parent_product_id").attr("value")
		if external_source_id:
			data["external_source_id"] = external_source_id

		brand = w("#breadcrumb_container").eq(3).text().strip()
		if brand:
			data["brand"] = brand

		availability_dict = dict()
		availability = w("div.product_option_div select").eq(0)
		if availability:
			options = pq(availability).find("option")
			print options
			for option in options:
				item = pq(option)
				itemtext = item.text().strip()
				if itemtext != "Choose a Size":
					if "Out of Stock" in itemtext:
						size = itemtext.split("-")
						availability_dict[size[0].strip()] = size[1].strip()
					else:
						availability_dict[itemtext] = "In Stock"

		data["availability"] = availability_dict

		image = w("a#product_zoom_image").attr("href")
		if image:
			data["image"] = domain + image
		old_price = w("span.product_price_was span.GBP").eq(0).text().strip()
		if old_price:
			data["price"] = old_price.replace(",", "")[1:]
			disc_price = w("span#product_price_sale span.GBP").eq(0).text().strip()
			data["discounted_price"] = disc_price.replace(",", "")[1:]
		else:
			price = w("span#product_price_sale span.GBP").eq(0).text().strip()
			data["price"] = price.replace(",", "")[1:]
			data["discounted_price"] = price.replace(",", "")[1:]

		tech_specs = str()
		specs = w("#overview_tab_content li")
		for item in specs:
			content = w(item)
			tech_specs += content.text().strip() + "||"
			if "frame" in content.text().strip().lower():
				data["frame"] = content.text().strip()
			if "wheel" in content.text().strip().lower():
				data["wheelset"] = content.text().strip()
			if "derailleur" in content.text().strip().lower():
				data["gearset"] = content.text().strip()

		data["tech_specs"] = tech_specs
		desc = w("#overview_tab_content").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
