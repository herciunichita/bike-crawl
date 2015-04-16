#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re



def extract_urls(req):
        urls = set()

        domain = 'http://www.evanscycles.com'
        w = pq(req["html"])

	cats = w("h2 a")

	for item in cats:
		item = pq(item)

		urls.add(domain + item.attr("href").replace(domain, ""))

	next_page = w(".next_page:first").attr("href")
	if next_page:
		urls.add(domain + next_page)
		
	return list(urls)


def extract_data(req):
        data = deepcopy(bike)
        w = pq(req["html"])

	is_bike = w(".product-page")
	if not is_bike:
		return {}

	data["name"] = w("h1.main-title.product-page").text()
	discount = w("div.main-title-price div.product_price_containter span.product_price")
	price = w("div.main-title-price div.product_price_containter span.one_product_price")
	if discount:
		price = w("div.main-title-price div.product_price_containter span.product_base_price strike").text()
		data["discounted_price"] = re.match(r"(\D+)([0-9\.]+)", discount.text()).group(2)
		price = re.match(r"(\D+)([0-9\.]+)", price)
		data["price"] = price.group(2)
		data["currency"] = price.group(1)
	elif price:
		price = re.match(r"(\D+)([0-9\.]+)", price.text())
                data["price"] = price.group(2)
                data["currency"] = price.group(1)
		data["discounted_price"] = data["price"]
	data["id"] = w("div#product_code").text().replace("Product code:", "")
	data["image"] = w("img#main_product_image").attr("src")
	data["bike_description"] = w("div#product_description").text()
	data["bike_brand"] = w("div#product_brand_logo a").attr("href").replace("/brands/", "")
	data["url"] = req["url"]
	frame = w("dl#product_features dt:contains('Frame:')").attr("class")
	if frame:
		data["frame_name"] = w("dl#product_features dd."+ frame).text()

	gears = w("dl#product_features dt:contains('Number of Gears:')").attr("class")
	if gears:
		data["gears"] = w("dl#product_features dd."+ gears).text()
	
	data["type"] = w(".current_category a").text().replace(" Bikes", "")	
	g_set = w("dl#product_features dt:contains('Shifters:')").attr("class")
	if g_set:
		data["gearset"] = w("dl#product_features dd."+ g_set).text()
	w_set = w("dl#product_features dt:contains('Wheelset:')").attr("class")
	if w_set:
		data["wheelset"] = w("dl#product_features dd."+ w_set).text()

	available = w("div#select_and_buy_buttons a img")
	data["availability"] = "A" if available else "O"

	return data