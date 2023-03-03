#!/usr/bin/env python3
from ptouch import PTouch
import config
import sys
import random, string, math
class SimpleLabelPrinter:
	def __init__(self, config):
		self.pt = PTouch(config.serialPort)

	def simpleLabel(self, lines):
		width = 0	
		print(lines)
		for (stretch, txt) in lines:
			width = max(width, self.pt.textWidth(stretch, txt))
		print(width)
		self.pt.makeBuffer(width)
		top = 0
		for (stretch, txt) in lines:
			self.pt.textToBuffer(0, top, stretch, txt)
			top = top + stretch[1]*8 + 1
	def preview(self):
		self.pt.showBuffer()
	def print(self):
		self.pt.printBuffer()
		self.pt.print(False)

invpr = SimpleLabelPrinter(config)

args = sys.argv[1:]
lines = []
for arg in args:
	stretch = (int(arg[0]), int(arg[1]))
	text = arg[2:]
	lines.append((stretch, text))


	
invpr.simpleLabel(lines)
invpr.preview()
print("Press ENTER to print")
input()
invpr.print()



