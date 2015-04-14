#!/usr/bin/env python


from pyquery import PyQuery as pq
from bike import bike
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.winstanleysbikes.co.uk'
	w = pq(req["html"])

	# ugly hack for testing purposes. avoid this 'if'
	if req["url"] == "http://www.winstanleysbikes.co.uk/category/336/Bikes":
		cats = w("table#catprods_hdr td.column_main a.links_main")

		for item in cats:
			item = pq(item)

			urls.add(domain + item.attr("href"))
		return list(urls)

	next_page = w("input.buttonstyle[name='next']")
	if next_page:
		urls.add(next_page.attr("onclick").replace("parent.location.href=", "").replace("'", ""))

	bikes = w("table#catprods_tbl a.links_main")
	for item in bikes:
		item = pq(item)

		urls.add(domain + item.attr("href"))

	return list(urls)


def extract_data(req):
	data = bike
	domain = 'http://www.winstanleysbikes.co.uk'
	w = pq(req["html"])

	is_bike = w("table#prod_tbl.sectionborder_main img")
	if is_bike:
		rows = w("table#item_Tbl.column_main tr")
		for row in rows:
			content = w(row)
			if "Name" in content.children('td').eq(0).text():
				data["name"] = content.children('td').eq(1).text()
			if "Availability" in content.children('td').eq(0).text():
				if "In stock" in content.children('td').eq(1).text():
					data["availability"] = "A"
				else:
					data["availability"] = "O"
			if "Size" in content.children('td').eq(0).text():
				size = re.match(r"(\d+)(.+)", content.children('td').eq(1).text())
				if size:
					data["size_value"] = size.group(1)
					if size.group(2) != "cm":
						data["size_measure"] = "inch"
			if "Product Code" in content.children('td').eq(0).text():
				data["id"] = content.children('td').eq(1).text()
			if "Price" in content.children('td').eq(0).text():
				currency = re.match(r"(^[A-Z]{3}).*", content.children('td').eq(1).text())
				if currency:
					data["currency"] = currency.group(1)
				price = re.match(r".*(\d{3,6}\.\d+),", content.children('td').eq(1).text())
				if price:
					data["price"] = price.group(1)
					data["discounted_price"] = price.group(1)
		data["provider_id"] = domain
		image = w(".small_main>img").eq(0).attr("src")
		if image:
			data["image"] = domain + image
		bike_description = 
	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
