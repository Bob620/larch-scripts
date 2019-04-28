import matplotlib.pyplot as plt


def interactive_legend(plot=None, sets=None):
    if plot is None:
        plot = plt.gca()
    if plot.legend_ is None:
        plot.legend()
    return InteractiveLegend(plot.legend_, sets)


class ElementSet(object):
    def __init__(self, toggleable, clickable):
        self.toggleable = []
        self.clickable = []
        self.visible = True

        if type(toggleable) is list:
            self.toggleable.extend(toggleable)
        else:
            self.toggleable.append(toggleable)

        if type(clickable) is list:
            self.clickable.extend(clickable)
        else:
            self.clickable.append(clickable)

    def get_visibility(self):
        return self.visible

    def add_toggleable(self, item):
        if type(item) is list:
            self.toggleable.extend(item)
        else:
            self.toggleable.append(item)

    def add_clickable(self, item):
        if type(item) is list:
            self.toggleable.extend(item)
        else:
            self.toggleable.append(item)

    def toggle(self):
        self.visible = not self.visible
        for element in self.toggleable:
            element.set_visible(self.visible)


# https://stackoverflow.com/questions/31410043/hiding-lines-after-showing-a-pyplot-figure
# https://matplotlib.org/examples/event_handling/legend_picking.html
# https://stackoverflow.com/questions/22201869/matplotlib-event-handling-line-picker

# Allows connection of elements to each other and specify which ones can be clicked to toggle all elements
class InteractiveLegend(object):
    def __init__(self, legend, defaultSetReference):
        self.legend = legend
        self.fig = legend.axes.figure

        if defaultSetReference is None:
            self.elementSets = {}
            self.labelReference = {}

            # self._build_lookups()
        else:
            self.elementSets = defaultSetReference

        # self._setup_connections()
        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(5)

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
    # self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self):
        labels = [t.get_text() for t in self.legend.texts]
        legendLines = self.legend.legendHandles

        label2legendLine = dict(zip(labels, legendLines))
        legendLine2text = dict(zip(legendLines, self.legend.texts))

        for line in self.legend.axes.get_children():
            if line.get_label() in labels:
                legendLine = label2legendLine[line.get_label()]
                text = legendLine2text[legendLine]
                elementSet = ElementSet([line, legendLine], [legendLine, text])

                self.labelReference[text.get_text()] = elementSet
                self.elementSets[legendLine] = elementSet
                self.elementSets[text] = elementSet

    def on_pick(self, event):
        test = event.artist.get_gid()

        (gid, toggleFunc) = test

        toggleFunc()

        # self.elementSets[event.artist.get_gid].toggle()
        self.update()

    def update(self):
        self.fig.canvas.draw()

    def show(self):
        plt.show(block=True)
