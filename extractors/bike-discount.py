#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
from json import loads
import re

domain = 'http://www.bike-discount.de'


def extract_urls(req):
    	urls = set()

    	w = pq(req["html"])
    
    	more = w("div#infinitescroll span.btn.red")

	wv_id = w("body.warengruppe.warengruppe-detail").attr("data-vw-id")
	if wv_id:
		url = "http://www.bike-discount.de/json.php?service=getProductsContent&page=0&praesenz=1&vw_type=warengruppe&vw_name=detail&lang=en&pfrom=0&pto=0&vw_id={0}&order_by=ranking".format(wv_id)
		urls.add(url)
		return list(urls)
	if len(req["html"]) < 50:
		return list(urls)
	try:
		data = loads(req["html"])
	except ValueError:
		return list(urls)
	current_page = re.match(r".+page=(\d+)&", req["url"]).group(1)

	urls.add(req["url"].replace("page={0}&".format(current_page), "page={0}&".format(int(current_page ) + 1)))

	w = pq(data["data"])
	
	for item in w("div.product-box div.title-and-description h3.title a"):
		item = pq(item)
		urls.add(domain + item.attr("href"))

	return list(urls)

	
def extract_data(req):
    	data = deepcopy(bike)
    	w = pq(req["html"])

	is_bike = w(".rightBox")
	if not is_bike:
		return {}
	data["brand"] = w("span.manufacturer:first").text()
	data["name"] = w("h1.product-title meta[itemprop='name']").attr("content").strip()
	data["external_source_id"] = w("body.artikel.artikel-detail").attr("data-vw-id")
	data["currency"] = "EUR"
	price = w("table.product-price tr.uvp td").text()
	if price:
		data["price"] = re.match(r"\D+([0-9\.]+)", price).group(1).replace(",", ".")
	else:
		data["price"] = w("meta[itemprop='price']").attr("content")
	data["discounted_price"] = w("meta[itemprop='price']").attr("content")

	data["image"] = domain + w("div.productimage-wrapper.responsive_image a#productimage").attr("href")

	available = w("div#variantselector tr.variant")
	availability = dict()
	for size in available:
		content = w(size)
		size = content.find('td.variant_text>label').text()
		if "cm" in size:
			data["size_measure"] = "cm"
		else:
			data["size_measure"] = "inch"
		status_text = content.find('td.delivery.last').text()
		if "In stock" in status_text:
			availability_text = "In Stock"
		elif "ordered for you" in status_text:
			availability_text = "Available to Order"
		elif "take notice of" in status_text:
			availability_text = "Available to Order"
		else:
			availability_text = "Out of Stock"
		availability[size[:2]] = availability_text

	data["availability"] = availability

	data["description"] = w("div.default.articletext").text().strip()

	year = w("div.variantMaster" + data["external_source_id"] + ".variantElement.variante div.additional-product-nos div.additional-product-no:contains('Model year:')").eq(0).text()
	if year:
		data["year"] = year.replace("Model year:", "").strip()

	attrs = w("div.articleattributes table.multieigenschaften.datagrid tr")
	tech_specs = str()
	for item in attrs:
		item = pq(item)
		name = item.find(".name").text().strip()
		value = item.find(".value").text()
		tech_specs += name + ":" + value + "||"
		if name == "Frame":
			data["frame"] = value
		elif name == "Wheelset":
			data["wheelset"] = value
		elif name == "Cassette":
			data["gearset"] = value
	data["tech_specs"] = tech_specs
	
	return data
