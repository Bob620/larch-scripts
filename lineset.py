from uuid import uuid4

import constants


class LineSet(object):
    def __init__(self, data, formula):
        self.uuid = uuid4()
        self.data = data
        self.store = {}
        self.formula = formula
        self.plot = None
        self.abscorrLine = None
        pass

    def get_uuid(self):
        return self.uuid

    def get_data(self):
        return self.data

    def get_name(self):
        return self.data.filename

    def get_formula(self):
        return self.formula

    def set_name(self, name):
        self.data.filename = name

    def set_plot(self, plot):
        self.plot = plot

    def set_store(self, name, data):
        self.store[name] = data

    def get_store(self, name):
        return self.store[name] or {}

    def plot_abs_corr(self):
        if self.plot and self.data.norm_corr is not None:
            self.abscorrLine = self.plot.plot(self.data.energy,
                                              self.data.norm_corr,
                                              label=self.data.filename + '_abs_corr',
                                              marker=None
                                              )
