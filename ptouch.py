#!/usr/bin/env python3
import serial
from my_font import my_font
class PTouch:
	def __init__(self, serPort):
		self.ser = serial.Serial(port=serPort, baudrate=9600)

	def initPrinter(self):
		self.ser.write(b"\x1b@")  # ESC @

	def print(self, eject=True):
		if eject:
			self.ser.write(b"\x03")
		else:
			self.ser.write(b"\x0C") # Form Feed

	def setAbsPosition(self, pos):
		self.writeBytes(0x1b, 0x24, pos%256, pos>>8)

	def sendImage(self, bitmap):
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
		self.ser.write(bmp3)

	def setMode(self, feedAmount=26, autocut=True, mirrorPrint=False):
		mode = feedAmount | (1<<6 if autocut else 0) | (1<<7 if mirrorPrint else 0)
		self.writeBytes(0x1b, 0x69, 0x4d, mode)

	def writeBytes(self, *b):
		print(bytearray(b))
		print(" ".join("%02X"%x for x in b))
		self.ser.write(bytearray(b))

	def sendText(self, text):
		img = bytearray(len(text)*8*24)
		for i,char in enumerate(text):  # iterate through all chars of the text
			for j in range(8): # each char has 8 cols
				for k in range(8):  # each char is 8 rows high
					# each char uses 8*8*3 = 192 pixels
					# each col has 8*3 = 24 pixels
					# each row of the char is stretched to two rows
					bit = 0xff if my_font[ord(char)][7-k] & (1<<j) else 0x00
					img[i*8*8*3+j*24+k*3+0] = bit
					img[i*8*8*3+j*24+k*3+1] = bit
					img[i*8*8*3+j*24+k*3+2] = bit
		for x in range(len(img)):
			if x%24==0: print("")
			if img[x]==0:
				print("  ",end="")
			else:
				print("%02x"%(img[x]), end="")
		self.sendImage(img)
		

	def statusRequest(self):
		self.writeBytes(0x1b, 0x69, 0x53)
		
		status = self.ser.read(32)
		header = status[0:8]
		err1 = status[8] # no tape, tape end, cutter jam
		err2 = status[9] # type change err, print buf full, transm err, recp buf full
		tapewidth = status[10]
		tapetype = status[11]
		reserved = status[12:15]
		mode = status[15]
		print_density = status[16]
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

		print("Tape Width:    %d" % (tapewidth))
		print("Tape Type:     %d" % (tapetype))
		print("Mode:          %d" % (mode))
		print("Print Density: %d" % (print_density))




