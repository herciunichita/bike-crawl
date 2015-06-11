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

	header = ["domain", "external_source_id", "url", "type", "name", "brand", "image","price", "discounted_price", "currency", "availability", "size_measure", "year", "frame", "gearset", "wheelset", "description"]
	csv_out.writerow(header)

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
			#continue
		items.append(data)
		if (data["external_source_id"], data["domain"]) not in id_domain:
			items.append(data)
			id_domain.add((data["external_source_id"], data["domain"]))
		else:
			print >>stderr, "Duplicate", (data["external_source_id"], data["domain"])
			continue	
		
		row = [data[item] for item in header]
		csv_out.writerow(row)

	
