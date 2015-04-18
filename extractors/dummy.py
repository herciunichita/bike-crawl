#!/usr/bin/env python

from pyquery import PyQuery as pq
from bike import bike
from copy import deepcopy
import re

domain = 'dummy.jp'

def extract_urls(req):
        urls = list()

        w = pq(req["html"])

	return urls


def extract_data(req):
        data = deepcopy(bike)
        w = pq(req["html"])


	return data
