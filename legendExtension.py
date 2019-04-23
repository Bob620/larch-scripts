from legend import ElementSet


class LineSet(object):
    def __init__(self, line, data, lineSearchSet=None):
        self.name = data.filename
        self.data = data
        self.line = line
        self.lineSearchSet = lineSearchSet

        line.get_figure().legend()

        self.lineSet = ElementSet([line, ])


class PreEdgeSet(ElementSet):
    def __init__(self, lineSet, toggleable, clickable):

        super().__init__(toggleable, clickable)


class EdgeSet(ElementSet):
    def __init__(self, lineSet, linear, points):
        toggleable = [linear]
        toggleable.extend(points)
        super().__init__(toggleable, clickable)


class MainPeakSet(ElementSet):
    def __init__(self, lineSet, toggleable, clickable):
        super().__init__(toggleable, clickable)