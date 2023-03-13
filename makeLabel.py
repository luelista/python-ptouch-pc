#!/usr/bin/env python3
from ptouch import PTouch
import config
import sys
import random, string, math
from subprocess import check_call
class SimpleLabelPrinter:
	def __init__(self, config):
		self.pt = PTouch(config.serialPort)

	def simpleLabel(self, lines):
		self.pt.setMode(0, False, False)
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
		return self.pt.showBufferTk()
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
with open("preview.pbm","w") as f:
	invpr.pt.writeBufferPBM(f)
	check_call(["open", "preview.pbm"])
if not invpr.preview():
	sys.exit(1)
print("Press ENTER to print")
input()

invpr.print()



