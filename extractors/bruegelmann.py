#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()
	w = pq(req["html"])
	total_pages = w("div#topPager.productFilterOverviewPage.productOverviewPage div.row div.block.right div#totalPages").attr("data-totalpages")
	if total_pages:
		page = int(re.match(r".+page=(\d+)", req["url"]).group(1))
		if page + 1 <= total_pages:
			urls.add(req["url"].replace("page="+ str(page), "page="+ str(page+1)))
		
	

	bikes = w("div.productBox div.row.productItem.noMargin div.productItemContainer a.productLink")
	
	
	#next_page = w(".next_page.page_num").eq(0)
	#if next_page:
	#	urls.add(next_page.attr("href"))

	#bikes = w("a.product_title")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	w = pq(req["html"])

	is_bike = w("div#ProductsInfo h1")
	if is_bike:
		name = w("div#ProductsInfo h1").text().strip()
		if name:
			data["name"] = name
		data["currency"] = "EUR"
		brand = w("div#ProductsInfo a img").attr("title")
		if brand:
			data["brand"] = brand
		image = w("div.mainImageContainer img.mainImage").attr("src")
		if image:
			data["image"] = image
		new_price = w("span.smartFontBold22.red").text().strip()
		if new_price:
			actual_price = re.search(r"(\d+\.*\d+)\.*", new_price)
			data["discounted_price"] = actual_price.group(1).replace(".", "")
			old_price = w("span.smartFontBold22.oldPrice__invalid").text().strip()
			disc_price = re.search(r"(\d+\.*\d+).*", old_price)
			data["price"] = disc_price.group(1).replace(".", "")
		else:
			price = w("span.smartFontBold22").text().strip()
			price = re.search(r"(\d+\.*\d+).*", price)
			data["price"] = price.group(1).replace(".", "")
			data["discounted_price"] = price.group(1).replace(".", "")

		external_source_id = w("span.productNo").text().strip()
		external_source_id = re.search(r"(\d+)", external_source_id)
		data["external_source_id"] = external_source_id.group(1)

		availability = dict()
		sizes = w("select.availableVariations option.variation[data-available='true']")
		for size in sizes:
			item = pq(size)
			size = item.text().split(" ")
			if size[1] == "cm":
				data["size_measure"] = "cm"
			else:
				data["size_measure"] = "inch"
			availability[size[0]] = "Available to Order"

		data["availability"] = availability	

		bike_specs = w("div#tabs-2 ol")
		tech_specs = str()
		for item in bike_specs:
			item = pq(item)
			label = item.find('lh').text().strip()
			item_data = item.find('ul li').text().strip() or item.find('li').text().strip()	
			tech_specs += label + ":" + item_data + "||"	
			if label:
				if "Rahmen" in label:
					data["frame"] = item_data
				
				if u"Reifen vorne" in label:
					data["wheelset"] = item_data
				if "Schaltung" in label:
					data["gearset"] = item_data
			else:
				label = item.find('span.title').text().strip()
				item_data = item_data.replace(label, "").strip()
				
				if "Einsatzzweck" in label:
					data["type"] = item_data
				if u"Modelljahr" in label:
					data["year"] = item_data
		data["tech_specs"] = tech_specs
			
		desc = w("p[itemprop='description']").text().strip()
		if desc:
			data["description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
