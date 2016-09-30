#!/usr/bin/env python3
from ptouch import PTouch
import config
import sys
import random, string, math
class InventoryLabelPrinter:
	def __init__(self, config):
		self.pt = PTouch(config.serialPort)
		self.urlPrefix = config.inventoryUrlPrefix

	def newID(self):
		N=8
		rid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
		return rid

	def inventoryLabel(self, rid, n1, n2='', n3=''):
		url  = self.urlPrefix + rid
		urlstretch = (1,1)
		itemstretch = (2,3); n1top = 0
		item2stretch = (1,2); n2top = 26
		if n3 != '':
			item2stretch=(1,1); n2top = 25
		item3stretch = (1,1)
		if n2 == '':
			itemstretch=(2,4)
			n1top = 5
		self.pt.makeBuffer(max( self.pt.textWidth(urlstretch, url), 45+self.pt.textWidth(item2stretch, n2), 45+self.pt.textWidth(itemstretch, n1), 45+self.pt.textWidth(item3stretch, n3) ))
		self.pt.dataMatrixToBuffer(0,0, 2, url)
		self.pt.textToBuffer(45, n1top, itemstretch, n1)
		self.pt.textToBuffer(45, n2top, item2stretch, n2)
		self.pt.textToBuffer(45, 33, item3stretch, n3)
		self.pt.textToBuffer(0, 41, urlstretch, url)

		
	def inventoryLabel2(self, rid, n1, n2='', n3=''):
		url  = self.urlPrefix + rid
		urlstretch = (1,1)
		itemstretch = (2,3); n1top = 0
		self.pt.makeBuffer(max( self.pt.textWidth(item2stretch, n2), 30 ))
		self.pt.code128ToBuffer(0, 27, (1,18), rid)
		self.pt.textToBuffer(0, n1top, itemstretch, n1)
		self.pt.textToBuffer(0, 41, urlstretch, url)

	def preview(self):
		self.pt.showBuffer()
	def print(self):
		self.pt.printBuffer()
		self.pt.print(False)

invpr = InventoryLabelPrinter(config)
n1 = sys.argv[1]
n2 = ""
n3 = ""
rid = invpr.newID()

if len(sys.argv)>2: n2=sys.argv[2]
if len(sys.argv)>3: n3=sys.argv[3]
if len(sys.argv)>4: rid=sys.argv[4]

invpr.inventoryLabel(rid,n1,n2,n3)
invpr.preview()
print("Press ENTER to print")
input()
invpr.print()



