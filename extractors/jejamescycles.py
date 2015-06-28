#!/usr/bin/env python


from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.jejamescycles.co.uk'
	w = pq(req["html"])

	next_pages = w(".pag>li>a")
	for next_page in next_pages:
		next_page_pq = w(next_page)
		if "Next" in next_page_pq.text():
			urls.add(next_page_pq.attr("href"))

	bikes = w(".column1>li>h3>a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	bikes = w(".column2>li>h3>a")
	for item in bikes:
		item = pq(item)
		urls.add(item.attr("href"))
	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	domain = 'http://www.jejamescycles.co.uk'
	w = pq(req["html"])

	is_bike = w(".product-info>h1>span")
	if is_bike:
		name = w(".product-info>h1>span")
		
		if name:
			data["name"] = name.text()
			year = re.search(r"(\d{4})", name.text() or "")
			if year:
				data["year"] = year.group(1)
		data["currency"] = "GBP"
		image = w("a#large-image").attr("href")
		if image:
			data["image"] = image
		price = w("div.product-info span.price").text()
		
		actual_price = re.match(r".(\d+\.\d+)", price)
		saving = w("div.product-info span.saving").text()
		if saving:
			data["discounted_price"] = actual_price.group(1)
			full_price = w("div.product-info span.rrp").text()
			if full_price:
				full_price = re.match(r".{6}(\d+\.\d+)", full_price)
				data["price"] = full_price.group(1)
		else:
			data["price"] = actual_price.group(1)
			data["discounted_price"] = actual_price.group(1)
		brand = w(".info-box>a").eq(0).text()
		if brand:
			data["brand"] = brand
		rows = w("tr[itemprop]")
		sizes = dict()
		for row in rows:
			content = w(row)
			size = content.find("td").eq(1).text()
			size = re.search(r"(\d+)(\w{2})", size)
			if size:
				if "instock" in content.find("span[itemprop='availability'] img").attr("src"):
					sizes[size.group(1)] = "Available"
				if "available-to-order" in content.find("span[itemprop='availability'] img").attr("src"):
					sizes[size.group(1)] = "Available to Order"
				if "out-of-stock" in content.find("span[itemprop='availability'] img").attr("src"):
					sizes[size.group(1)] = "Out of Stock"
				data["size_measure"] = size.group(2)
		data["availability"] = sizes
		product_code = w("input[name='prodID']").attr("value")
		if product_code:
			data["external_source_id"] = product_code
		desc = w("div.description p").text().strip()
		if desc:
			data["description"] = desc
		specs = w("div.specification ul li")
		tech_specs = str()
		for spec in specs:
			content = w(spec)
			tech_specs += content.text().strip() + "||"
			if "Frame" in content.text():
				data["frame"] = content.text().replace("Frame", "").strip()
			if "Shifters" in content.text():
				data["gearset"] += content.text().strip().replace("N/A", "") + "\n" 
			if "Rear derailleur" in content.text():
				data["gearset"] += content.text().strip().replace("N/A", "") + "\n"
			if "Front derailleur" in content.text():
				data["gearset"] += content.text().strip().replace("N/A", "") + "\n"
			if "Chain" in content.text():
				data["gearset"] += content.text().strip().replace("N/A", "") + "\n"
			if "Wheels" in content.text():
				data["wheelset"] += content.text().strip().replace("N/A", "") + "\n"
			if "Tire" in content.text():
				data["wheelset"] += content.text().strip().replace("N/A", "") + "\n"
		data["tech_specs"] = tech_specs
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
