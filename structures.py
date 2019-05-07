class sequence(object):
    def __init__(self, elements):
        self.list = elements



        self.dip = elements[0]
        self.peak = elements[0]
        self.variance = (elements[1][0] - elements[0][0], self.peak[1] - self.dip[1])
