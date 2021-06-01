import collections
import random

import vanilla
import merz
from fontParts import *

DIRECTIONS = ['up', 'down', 'left', 'right']
Element = collections.namedtuple("Element", ("name", "size", "count"))
Board = collections.namedtuple("Board", ("w", "h", "map"))
elements = [Element("wall4", 4, 2),
		 Element('wall3', 3, 2),
		 Element('wall2', 2, 3),
		 Element("monster", 1, 4),
		 Element("wall5", 5, 1),
		 Element('gold', 1,4)]

colors = {
	'_':(1,1,1,1),
	'w':(0,0,0,1),
	'm':(1,0,0,1),
	'g':(0,1,0,1),
	'i':(0,0,1,1),
	'o':(1,1,0,1)
}

def create_board(w, h):
	x= Board(w, h, [['_'] * w for _ in range(h)])
	x.map[9][0] = 'i'
	x.map[0][9] = 'o'
	return x
	
def place_elements(board, elements):
	for e in elements:
		for _ in range (e.count):
			place_element(board, e)

def place_element(board, element):
	count = 0 
	while True:
		count +=1
		if count > 1000:
			print('imposible :(')
			return
		_x = random.randint(0, board.w - 1)
		_y = random.randint(0, board.h - 1)
		random.shuffle(DIRECTIONS)
		for direction in DIRECTIONS:
			if maybe_place(board, _x, _y, direction, element):
				return

def maybe_place(board, x, y, direction, element):
	if direction == "right":
		right = min(board.w , x + element.size +1)
		left = right - element.size
		slots = [(x, i) for i in range(left, right)]
	elif direction == "left":
		left = max(0-1, x - element.size -1)
		right = left + element.size
		slots = [(x, i) for i in range(left, right)]
	elif direction == "down":
		bottom = min(board.h , y + element.size +1)
		top = bottom - element.size
		slots = [(i, y) for i in range(top, bottom)]
	elif direction == "up":
		top = max(0-1, y - element.size -1)
		bottom = top + element.size
		slots = [(i, y) for i in range(top, bottom)]

	if all([board.map[x][y] == '_' for x, y in slots]):
		# for x1 in range(x-1,x+1):
		#	 if x1 < board.w-1 and x1 > 0:
		#		 for y1 in range(y-1, y+1):
		#			 if y1 < board.h-1 and y1 > 0:
		#				 if board.map[x1][y1] == '_':
		for x, y in slots:
			board.map[x][y] = element.name[0]
		return True
	return False

if __name__ == "__main__":
	
	class MerzDemo:
		def __init__(self):
			self.w = vanilla.Window((300, 400))#,minSize = (210, 270))
			self.w.merzView = merz.MerzView(
				(50,30,200,200),
				backgroundColor=(1, 1, 1, 1),
				delegate = self
				)
			self.w.btn = vanilla.Button((50,-55,200,21), 'rebuild' , callback=self.btnCallback)
			self.w.zoom = vanilla.Slider((10, -85, -10, 23), callback = self.sliderCallback, value = 100)
			self.scalefactor = 1
			self.w.open()
			self.drawMap()
			
		def drawMap(self):
			c = self.w.merzView.getMerzContainer()
			c.clearSublayers()
			board = create_board(10, 10)
			place_elements(board, elements)

			sizeElement = 20
			x = 0
			y = sizeElement * 10 - sizeElement
			for row in board.map:
				for l in row:
					r, g, b, a = colors[l]
					c.appendRectangleSublayer(
						name = l,
					   position=(x, y),
					   size=(sizeElement, sizeElement),
					   fillColor=(r, g, b, a),
					   strokeColor=(0.4,0.4,0.4,.7),
					   strokeWidth = 1
					)
					
					x += sizeElement
				y -= sizeElement
				x = 0
			c.setSublayerScale(self.scalefactor)

		def btnCallback(self, sender):
			self.drawMap()

		def acceptsFirstResponder (self, info):
			return True
			
		def mouseDown(self, sender, event):
			X_mouse_pos = int(round( event.locationInWindow().x, 0))
			Y_mouse_pos = int(round( event.locationInWindow().y, 0))
			print ( 'mouse:', X_mouse_pos, Y_mouse_pos )

			container = self.w.merzView.getMerzContainer()
			point = self.w.merzView.convertWindowCoordinateToViewCoordinate((X_mouse_pos, Y_mouse_pos))
			hits = container.findSublayersContainingPoint((point))
			print (hits)


		def sliderCallback(self, info):
			self.scalefactor = info.get()/100
			c = self.w.merzView.getMerzContainer()
			c.setSublayerScale(self.scalefactor)

	
	MerzDemo()