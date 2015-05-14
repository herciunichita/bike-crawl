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
		urls.add(next_page.attr("href"))

	bikes = w("a.product_title")
	for item in bikes:
		item = pq(item)
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
			data["year"] = re.search(r"\d{4}", name).group(1)
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
		old_price = w("span.product_price_was span.GBP").text().strip()
		if old_price:
			actual_price = re.search(r".*(\d+\,*\d+\.\d+)", price)
			data["price"] = actual_price.group(1).replace(",", "")
			disc_price = w("span#product_price_sale span.GBP").text().strip()
			disc_price = re.match(r".*(\d+\,*\d+\.\d+)", disc_price)
			data["discounted_price"] = disc_price.group(1).replace(",", "")
		else:
			price = w("span#product_price_sale span.GBP").text().strip()
			price = re.match(r".*(\d+\,*\d+\.\d+)", price)
			data["price"] = price.group(1).replace(",", "")
			data["discounted_price"] = price.group(1).replace(",", "")

		desc = w("#overview_tab_content").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
