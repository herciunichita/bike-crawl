#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

def extract_urls(req):
	urls = set()

	domain = 'http://www.winstanleysbikes.co.uk'
	w = pq(req["html"])

	next_page = w("input.buttonstyle[name='next']")
	if next_page:
		urls.add(next_page.attr("onclick").replace("parent.location.href=", "").replace("'", ""))

	bikes = w("table#catprods_tbl td.column_main[align='center']>a.links_main")
	for item in bikes:
		item = pq(item)

		urls.add(domain + item.attr("href"))

	return list(urls)


def extract_data(req):
	data = deepcopy(bike)
	availability = list()
	sizes = list()
	domain = 'http://www.winstanleysbikes.co.uk'
	w = pq(req["html"])

	is_bike = w("table#prod_tbl.sectionborder_main img")
	if is_bike:
		rows = w("table#item_Tbl.column_main tr")
		for row in rows:
			content = w(row)
			if "Name" in content.children('td').eq(0).text():
				data["name"] = content.children('td').eq(1).text()
				data["brand"] = content.children('td').eq(1).text().split(" ")[0]
				year = re.search(r"(\d{4})", content.children('td').eq(1).text())
				if year:
					data["year"] = year.group(1)
			if "Availability" in content.children('td').eq(0).text():
				if "In stock" in content.children('td').eq(1).text():
					availability.append("Available")
				elif "Available to order":
					availability.append("Available to Order")
				else:
					availability.append("Out of Stock")
			if "Size" in content.children('td').eq(0).text():
				size = re.search(r"(\d+)(.*)", content.children('td').eq(1).text())
				if size:
					sizes.append(size.group(1))
					if size.group(2).strip() != "cm":
						data["size_measure"] = "inch"
					else:
						data["size_measure"] = "cm"
			if "Product Code" in content.children('td').eq(0).text():
				data["external_source_id"] = content.children('td').eq(1).text()
			if "Price" in content.children('td').eq(0).text():
				data["currency"] = "GBP"
				price = re.search(r"(\d{3,6}\.\d+).*", content.children('td').eq(1).text())
				if price:
					data["price"] = price.group(1)
					data["discounted_price"] = price.group(1)
		data["provider_store"] = domain
		data["availability"] = dict(zip(sizes, availability))
		image = w(".small_main>img").eq(0).attr("src")
		if image:
			data["image"] = domain + image
		bike_descriptions = w("td.column_main>li")
		bike_text = str()
		tech_specs = str()
		for description in bike_descriptions:
			description = pq(description)
			tech_specs += description.text().strip() + "||"
			if "Frame" in description.text():
				frame = description.text().strip().replace("\t", "").split(":")
				if len(frame) > 1:
					data["frame"] = frame[1]
			if "Wheelset" in description.text():
				wheelset = description.text().strip().replace("\t", "").split(":")
				if len(wheelset) > 1:
					data["wheelset"] = wheelset[1]
			if "Shifters" in description.text():
				gearset = description.text().strip().replace("\t", "").split(":")
				if len(gearset) > 1:
					data["gearset"] = gearset[1]
			bike_text = bike_text + description.text().replace("\t", "") + ". "
		data["description"] = bike_text
		data["tech_specs"] = tech_specs


	#make that > 3
	if len([item for item in data if data[item] != "N/A"]) >= 1:
		return data
	return {}
