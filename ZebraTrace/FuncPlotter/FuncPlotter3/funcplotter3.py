#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================
#
# Module for image tracing using functions graphs
# Python >= 2.6, PyQt4
#
# The contents of this file are dedicated to the public domain.
#
# =============================================================

import sys, os
from math import *
from PyQt4.QtGui import QImage, QColor, qGray, QMessageBox
# from ..utils import xrange

sys.setcheckinterval(0xfff)
xrange = range

class Tracer:
	def __init__(self, image_file=None, default_wh=[1024.0, 1024.0], progress_handler = None):
		self.clear()
		self.image = None

		if progress_handler:
			self.ph = progress_handler
		else:
			self.ph = lambda i: None
			self.ph._message = ''
			self.ph._maxval = 0

		if image_file and os.path.exists(image_file):
			# image tracing shall consist of 256 index colors ranked by luma
			img = QImage(image_file)

			if not img.isGrayscale() and QMessageBox("Image is not in grayscale",
													 "Convert RGB image to grayscale?",
													 QMessageBox.Question,
													 QMessageBox.Yes, QMessageBox.No, 0).exec_() == QMessageBox.Yes:
				self.ph._message = 'Converting image to grayscale'
				self.ph._maxval = img.height()
				for y in range(img.height()):
					for x in range(img.width()):
						lightness = qGray(img.pixel(x, y))
						img.setPixel(x, y, (lightness<<16) + (lightness<<8) + lightness)
					self.ph(y)

			colortable = [QColor(i, i, i).rgb() for i in xrange(256)]
			self.image = img.convertToFormat(QImage.Format_Indexed8, colortable)
			w, h = float(self.image.width()), float(self.image.height())
			self.dpi = img.dotsPerMeterX() / 1000.0 * 25.4
		else:
			w, h = default_wh
			self.dpi = 96.0

		self.wh = [w, h]

		self.x1, self.y1, self.x2, self.y2 = [i/max(w, h) for i in [-w, -h, w, h]]
		self.dx = self.x2 - self.x1
		self.dy = self.y2 - self.y1
		# Resolution field in SVG units per pixel
		self.scale = self.dx / w


	def clear(self):
		self.svg = []
		self.nodes_count = 0
		self.objects_count = 0
		self.total_length = 0 # in inches; adjust self.dpi to get desirable value


	def _trace(self, coords, width_range):
		if len(coords) < 2:
			return []

		# OPTIMIZATION
		canvas_x1 = self.x1
		canvas_y1 = self.y1
		canvas_dx = self.dx
		canvas_dy = self.dy
		img_w = self.image.width()
		img_h = self.image.height()
		img_colors = float(self.image.colorCount() - 1)
		img_pixelIndex = self.image.pixelIndex
		scale = self.scale

		delta = (width_range[1] - width_range[0]) / 2.0
		min_width = width_range[0] / 2.0

		paths = []
		right, left = [], []

		d1, d2, d3 = 0, 0, 0 # consecutive points thicknesses, d3 is the current

		p0, p1, pn, ps = coords[0], coords[1], coords[-1], coords[-2]
		# if directions of start of curve and of its end are not equal
		if (p1[0] - p0[0]) * (p1[0] - pn[0]) < 0 or \
			(p1[1] - p0[1]) * (p1[1] - pn[1]) < 0:
			# extrapolation
			pre_x, pre_y = 2 * p0[0] - p1[0], 2 * p0[1] - p1[1]
			coords += [[2 * pn[0] - ps[0], 2 * pn[1] - ps[1]]]
		else:
			# last but 1 point
			pre_x, pre_y = ps
			coords += [p1]

		for i, [x, y] in enumerate(coords[:-1]):
			pixel_x = int((x - canvas_x1) / canvas_dx * img_w - 0.33) # 0.33 - px shift
			pixel_y = int((y - canvas_y1) / canvas_dy * img_h - 0.33)

			if 0 <= pixel_x < img_w and 0 <= pixel_y < img_h:
				k = 1 - img_pixelIndex(pixel_x, pixel_y) / img_colors
				out_of_image = False
			else:
				k = 0
				out_of_image = True

			d3 = ([min_width, 0][out_of_image] + k * delta) * scale # line thickness

			# append
			if d3:
				x1, y1 = coords[i+1][0], coords[i+1][1]
				if pre_x < x1:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2
				elif pre_x > x1:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2 + pi
				else:
					if pre_y < y1:
						alpha = pi
					else:
						alpha = 0
				dx = d3 * cos(alpha)
				dy = d3 * sin(alpha)
			else:
				dx, dy = 0, 0

			right.append([x + dx, y + dy])
			left.append([x - dx, y - dy])

			pre_x, pre_y = x, y

			# remove 0 thickness points
			if not d3 and not d2:
				if not d1:
					# remove previous (at d2) if exists
					if len(right) > 1:
						right.pop(-2)
						left.pop(-2)
				else:
					# append/close at d2 if possible
					if len(right) > 1:
						left.reverse()
						paths.append(right[:-1] + left[1:] + [right[0]])
						right = right[-1:]
						left = left[:1]

			d1, d2 = d2, d3 # shift for next iter

		#append last unclosed path
		if len(right) > 1:
			left.reverse()
			paths.append(right + left + [right[0]])

		# return paths' coords
		return paths


	def _get_coords(self, fX, fY, T, res=1, polar=False):
		res = res / self.scale
		if polar and fY:
			fR, fT = fX, fY
			fX = lambda a: fR(a) * cos(fT(a))
			fY = lambda a: fR(a) * sin(fT(a))
		elif not fY:                            # If only the function x
			fR = fX                             # then consider the polar coordinates
			fX = lambda a: fR(a) * cos(a)
			fY = lambda a: fR(a) * sin(a)
		dT = float(T[1] - T[0])
		resolution = int(dT * res)
		if resolution > 2:
			tl = [T[0] + dT / resolution * i for i in xrange(resolution + 1)]
			return list(map(fX, tl)), list(map(fY, tl))
		else:
			return None, None


	def auto_resolution(self, fX, fY, T, polar=False):
		coords = list(zip(*self._get_coords(fX, fY, T, 0.25, polar)))
		l = 0
		for i, [x, y] in enumerate(coords[:-1]):
			l += hypot(x - coords[i+1][0], y - coords[i+1][1])
		# returns length of a path divided by var range (= resolution)
		return l / (T[1] - T[0])


	def append_func(self, fX, fY, T, res=1, polar=False, width_range=[0,2.0], tolerance=0.0):
		coordX, coordY = self._get_coords(fX, fY, T, res, polar)

		if coordX:
			coords = list(zip(coordX, coordY))

			# if there is an image and reason, tracing
			if self.image and width_range[0] != width_range[1]:
				paths = self._trace(coords, width_range)

				if tolerance > 0.0:
					# Douglas-Peucker line simplification
					from .dp import simplify_points
					simplified_paths = []
					for path in paths:
						simplified_paths.append(simplify_points(path, tolerance * self.scale))
					paths = simplified_paths

				for path in paths:
					self._generate_path(path, close_path = True)

			else:	# no image or width have no range
				if tolerance > 0.0:
					from .dp import simplify_points
					coords = simplify_points(coords, tolerance * self.scale)

				self._generate_path(coords, 'none', 'black', width_range[1], False)


	def _generate_path(self, coords=[], fill_color='black', stroke_color='none', stroke_width=0, close_path=True):
		if not coords:
			return

		params = (fill_color, stroke_color, stroke_width * self.scale, coords[0][0], coords[0][1])
		svg_path = '<path fill="%s" stroke="%s" stroke-width="%s" d="M%f,%f ' % params

		length = 0
		for i, [x, y] in enumerate(coords[1:]):
			svg_path += 'L%f,%f ' % (x, y)
			length += hypot(x - coords[i][0], y - coords[i][1])

		svg_path += ['"/>', 'Z"/>'][close_path]

		self.svg.append(svg_path)
		# statistics
		self.nodes_count += len(coords) - 1
		self.objects_count += 1
		self.total_length += length / self.scale / self.dpi


	def save_svg(self, file_name='trace.svg'):
		params = (self.wh[0] / self.dpi, self.wh[1] / self.dpi) + (self.x1, self.y1, self.dx, self.dy) * 2
		header = """<?xml version="1.0" encoding="utf-8"?>
					<svg xmlns="http://www.w3.org/2000/svg"
						 xmlns:xlink="http://www.w3.org/1999/xlink"
						 preserveAspectRatio="none"
						 width="%fin" height="%fin" viewBox="%f %f %f %f">
					<g fill-rule="evenodd">
					<rect x="%f" y="%f" width="%f" height="%f" fill="white"/>\n""" % params
		footer = "\n</g>\n</svg>"

		f = open(file_name, 'w')
		f.write(header + '\n\t'.join(self.svg) + footer)
		f.close()


# Example:
if __name__ == '__main__':

	# this is necessary for reading image formats other than PNG
	from PyQt4.QtGui import QApplication
	app = QApplication(sys.argv)

	import time

	def ph(i):	# progress_handler
		if i == 0:
			print('\n'+ph._message)
		permil = int((i+1)/ph._maxval * 1000)
		if not permil % 100:
			print(permil/10, '%')

## INIT
	tracer = Tracer('image.jpg', progress_handler = ph)
	print("\nImage resolution: %ix%i, %idpi" % tuple(tracer.wh + [tracer.dpi])) # dpi gathered from the image
	time.clock()

## PART 1
	# here we trace the image using multiple curves
	n = 1000
	tracer.ph._message = 'Tracing by ' + str(n) + ' lines'
	tracer.ph._maxval = n + 1
	for i in range(n + 1):
		x = lambda t: t
		y = lambda t: t**2 * (1 - 2*i/n) + 1 - 2*i/n
		tracer.append_func(x, y, [-1.0, 1.0], res=1, polar=False, width_range=[0, 1.8], tolerance=0.0)
		tracer.ph(i)

	print("\nPART 1 STATS\nNodes: %i\nObjects: %i\nTotal curve length: %.3f mm" % \
		 (tracer.nodes_count, tracer.objects_count, tracer.total_length * 25.4))
	# save result
	tracer.save_svg()

## PART 2
	tracer.clear() # image, dimensions and scale remain while svg data and stats cleared
	tracer.dpi = 180.0

	# graph in rectangular coordinates
	x = lambda t: t
	y = lambda t: 0.5 * sin(t * pi)
	tracer.append_func(x, y, [-1.0, 1.0], width_range=[10.0, 10.0])	# max and min with are same, output is outline

	# graph in polar coordinates using uniform angle change
	r = lambda a: sin(a * 2)
	tracer.append_func(r, None, [0, 2*pi], width_range=[0.0, 10.0])

	print("\nPART 2 STATS\nNodes: %i\nObjects: %i\nTotal curve length: %.3f inches" % \
		 (tracer.nodes_count, tracer.objects_count, tracer.total_length))
	tracer.save_svg('plot.svg')

	print("\nTime without conversion to grayscale:", round(time.clock(), 5), 's')
