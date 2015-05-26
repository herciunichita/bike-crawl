#!/usr/bin/env python

from unicodecsv import reader, writer
from sys import stdin, stdout, stderr
from json import loads, dumps


if __name__ == '__main__':


	header = set()
	id_domain = set()
	urls = set()

	items = list()

	csv_out = writer(stdout)

	for line in stdin:
		try:
	
			line = loads(line)
		except ValueError:
			print >>stderr, "ERROR:\n" + line
			continue
		line["data"]["domain"] = line["domain"]
		line["data"]["url"] = line["url"]
		line["data"]["type"] = line["type"]
		data = line["data"]

		if data["url"] not in urls:
			urls.add(data["url"])
		else:
			print >>stderr, data["url"]
			continue
		items.append(data)
		if (data["external_source_id"], data["domain"]) not in id_domain:
			items.append(data)
			id_domain.add((data["external_source_id"], data["domain"]))
		else:
			print >>stderr, "Duplicate", (data["external_source_id"], data["domain"])
			#continue
		"""
		if data["frame_material"] != "N/A" and data["frame"] == "N/A":
			aux = data["frame_material"]
			data["frame"] = aux
			data["frame_material"] = "N/A"
		"""
		#del data["provider_id"]
		#del data["size_value"]
		data["gears"] = "N/A" if not data.get("gears") else data["gears"]
		for item in data:
			if data[item] != "N/A":
				header.add(item)
		#items.append(data)
	header = list(header)
	csv_out.writerow(header)
	for item in items:
		row = [item.get(key) for key in header]
		csv_out.writerow(row)

	
