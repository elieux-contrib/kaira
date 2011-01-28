#
#    Copyright (C) 2010 Stanislav Bohm
#
#    This file is part of Kaira.
#
#    Kaira is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License, or
#    (at your option) any later version.
#
#    Kaira is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Kaira.  If not, see <http://www.gnu.org/licenses/>.
#

import gtk
from events import EventSource

class NetCanvas(gtk.DrawingArea, EventSource):
	"""
		Events: button_down, button_up, mouse_move
	"""
	def __init__(self, net, draw_cb, vconfig, zoom = 1.0):
		gtk.DrawingArea.__init__(self);
		EventSource.__init__(self)
		self.net = net
		self.zoom = zoom
		self.viewport = (0,0)
		self.vconfig = vconfig
		self.draw_cb = draw_cb
		self.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
		self.connect("expose_event", self._expose)
		self.connect("button_press_event", self._button_down)
		self.connect("button_release_event", self._button_up)
		self.connect("motion_notify_event", self._mouse_move)

	def set_viewport(self, viewport):
		self.viewport = viewport
		self.redraw()

	def get_viewport(self):
		return self.viewport

	def set_vconfig(self, vconfig):
		self.vconfig = vconfig
		self.redraw()

	def redraw(self):
		self.queue_draw()

	def zoom_in(self):
		self.zoom *= 1.25
		self.redraw()

	def zoom_out(self):
		self.zoom /= 1.25
		self.redraw()

	def get_zoom(self):
		return self.zoom

	def set_size_and_viewport_by_net(self):
		((l, t), (r, b)) = self.net.corners()
		sizex = r - l + 100
		sizey = b - t + 100
		self.set_size_request(int(sizex * self.zoom), int(sizey * self.zoom))
		self.set_viewport((l , t ))

	def _expose(self, w, event):
		cr = self.window.cairo_create()
		self.cr = cr
		cr.rectangle(event.area.x, event.area.y,
				event.area.width, event.area.height)
		cr.clip()
		self._draw(cr, *self.window.get_size())

	def _draw(self, cr, width, height):
		cr.set_source_rgb(0.8, 0.8, 0.8)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		cr.translate(self.viewport[0], self.viewport[1])
		cr.scale(self.zoom, self.zoom)
		self.net.draw(cr, self.vconfig)
		if self.draw_cb:
			self.draw_cb(cr, width, height)

	def _mouse_to_canvas(self, event):
		return self.cr.device_to_user(event.x, event.y)

	def _button_down(self, w, event):
		self.emit_event("button_down", event, self._mouse_to_canvas(event))

	def _button_up(self, w, event):
		self.emit_event("button_up", event, self._mouse_to_canvas(event))

	def _mouse_move(self, w, event):
		self.emit_event("mouse_move", event, self._mouse_to_canvas(event))


class MultiCanvas(gtk.DrawingArea):

	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.lines = []
		self.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
		self.connect("expose_event", self._expose)
		self.connect("button_press_event", self._button_down)

	def register_line(self, view_size, view_pos, callbacks):
		""" callbacks is list of tuple for each area in line,
			first element of tuple is draw_callback, second is click_callback """
		self.lines.append( (view_size, view_pos, callbacks) )

	def redraw(self):
		self.queue_draw()

	def end_of_registration(self):
		if self.lines:
			self.size_x = max([ s[0] * len(cbs) for s,v,cbs in self.lines ])
			self.size_y = sum([ s[1] for s,v,cbs in self.lines ])
		else:
			self.size_x = 0
			self.size_y = 0
		self.set_size_request(self.size_x, self.size_y)

	def _button_down(self, w, event):
		position = (event.x, event.y)
		pos_and_callbacks = self._find_area_callbacks(position)
		if pos_and_callbacks is not None:
			p, callbacks = pos_and_callbacks
			callbacks[1](p)

	def _find_area_callbacks(self, position):
		""" Returns relative position and callbacks of area """
		px, py = position
		y = 0
		for (sx, sy),(vx, vy),cbs in self.lines:
			y += sy
			if py < y:
				i = int(px / sx)
				if i < 0 or i >= len(cbs):
					return None
				return ((px % sx + vx, py - (y - sy) + vy), cbs[i])

	def _expose(self, w, event):
		cr = self.window.cairo_create()
		cr.rectangle(event.area.x, event.area.y,
				event.area.width, event.area.height)
		cr.clip()
		self._draw(cr, *self.window.get_size())

	def _draw(self, cr, width, height):
		cr.set_source_rgb(0.8, 0.8, 0.8)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		if not self.lines:
			return
		self._draw_grid(cr)

		y = 0
		for (sx,sy), (vx, vy), callbacks in self.lines:
			for i,(draw_cb, click_cb) in enumerate(callbacks):
				cr.save()
				cr.rectangle(sx * i, y, sx, sy)
				cr.clip()
				cr.translate(sx * i - vx, y - vy)
				draw_cb(cr, sx, sy, vx, vy)
				cr.restore()
			y += sy

	def _draw_grid(self,cr):
		y = 0
		cr.set_line_width(1.5)
		cr.set_source_rgb(0.1,0.1,0.1)

		for (sx,sy), view_pos, callbacks in self.lines:
			y2 = y + sy
			cr.move_to(0, y2)
			cr.line_to(self.size_x, y2)
			cr.stroke()
			for i in xrange(1, len(callbacks) + 1):
				cr.move_to(i * sx, y)
				cr.line_to(i * sx, y2)
				cr.stroke()
			y = y2
