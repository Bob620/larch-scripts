import matplotlib.pyplot as plt


# https://stackoverflow.com/questions/31410043/hiding-lines-after-showing-a-pyplot-figure
# https://matplotlib.org/examples/event_handling/legend_picking.html
# https://stackoverflow.com/questions/22201869/matplotlib-event-handling-line-picker
def interactive_legend(plot=None):
	if plot is None:
		plot = plt.gca()
	if plot.legend_ is None:
		plot.legend()
	return InteractiveLegend(plot.legend_)


class ElementSet(object):
	def __init__(self, toggleable, clickable):
		self.toggleable = toggleable
		self.clickable = clickable
		self.visible = True

	def toggle(self):
		self.visible = not self.visible
		for element in self.toggleable:
			element.set_visible(self.visible)

# Allows connection of elements to each other and specify which ones can be clicked to toggle all elements
class InteractiveLegend(object):
	def __init__(self, legend):
		self.legend = legend
		self.fig = legend.axes.figure

		self.elementSets = {}
		self.labelReference = {}

		self._build_lookups()
		self._setup_connections()

		self.update()

	def _setup_connections(self):
		for artist in self.legend.texts + self.legend.legendHandles:
			artist.set_picker(5)

		self.fig.canvas.mpl_connect('pick_event', self.on_pick)
		# self.fig.canvas.mpl_connect('button_press_event', self.on_click)

	def _build_lookups(self):
		labels = [t.get_text() for t in self.legend.texts]
		handles = self.legend.legendHandles

		label2handle = dict(zip(labels, handles))
		handle2text = dict(zip(handles, self.legend.texts))

		for artist in self.legend.axes.get_children():
			if artist.get_label() in labels:
				handle = label2handle[artist.get_label()]
				text = handle2text[handle]
				elementSet = ElementSet([artist, handle], [handle, text])

				self.labelReference[text.get_text()] = elementSet
				self.elementSets[handle] = elementSet
				self.elementSets[text] = elementSet

	def on_pick(self, event):
		try:
			self.elementSets[event.artist].toggle()
			self.update()
		except Exception:
			pass

	def update(self):
		self.fig.canvas.draw()

	def show(self):
		plt.show(block=True)
