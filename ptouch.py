#!/usr/bin/env python3
# vim: noexpandtab 
#from hubarcode.code128 import Code128Encoder
from hubarcode.datamatrix import DataMatrixEncoder
from hubarcode.datamatrix.renderer import DataMatrixRenderer
import serial, socket
from my_font import my_font
import math
import random, string
import time

from config import *

class PTouch:
	BARCODE_CONTROL = ["no change", "no barcode", "barcode only", "including barcode"]

	def __init__(self, serPort):
		if isinstance(serPort, tuple):
			self.ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ser.connect(serPort)
			self.isSerial = False
		elif isinstance(serPort, str):
			self.ser = serial.Serial(port=serPort, baudrate=9600)
			self.isSerial = True
		else:
			raise "Param must be tupel for TCP or string for serial port"
		self.statusRequest()

	# Printer communication routines

	def initPrinter(self):
		self.writeBytes(0x1b, 64)  # ESC @

	def setMode(self, feedAmount=26, autocut=True, mirrorPrint=False):
		mode = feedAmount | (1<<6 if autocut else 0) | (1<<7 if mirrorPrint else 0)
		self.writeBytes(0x1b, 0x69, 0x4d, mode)

	def writeBytes(self, *b):
		print(bytearray(b))
		print(" ".join("%02X"%x for x in b))
		if self.isSerial:
			self.ser.write(bytearray(b))
		else:
			self.ser.send(bytearray(b))

	def print(self, eject=True):
		if eject:
			self.writeBytes(0x03)
		else:
			self.writeBytes(0x0C) # Form Feed

	def setAbsPosition(self, pos):
		self.writeBytes(0x1b, 0x24, pos%256, pos>>8)

	# bitmap is an array of pixels, where each pixel is an int of 1 or 0
	# each row is scanned left to right, then the rows top to bottom
	def sendFullImage(self, bitmap):
		rowheight = 24
		rows = int(math.ceil(self.dotswidth / rowheight))
		rows = int(math.floor(self.dotswidth / rowheight))
		# sollte eigentlich mit math.ceil funktionieren - allerdings meldet der Drucker dann den Fehler PRINT BUFFER FULL

		size = int(len(bitmap)/self.dotswidth)
		for row in range(rows):
			bmp = bytearray(rowheight * size)
			for line in range(rowheight):
				lineidx = (row*rowheight+line)*size
				if lineidx >= len(bitmap): continue
				for col in range(size):
					bmp[col *rowheight + line] = bitmap[lineidx + col]
			self.send24RowImage(bmp)
			time.sleep(0.8)
			self.writeBytes(0x0d, 0x0a)
			time.sleep(0.8)


	# bitmap is an array of pixels, where each pixel is an int of 1 or 0
	# each col is scanned top to bottom, then the cols left to right
	def send24RowImage(self, bitmap):
		size = len(bitmap)/24
		print(size)
		size=int(size)
		self.writeBytes(0x1b, 0x2a, 0x27, size%256, size>>8)
		bmp3 = bytearray(int(len(bitmap)/8))
		print(len(bmp3))
		for i in range(len(bmp3)):
			if (i%3)==0: print("")
			byte = 0
			for b in range(8):
				byte = byte | ((bitmap[i*8+7-b] & 0x01) << b)
			bmp3[i] = byte
			print(format(bmp3[i], '08b'), end="")
		if self.isSerial:
			self.ser.write(bmp3)
		else:
			self.ser.send(bmp3)

	def sendText(self, text):
		img = bytearray(len(text)*8*24)
		for i,char in enumerate(text):  # iterate through all chars of the text
			for j in range(8): # each char has 8 cols
				for k in range(8):  # each char is 8 rows high
					# each char uses 8*8*3 = 192 pixels
					# each col has 8*3 = 24 pixels
					# each row of the char is stretched to two rows
					bit = 0xff if my_font[ord(char)][k] & (1<<j) else 0x00
					img[i*8*8*3+j*24+k*3+0] = bit
					img[i*8*8*3+j*24+k*3+1] = bit
					img[i*8*8*3+j*24+k*3+2] = bit
		for x in range(len(img)):
			if x%24==0: print("")
			if img[x]==0:
				print("  ",end="")
			else:
				print("%02x"%(img[x]), end="")
		self.send24RowImage(img)
	


	# Printer status request

	def statusRequest(self):
		self.writeBytes(0x1b, 0x69, 0x53)
		
		if self.isSerial:
			status = self.ser.read(32)
		else:
			status = self.ser.recv(32)
		header = status[0:8]
		err1 = status[8] # no tape, tape end, cutter jam
		err2 = status[9] # type change err, print buf full, transm err, recp buf full
		self.tapewidth = status[10]
		tapetype = status[11]
		reserved = status[12:15]
		mode = status[15]
		print_density_bytes = status[16]
		print_density = print_density_bytes & 0b1111
		barcode_control = (print_density_bytes & 0b110000) >> 4
		reserved2 = status[17:32]
		
		print("Header:         ",end="")
		for x in header: print("%02X "%(x), end="")
		print("")
		print("Error 1:        ",end="")
		print("%02X "%(err1),end="")
		if err1 & 0x01: print("NO_TAPE ",end="")
		if err1 & 0x02: print("TAPE_END ",end="")
		if err1 & 0x04: print("CUTTER_JAM ",end="")
		print("")

		print("Error 2:        ",end="")
		print("%02X "%(err2),end="")
		if err2 & 0x01: print("TAPE_CHANGE_ERROR ",end="")
		if err2 & 0x02: print("PRINT_BUFFER_FULL ",end="")
		if err2 & 0x04: print("TRANSMISSION_ERROR ",end="")
		if err2 & 0x08: print("RECEPTION_BUFFER_FULL ",end="")
		print("")

		print("Tape Width:     %d" % (self.tapewidth))
		print("Tape Type:      %d" % (tapetype))
		print("Mode:           %d" % (mode))
		print("Print Density:  %d" % (print_density))
		print("Barcode Ctrl:   %d (%s)" % (barcode_control, PTouch.BARCODE_CONTROL[barcode_control]))
		
		# Available dots, copied from manual
		if self.tapewidth == 24:
			self.dotswidth = 128
		elif self.tapewidth == 18:
			self.dotswidth = 85
		elif self.tapewidth == 12:
			self.dotswidth = 57
		elif self.tapewidth == 9:
			self.dotswidth = 49
		elif self.tapewidth == 6:
			self.dotswidth = 28


	# Buffer operations
	
	def getFullImageWidth(self):
		return self.dotswidth

	def makeBuffer(self, cols):
		self.buffer = bytearray(cols*self.dotswidth)
		self.buffersize = cols

	def printBuffer(self):
		self.sendFullImage(self.buffer)
		#self.print(False)

	def setPixel(self, line, col, onoff):
		self.buffer[line*self.buffersize + col] = onoff
	def textToBuffer(self,x, y, stretch, text):
		(stretchX, stretchY) = stretch
		for i,char in enumerate(text):  # iterate through all chars of the text
			for j in range(8): # each char has 8 cols
				for k in range(8):  # each char is 8 rows high
					# each char uses 8*8*3 = 192 pixels
					# each col has 8*3 = 24 pixels
					# each row of the char is stretched to two rows
					bit = 0xff if my_font[ord(char)][k] & (1<<j) else 0x00
					col = x + (i*8+j)*stretchX
					line = y + k*stretchY
					for sx in range(stretchX):
						for sy in range(stretchY):
							if line+sy < self.dotswidth:
								self.buffer[ (line+sy) * self.buffersize + col+sx  ] = bit

	def code128ToBuffer(self, x, y, stretch, text):
		(barwidth, height)=stretch
		dm = Code128Encoder(text)
		for c in range(len(dmtx.bars)):
			col = x + c*barwidth
			bit = dm.bars[c]
			for sx in range(barwidth):
				for sy in range(height):
					self.buffer[ (y+sy) * self.buffersize + col+sx  ] = bit
				
	def dataMatrixToBuffer(self, x, y, stretch, text):
		dm = DataMatrixEncoder(text)
		dmtx = DataMatrixRenderer(dm.matrix)
		for r in range(len(dmtx.matrix)):
			line = y + r*stretch
			for c in range(len(dmtx.matrix)):
				col = x + c*stretch
				bit = dmtx.matrix[r][c]
				for sx in range(stretch):
					for sy in range(stretch):
						self.buffer[ (line+sy) * self.buffersize + col+sx  ] = bit
						print(bit,end="")
			print("")
				
	
	def textWidth(self, stretch, text):
		(stretchX, stretchY) = stretch
		return len(text) * stretchX * 8
	
	def showBuffer(self):
		for row in range(self.dotswidth):
			for col in range(self.buffersize):
				print('.' if self.buffer[row*self.buffersize + col] == 0 else '#', end='')
			print("|")



