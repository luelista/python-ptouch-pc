#!/usr/bin/env python3
from ptouch import PTouch
import config
import sys
import random, string, math
class InventoryLabelPrinter:
	def __init__(self, config):
		self.pt = PTouch(config.serialPort)
		self.urlPrefix = config.inventoryUrlPrefix
		self.pt.setMode(1, False, False)

	def newID(self):
		N=8
		rid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
		return rid

	def inventoryLabel(self, rid, n1, n2='', n3=''):
		url  = self.urlPrefix + rid
		urlstretch = (1,2)
		itemstretch = (2,5); n1top = 0
		item2stretch = (1,4); n2top = 40
		if n3 != '':
			item2stretch=(1,2); n2top =43 
		item3stretch = (1,2)
		if n2 == '':
			itemstretch=(2,6)
			n1top = 10
		self.pt.makeBuffer(max( self.pt.textWidth(urlstretch, url), 90+self.pt.textWidth(item2stretch, n2), 90+self.pt.textWidth(itemstretch, n1), 90+self.pt.textWidth(item3stretch, n3) ))
		self.pt.dataMatrixToBuffer(0,0, 4, url)
		self.pt.textToBuffer(90, n1top, itemstretch, n1)
		self.pt.textToBuffer(90, n2top, item2stretch, n2)
		self.pt.textToBuffer(90, 70, item3stretch, n3)
		self.pt.textToBuffer(0, 103, urlstretch, url)

		
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



