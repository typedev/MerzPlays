import importlib
import vanilla
import merz
from fontParts import *
import random
from AppKit import *
from mojo.pens import DecomposePointPen
from fontParts.world import *
import math

import tdGlyphsMatrix
importlib.reload(tdGlyphsMatrix)
from tdGlyphsMatrix import *


def italicShift (angle, Ypos):
	if angle:
		return Ypos * math.tan(abs(angle) * 0.0175)
	else:
		return 0


class MerzDemo:

	def __init__ (self):
		self.w = vanilla.Window((800, 800), minSize = (200, 100))
		self.w.merzView = merz.MerzView(
			(5, 35, -5, -40),
			# centered = False,
			backgroundColor=(.18, .18, .2, 1),
			delegate = self
		)

		# self.w.merzNavi = merz.MerzView(
		# 	(-50, 35, -5, -40),
		# 	# centered = False,
		# 	backgroundColor = (.18, .18, .4, .5),
		# 	delegate = self
		# )

		self.merzW = 10000
		self.merzH = 10000
		# self.w.merzView.setMerzViewSize((self.merzW, self.merzH))
		# self.w.edit = vanilla.EditText((5, 5, -5, 21), callback = self.editCallback)
		self.w.btn2 = vanilla.Button((-350, -35, 200, 21), 'show selected', callback = self.btn2Callback)
		self.w.btn3 = vanilla.CheckBox((-560, -35, 200, 21), 'margins', value = True, callback = self.btn3Callback)
		# self.w.zoom = vanilla.Slider((10, -35, 100, 23), callback = self.sliderCallback)

		self.font = CurrentFont()
		self.scaleFactor = 0.08
		self.heightLine = 1700
		self.pointSizeMargins = 9
		self.showMargins = True

		self.glyphsMatrix = TDGlyphsMatrix(font = self.font, width = self.merzW)

		self.w.open()

	def acceptsMouseMoved (self):
		return True

	def drawMargins (self, container, glyph, italicAngle=0):
		yctrl = 200
		hctrl = 70
		ygap = 20
		color_text = (0.2, 0.2, 0.7, .7)
		offsetX_text = 10
		fontname = '.SFNSMono-Medium'
		# fontsize = self.pointSizeMargins
		pointsize = self.pointSizeMargins
		leftsymbol = chr(int('25C2', 16))
		rightsymbol = chr(int('25B8', 16))

		leftMargin = glyph.leftMargin
		rightMargin = glyph.rightMargin
		if italicAngle != 0:
			leftMargin = glyph.angledLeftMargin
			rightMargin = glyph.angledRightMargin
		if not leftMargin:
			leftMargin = 0
		if not rightMargin:
			rightMargin = 0

		itshift = italicShift(italicAngle, yctrl)

		container.appendTextLineSublayer(
			name = 'margin.left',
			font = fontname,
			position = (-offsetX_text - itshift, yctrl),
			fillColor = color_text,
			pointSize = pointsize,
			text = leftsymbol + str(int(round(leftMargin, 0))),
			visible = self.showMargins,
		)
		container.appendTextLineSublayer(
			name = 'margin.right',
			font = fontname,
			position = (glyph.width + offsetX_text - itshift, yctrl - hctrl - ygap),
			fillColor = color_text,
			pointSize = pointsize,
			text = str(int(round(rightMargin, 0))) + rightsymbol,
			horizontalAlignment = "right",
			visible = self.showMargins,
		)

	def drawGlyph (self, container, glyph, position=(0, 0), italicAngle=0,
	               drawMargins = True, color_glyph = (0, 0, 0, 1), color_box = (0, 0, 0, 0)):
		xpos, ypos = position
		# color_glyph = (0, 0, 0, 1)
		# color_box = (0, 0, 0, 0)
		with container.sublayerGroup():
			baselayer = container.appendRectangleSublayer(
				name = 'glyphbox.' + glyph.name,
				position = (xpos, ypos),
				size = (glyph.width, self.heightLine),
				fillColor = color_box,
				acceptsHit = True
			)
			glyphLayer = baselayer.appendPathSublayer(
				name = 'path.' + glyph.name,
				fillColor = color_glyph,
				position = (0, 500),
				strokeColor = None,
				strokeWidth = 0,
				acceptsHit = True,
			)
			glyphPath = glyph.getRepresentation("merz.CGPath")
			glyphLayer.setPath(glyphPath)
			if drawMargins:
				self.drawMargins(baselayer, glyph, italicAngle)

	def drawGlyphsLine (self, container, glyphs=None, position=(0, 0), numberline = (0,0)):
		italicAngle = self.font.info.italicAngle
		visible = container.getInfoValue('visible')
		if not visible:
			glyphs = container.getInfoValue('glyphs')
			numberline = container.getInfoValue('numberline')
			xpos = 0
			for glyph in glyphs:
				self.drawGlyph(container, glyph, position = (xpos, 0), italicAngle = italicAngle)
				xpos += glyph.width
			container.setInfoValue('visible', True)

			if numberline != (0,0):
				w,h = container.getSize()
				container.appendTextLineSublayer(
					name = 'pos',
					font = '.SFNSMono-Medium',
					position = (w + 100, 500),
					fillColor = (.5, .5, .5, 1),
					pointSize = 9,
					text = '%i:%i' % numberline,
				)

	def clearGlyphsLine(self, container):
		visible = container.getInfoValue('visible')
		if visible:
			container.clearSublayers()
			container.setInfoValue('visible', False)

	def placeGlyphsLine(self, container, glyphs=None, position=(0, 0), numberline = (0,0)):
		with container.sublayerGroup():
			baselayer = container.appendRectangleSublayer(
				name = 'glyphsline',
				position = position,
				size = (self.merzW -500, self.heightLine),
				fillColor = (0, 0, 0, 0),
			)
			baselayer.setInfoValue('glyphs', glyphs)
			baselayer.setInfoValue('visible', False)
			baselayer.setInfoValue('numberline', numberline)
		return baselayer

	def drawGlyphsMatrix(self, container, position=(0, 0)):
		container = self.w.merzView.getMerzContainer()
		w, h = container.getSize()
		tolerance = 20

		# draw the glyphsline only if it is visible within the window
		hits = container.findSublayersIntersectedByRect((0, tolerance, w, h - tolerance), onlyLayers = ['glyphsline'])
		# print('hits visible', len(hits))
		for layer in hits:
			self.drawGlyphsLine(layer)

		# clear bottom layers
		hits = container.findSublayersIntersectedByRect((0, -1000, w, 800))
		# print('hits bottom', len(hits))
		for layer in hits:
			self.clearGlyphsLine(layer)

		# clear top layers
		hits = container.findSublayersIntersectedByRect((0, h + 200, w, 800))
		# print('hits top', len(hits))
		for layer in hits:
			self.clearGlyphsLine(layer)


		
	def magnifyWithEvent(self, sender, event):
		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		container = sender.getMerzContainer()
		point = sender.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
		# print (event.magnification())
		self.scaleFactor += event.magnification()/50
		if self.scaleFactor < 0.04:
			self.scaleFactor = 0.04
		if self.scaleFactor > 0.15:
			self.scaleFactor = 0.15
		self.setContainerScale(self.scaleFactor)
		base = container.getSublayer('base')

		x, y = base.getPosition()
		_x, _y = point
		wM = self.w.merzView.width()
		w2, h2 = base.getSize()
		with base.propertyGroup():
			base.setPosition(( ((wM/self.scaleFactor - w2)/2) , y - _y ))
		self.drawGlyphsMatrix(container = container)
				

	def setContainerScale (self, scale):
		container = self.w.merzView.getMerzContainer()
		container.setSublayerScale(scale)
		print ('scale', scale)

		baselayer = container.getSublayer('base')

		print (baselayer)
		if self.showMargins:
			if scale < 0.11 and self.pointSizeMargins == 9:
				self.pointSizeMargins = 6
				for baselayer1 in baselayer.getSublayers():
					# print (baselayer.getSublayers())
					for glyphslayer in baselayer1.getSublayers():
						# print (glyphslayer.getSublayers())
						l = glyphslayer.getSublayer('margin.left')
						if l:
							l.setPointSize(6)
						r = glyphslayer.getSublayer('margin.right')
						if r:
							r.setPointSize(6)
			elif scale > 0.11 and self.pointSizeMargins == 6:
				self.pointSizeMargins = 9
				for baselayer1 in baselayer.getSublayers():
					# print (baselayer.getSublayers())
					for glyphslayer in baselayer1.getSublayers():
						# print (glyphslayer.getSublayers())
						l = glyphslayer.getSublayer('margin.left')
						if l:
							l.setPointSize(9)
						r = glyphslayer.getSublayer('margin.right')
						if r:
							r.setPointSize(9)

				

	def switchMargins (self, container, showMargins=False):
		self.showMargins = showMargins
		italicAngle = self.font.info.italicAngle
		if self.showMargins:
			# print('ON margins')
			for baselayer in container.getSublayers():
				for glyphlayer in baselayer.getSublayers():
					layername = glyphlayer.getName()
					if 'glyphbox.' in layername:
						l = glyphlayer.getSublayer('margin.left')
						l.setVisible(True)
						r = glyphlayer.getSublayer('margin.right')
						r.setVisible(True)

		else:
			# print('OFF margins')
			for baselayer in container.getSublayers():
				for glyphlayer in baselayer.getSublayers():
					layername = glyphlayer.getName()
					if 'glyphbox.' in layername:
						l = glyphlayer.getSublayer('margin.left')
						l.setVisible(False)
						r = glyphlayer.getSublayer('margin.right')
						r.setVisible(False)


	def mouseDown (self, sender, event):
		X_mouse_pos = int(round(event.locationInWindow().x, 0))
		Y_mouse_pos = int(round(event.locationInWindow().y, 0))
		container = sender.getMerzContainer()
		point = sender.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
		hits = container.findSublayersContainingPoint((point), onlyAcceptsHit = True)
		print (hits)
		# # RANDOM REPOSITION
		# for layer in hits:
		# 	x, y = layer.getPosition()
		# 	with layer.propertyGroup(duration = 1):
		# 		_x = random.randint(-500, 500)
		# 		_y = random.randint(-500, 500)
		# 		layer.setPosition((x + _x, y + _y))
		#
		# w, h = container.getSize()
		# hM = self.w.merzView.height()
		# tolerance = 20
		# hits = container.findSublayersIntersectedByRect((0, tolerance, w, h - tolerance), onlyLayers = ['glyphsline'])
		# for glyphsline in hits:
		# 	for glyphsbox in glyphsline.getSublayers():
		# 		x, y = glyphsbox.getPosition()
		#
		# 		with glyphsbox.propertyGroup(duration = 1, reverse = True, repeatCount='loop'):
		# 			_x = random.randint(-5500, 5500)
		# 			_y = random.randint(-5500, 5500)
		# 			glyphsbox.setPosition((x + _x, y + _y))
		# 			glyphsbox.setFillColor((random.randint(0,10)/10, random.randint(0,10)/10, random.randint(0,10)/10, 1))


		# # FILL RED
		# for layer in hits:
		# 	with layer.propertyGroup( duration=1 ):
		# 		layer.setFillColor((1,0,0,1))

	def scrollWheel (self, sender, event):
		# if sender != self.w.merzView: return
		deltaX = int(round(event.deltaX(), 0))
		deltaY = int(round(event.deltaY(), 0))
		if deltaX == 0 and deltaY == 0: return
		scaleScroll = 40 #abs((math.sin(deltaY/100) * math.tan(deltaY/100)) * 1000)

		deltaX = deltaX * scaleScroll
		deltaY = deltaY * scaleScroll

		container = sender.getMerzContainer()
		hM = self.w.merzView.height()
		wM = self.w.merzView.width()
		heightMatrix = len(self.glyphsMatrix.matrix) * self.heightLine

		layer  = container.getSublayer('base')
		x, y = layer.getPosition()
		w2, h2 = layer.getSize()
		_x = x + deltaX
		_y = y - deltaY

		with layer.propertyGroup(): #duration = .3, animationFinishedCallback=self.myAnimationFinished
			if _y > 0:
				_y = 0
			if _y < hM/self.scaleFactor - heightMatrix:
				_y = hM/self.scaleFactor - heightMatrix
			layer.setPosition(( ((wM/self.scaleFactor - w2)/2) , _y ))

		self.drawGlyphsMatrix(container = container)

	def startDrawGlyphsMatrix(self, merzView, glyphsMatrix):
		container = merzView.getMerzContainer()
		container.clearSublayers()
		xpos = 500
		heightMatrix = len(glyphsMatrix) * self.heightLine
		hM = merzView.height()
		wM = merzView.width()
		# print('MerzSize', wM, hM)

		base = container.appendRectangleSublayer(
			name = 'base',
			size = (self.merzW, heightMatrix),
			fillColor = (1, 1, 1, 1),
			position = (0, 0)
		)

		ypos = len(glyphsMatrix) * self.heightLine
		for idx, line in enumerate(glyphsMatrix):
			ypos -= self.heightLine
			self.placeGlyphsLine(base, line, (xpos, ypos), (idx + 1, len(glyphsMatrix)))

		self.setContainerScale(self.scaleFactor)

		w, h = container.getSize()
		w2, h2 = base.getSize()
		base.setPosition(((wM / self.scaleFactor - w2) / 2, - heightMatrix))

		hits = container.findSublayersIntersectedByRect((0, -h, w, h), onlyLayers = ['glyphsline'])
		for layer in hits:
			self.drawGlyphsLine(layer)

		# w2, h2 = base.getSize()
		with base.propertyGroup(duration = .7):
			base.setPosition((((wM / self.scaleFactor - w2) / 2), hM / self.scaleFactor - heightMatrix))



	def editCallback (self, info):
		pass


	def btn2Callback (self, sender):

		font = CurrentFont()
		glyphsline = []
		glyphsNavi = []
		for nL in font.selection:
			glyphsNavi.append(nL)
			for nR in font.selection:
				glyphsline.append(nL)
				glyphsline.append(nR)
			glyphsline.append('{break}')


		self.glyphsMatrix.setGlyphs(glyphsline, insertVirtual = True)
		self.startDrawGlyphsMatrix(self.w.merzView, self.glyphsMatrix.matrix)


		# navi = self.w.merzNavi.getMerzContainer()
		# hM = self.w.merzNavi.height()
		# wM = self.w.merzNavi.width()
		# navi.setSublayerScale(.012)
		#
		# # xpos, ypos = position
		# color_glyph = (1, 1, 1, 1)
		# color_baselayer = (0, 0, 0, 0)
		# # xpos = 200
		# ypos = hM / .012 #(len(glyphsNavi)) * 1000
		# stepY = ypos / (len(glyphsNavi)) - 100
		# # with navi.sublayerGroup():
		# with navi.sublayerGroup():
		# 	baselayer = navi.appendRectangleSublayer(
		# 		# name = 'glyphbox.' + glyph.name,
		# 		position = (500, 500),
		# 		size = (wM/0.012 - 1000, ypos -500),
		# 		fillColor = (0,0,0,.3),
		# 		cornerRadius = 700
		# 		# acceptsHit = True
		# 	)
		#
		# 	for g in glyphsNavi:
		# 		glyph = self.font[g]
		# 		ypos -= stepY
		# 		xpos = (wM/0.012 -1000 - glyph.width)/2
		# 		self.drawGlyph(baselayer, glyph, position = (xpos, ypos),
		# 		               drawMargins = False, color_glyph = color_glyph, color_box = color_baselayer)

			
		


	def btn3Callback (self, sender):
		self.showMargins = sender.get()
		container = self.w.merzView.getMerzContainer()
		self.switchMargins(container.getSublayer('base'), showMargins = self.showMargins)


MerzDemo()
