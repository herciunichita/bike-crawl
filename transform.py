#!/usr/bin/env python


from unicodecsv import reader
from sys import stdin
from xlsxwriter.workbook import Workbook

def parse_args():
        from argparse import ArgumentParser
        argp = ArgumentParser(__doc__)
        argp.add_argument("--output", default="output")
      
       
        
        return vars(argp.parse_args())



if __name__ == '__main__':

	args = parse_args()
	workbook = Workbook(args["output"] + ".xlsx")
	worksheet = workbook.add_worksheet()


	for r, row in enumerate(reader(stdin)):
		for c, col in enumerate(row):
			worksheet.write(r, c, col)

	workbook.close()
