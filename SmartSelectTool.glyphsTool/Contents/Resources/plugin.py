# encoding: utf-8

###########################################################################################################
#
#
#	Smart Select Tool Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/SelectTool
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from AppKit import NSShiftKeyMask, NSCursor	#NSCommandKeyMask, NSAlternateKeyMask, NSControlKeyMask, 
from GlyphsApp import *
from GlyphsApp.plugins import *

class SmartSelectTool(SelectTool):

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': u'Smart Select Tool', 'zh-Hant': u'智慧選取工具', 'zh-Hant-TW': u'智慧選取工具', 'zh': u'智慧選取工具', 'ja': u'スマートセレクトツール'})
		# self.generalContextMenus = [
		# 	{'name': Glyphs.localize({'en': u'Switch to Select Tool', 'zh-Hant': u'切換至選取工具', 'zh-Hant-TW': u'切換至選取工具', 'zh': u'切換至選取工具', 'ja': u'セレストツールに切り替え'}), 'action': self.gotoSelect_},
		# ]
		self.toolbarPosition = 10

	def trigger(self):
		return "x"

	def standardCursor(self):
		return NSCursor.pointingHandCursor()

	@objc.python_method
	def start(self):
		pass
	
	@objc.python_method
	def activate(self):
		self.clickedElement = None
		self.origin = None
		#print(dir(self))
		pass
	
	# @objc.python_method
	# def background(self, layer):
	# 	# Draw a red rectangle behind the glyph as big as the glyph’s bounding box
	# 	# NSColor.redColor().set()
	# 	# NSBezierPath.fillRect_(layer.bounds)
	# 	pass

	@objc.python_method
	def deactivate(self):
		pass

	@objc.python_method
	def conditionalContextMenus(self):
		Glyphs.font.tool = 'SelectTool'

	# def gotoSelect_(self, sender):
	# 	Glyphs.font.tool = 'SelectTool'

	def mouseDown_(self, event):
		objc.super(SmartSelectTool, self).mouseDown_(event)
		#print('vent.pressedMouseButtons()')
	
		loc = self.editViewController().graphicView().getActiveLocation_(event)
		layer = self.editViewController().graphicView().activeLayer()
		if not layer: return
		#shift = 'shift' if event.modifierFlags() & NSShiftKeyMask else ''
		#print('mouse down: ', loc, shift)
		self.clickedElement = self.elementAtPoint_atLayer_(loc, layer)
		self.origin = None

		if not self.clickedElement:
			self.origin = loc

	def mouseDragged_(self, event):
		objc.super(SmartSelectTool, self).mouseDragged_(event)
		#pass
		# if self.clickedElement:	return	# if anything clicked, run normal behavior to edit

		# loc = self.editViewController().graphicView().getActiveLocation_(event)
		# layer = self.editViewController().graphicView().activeLayer()

		
	def mouseUp_(self, event):
		if self.clickedElement:
			objc.super(SmartSelectTool, self).mouseUp_(event)
			return	#if anything clicked, run normal behavior to edit

		#objc.super(SmartSelectTool, self).mouseUp_(event)
		if not self.origin: return

		loc = self.editViewController().graphicView().getActiveLocation_(event)
		layer = self.editViewController().graphicView().activeLayer()
		shift = event.modifierFlags() & NSShiftKeyMask
		if not layer: return

		x1 = min(loc.x, self.origin.x)
		x2 = max(loc.x, self.origin.x)
		y1 = min(loc.y, self.origin.y)
		y2 = max(loc.y, self.origin.y)

		selectedPaths = [path for path in layer.paths if path.selected]
		objc.super(SmartSelectTool, self).mouseUp_(event)	# run default behavior to redraw screen

		paths = []
		for path in layer.paths:
			#path.selected = False
			#selected = shift and len([n for n in path.nodes if not n.selected]) == 0
			selected = shift and path in selectedPaths
			for node in path.nodes:
				if node.position.x >= x1 and node.position.x <= x2 and node.position.y >= y1 and node.position.y <= y2:
					path.selected = not selected
					continue

		#print('mouse up: ', loc)
		# clickedElement = self.elementAtPoint_atLayer_(loc, layer)
		# if clickedElement is not None:
		# 	layer.selection.append(clickedElement)
		# 	print('click event: ', clickedElement)

	def mouseDoubleDown_(self, event):
		#objc.super(SmartSelectTool, self).mouseDoubleDown_(event)
		"""
		Do more stuff that you need on mouseDown_(). Like custom selection 
		"""
		loc = self.editViewController().graphicView().getActiveLocation_(event)
		layer = self.editViewController().graphicView().activeLayer()
		shift = event.modifierFlags() & NSShiftKeyMask
		#print('double down: ', loc, flag)
		self.clickedElement = self.elementAtPoint_atLayer_(loc, layer)
		if not layer or self.clickedElement:
			objc.super(SmartSelectTool, self).mouseDoubleDown_(event)
		else:
			cnt = 0
			pathList = []
			revList = []
			for path in layer.paths:
				if path.bezierPath.containsPoint_(loc):
					if path.direction < 0: pathList.append(path)
					if path.direction > 0: revList.append(path)

			if len(pathList) > 0 and len(pathList) - len(revList) > 0:
				pathSet = set(pathList)
				if len(revList) >= 1:
					for path in pathList:
						removed = False
						for rpath in revList:
							if not removed and path.bezierPath.containsPoint_(rpath.nodes[0].position): 
								pathSet.remove(path)
								removed = True
					pathList = list(pathSet)

				if len(pathList) > 0:
					for path in layer.paths:
						if path.direction > 0 and pathList[0].bezierPath.containsPoint_(path.nodes[0].position): 
							pathList.append(path)

					pathSet = set(pathList)
					for path1 in pathList:
						for path2 in pathList:
							if path1 == path2 or path1.direction < 0 or path2.direction < 0: continue
							if path1.bezierPath.containsPoint_(path2.nodes[0].position):
								if path2 in pathSet: pathSet.remove(path2)
					pathList = list(pathSet)
				
				if len(pathList) > 0:
					selected = shift and len([p for p in pathList if not p.selected]) == 0
					for path in pathList: path.selected = not selected

			elif loc.x < 0 or loc.x > layer.width or loc.y < layer.master.descender or loc.y > layer.master.ascender:		# run default behavior to switch glyph
				objc.super(SmartSelectTool, self).mouseDoubleDown_(event)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
