#!/usr/bin/env python


from pyquery import PyQuery as pq
from bike import bike
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.jejamescycles.co.uk'
	w = pq(req["html"])

	# ugly hack for testing purposes. avoid this 'if'
	if req["url"] == "http://www.jejamescycles.co.uk/bikes-cp1.html":
		cats = w("#left .menu>li>a")

		for item in cats:
			item = pq(item)
			urls.add(item.attr("href"))
		return list(urls)

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
	data = bike
	domain = 'http://www.jejamescycles.co.uk'
	w = pq(req["html"])

	is_bike = w(".product-info>h1>span")
	if is_bike:
		name = w(".product-info>h1>span")
		data["provider_id"] = domain
		if name:
			data["name"] = name.text()
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
		bike_type = w(".info-box>a").eq(1).text()
		if bike_type:
			data["type"] = bike_type
		available = w("span[itemprop='availability'] img").attr("src")
		if available:
			if available == "http://www.jejamescycles.co.uk/images/zerostock.jpg":
				data["availability"] = "O"
			else:
				data["availability"] = "A"
		product_code = w("input[name='prodID']").attr("value")
		if product_code:
			data["id"] = product_code
		desc = w("div.description").text().strip()
		if desc:
			data["bike_description"] = desc
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
