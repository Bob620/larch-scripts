from uuid import uuid4

import constants


class EdgeLines(object):
    def __init__(self, plot, gid, farthestPos=None, farthestNeg=None, closest=None, linear=None, visible=True):
        self.plot = plot
        #        legend = plot.legend_
        #        if legend is None:
        #            plot.legend()
        #            legend = plot.legend_

        self.farthestPos = farthestPos
        self.farthestNeg = farthestNeg
        self.closest = closest
        self.linear = linear

        self.visible = visible

        #        textToHandle = dict(zip(map(
        #            lambda text: text.get_text(), legend.texts
        #        ), zip(legend.legendHandles, legend.texts)))
        #        self.handle = textToHandle[linear._label]

        #        self.handle[0].set_label('linear')
        #        self.handle[0].set_gid(gid)
        #        self.handle[0].set_picker(5)

        #        self.handle[1].set_text('linear')
        #        self.handle[1].set_gid(gid)
        #        self.handle[1].set_picker(5)

        self.toggle(self.visible)

    def toggle(self, visibility=None):
        if visibility is None:
            self.visible = not self.visible
        else:
            self.visible = visibility

        self.farthestPos.set_visible(self.visible)
        self.farthestNeg.set_visible(self.visible)
        self.closest.set_visible(self.visible)
        self.linear.set_visible(self.visible)


class AbscorrLine:
    def __init__(self, plot, gid, abscorr):
        self.abscorr = abscorr
        self.visible = True

#        legend = plot.legend_

#        test = Line2D([0], [0], label=abscorr._label,
#                      gid=gid,
#                      pickradius=5
#                      )

#        legend.legendHandles.append(test)

#        plot.legend(handles=legend.legendHandles)

        self.toggle(self.visible)

    def toggle(self, visibility=None):
        if visibility is None:
            self.visible = not self.visible
        else:
            self.visible = visibility

        self.abscorr.set_visible(self.visible)


class LineSet(object):
    def __init__(self, data, formula):
        self.uuid = uuid4()
        self.data = data
        self.store = {}
        self.formula = formula
        self.plot = None
        self.abscorr = None
        self.edge = None
        pass

    def get_uuid(self):
        return self.uuid.hex

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

    def toggle_abs_corr(self):
        if self.abscorrLine is not None:
            self.abscorrLineVisible = not self.abscorrLineVisible
            self.abscorrLine.set_visible(self.abscorrLineVisible)

    def toggle_edge(self):
        if self.edge is not None:
            self.edge.toggle()

    def plot_abs_corr(self):
        if self.plot and self.data.norm_corr is not None:
            self.abscorr = AbscorrLine(self.plot, (self.get_uuid(), self.toggle_edge),
                                       self.plot.plot(self.data.energy,
                                                      self.data.norm_corr,
                                                      label=self.data.filename + '_abs_corr',
                                                      marker=None,
                                                      gid=(self.get_uuid(), self.toggle_abs_corr)
                                                      )[0]
                                       )

    def plot_edge(self):
        if self.plot and self.store[constants.EdgeData.storeName]:
            store = self.store[constants.EdgeData.storeName]
            self.edge = EdgeLines(self.plot, (self.get_uuid(), self.toggle_edge),
                                  farthestPos=self.plot.plot(self.data.energy[store.farthestPositiveIndex],
                                                             self.data.norm_corr[store.farthestPositiveIndex],
                                                             marker='o',
                                                             markersize=5,
                                                             gid=(self.get_uuid(), self.toggle_edge)
                                                             )[0],
                                  farthestNeg=self.plot.plot(self.data.energy[store.farthestNegativeIndex],
                                                             self.data.norm_corr[store.farthestNegativeIndex],
                                                             marker='x',
                                                             markersize=5,
                                                             gid=(self.get_uuid(), self.toggle_edge)
                                                             )[0],
                                  closest=self.plot.plot(self.data.energy[store.closestIndex],
                                                         self.data.norm_corr[store.closestIndex],
                                                         marker='+',
                                                         markersize=5,
                                                         gid=(self.get_uuid(), self.toggle_edge)
                                                         )[0],
                                  linear=self.plot.plot(self.data.energy[store.startIndex:store.endIndex + 1],
                                                        store.linearLine,
                                                        linestyle='--',
                                                        label='Linear ' + self.get_uuid(),
                                                        gid=(self.get_uuid(), self.toggle_edge)
                                                        )[0]
                                  )


            self.plot.plot(self.data.energy[store.farthestPositiveIndex],
                           self.data.norm_corr[store.farthestPositiveIndex],
                           marker='o',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.farthestNegativeIndex],
                           self.data.norm_corr[store.farthestNegativeIndex],
                           marker='x',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.closestIndex],
                           self.data.norm_corr[store.closestIndex],
                           marker='+',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.startIndex:store.endIndex + 1],
                           store.linearLine,
                           linestyle='--',
                           label='Linear'
                           )

    def plot_main_peak(self):
        if self.plot and self.store[constants.MainPeakData.storeName]:
            store = self.store[constants.MainPeakData.storeName]

            self.plot.plot(self.data.energy, store.smoothedPeak,
                           linestyle=':',
                           label='smoothed'
                           )

            self.plot.plot(self.data.energy[store.initialPeakIndex], store.smoothedPeak[store.initialPeakIndex],
                           marker='o',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.lowIndex], store.smoothedPeak[store.lowIndex],
                           marker='x',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.peakBound[0]], store.smoothedPeak[store.peakBound[0]],
                           marker='+',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.peakBound[1]], store.smoothedPeak[store.peakBound[1]],
                           marker='+',
                           markersize=5
                           )

            self.plot.plot(self.data.energy[store.peakCenterOffset], store.smoothedPeak[store.peakCenterOffset],
                           marker='+',
                           markersize=5
                           )

            if store.initialPeakIsShoulder:
                self.plot.plot(store.shoulderCenter,
                               store.smoothedPeak[store.shoulderCenterIndex],
                               marker='+',
                               markersize=5
                               )

            for seq in store.shoulders:
                self.plot.plot(self.data.energy[seq[0][0]], store.smoothedPeak[seq[0][0]],
                               marker='D',
                               markersize=5
                               )

                self.plot.plot(self.data.energy[seq[len(seq) - 1][0]], store.smoothedPeak[seq[len(seq) - 1][0]],
                               marker='D',
                               markersize=5
                               )

#            for seq in store.peaks:
#                self.plot.plot(self.data.energy[seq[0][0]], store.smoothedPeak[seq[0][0]],
#                               marker='H',
#                               markersize=5
#                               )

#                self.plot.plot(self.data.energy[seq[len(seq) - 1][0]], store.smoothedPeak[seq[len(seq) - 1][0]],
#                               marker='H',
#                               markersize=5
#                               )

            for peakData in store.peaks:
                self.plot.plot(self.data.energy[peakData.lowIndex], store.smoothedPeak[peakData.lowIndex],
                               marker='*',
                               markersize=5
                               )

                self.plot.plot(self.data.energy[peakData.actualPeakIndex], store.smoothedPeak[peakData.actualPeakIndex],
                               marker='o',
                               markersize=5
                               )

                self.plot.plot(peakData.peakEnergy, store.smoothedPeak[peakData.actualPeakIndex],
                               marker='+',
                               markersize=5
                               )

                self.plot.plot(self.data.energy[peakData.highIndex], store.smoothedPeak[peakData.highIndex],
                               marker='*',
                               markersize=5
                               )
