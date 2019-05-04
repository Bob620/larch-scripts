from functools import reduce

import math

import constants

from scipy import signal
import matplotlib.pyplot as plt


class EdgeData:
    def __init__(self):
        self.startIndexDiff = 0  # diff from wanted value vs actual data point
        self.startIndex = 0  # normalized index of start of edge
        self.startValue = 0  # value at the start index

        self.endIndexDiff = 0  # diff from wanted value vs actual data point
        self.endIndex = 0  # normalized index of end of edge
        self.endValue = 0  # value at the end index

        self.linearLine = []  # array of linear line to compare against actual edge
        self.avgTangentSlope = 0  # average slope at farthest positive index
        self.shoulderAngle = 0  # avg slope angle with horizontal

        self.farthestPositiveIndex = 0  # (normalized after use) farthest(+) point away from expected linear
        self.farthestPositiveDiff = 0  # difference from expected linear value

        self.farthestNegativeIndex = 0  # (normalized after use) farthest(-) point away from expected linear
        self.farthestNegativeDiff = 0  # difference from expected linear value

        self.closestIndex = 0  # (normalized after use) closest index to the linear (expected between + and -)
        self.closestDiff = math.inf  # We want the smallest possible diff


class MainPeakData:
    def __init__(self):
        self.smoothedPeak = []

        self.startIndex = 0
        self.startIndexDiff = 0
        self.startValue = 0

        self.endIndex = 0
        self.endIndexDiff = 0
        self.endValue = 0

        self.derivative = []

        self.initialPeakIndex = 0
        self.initialPeakSmoothed = []

        self.peakBound = [0, 0]
        self.peakCenter = 0
        self.peakCenterDiff = 0
        self.peakCenterOffset = 0

        self.lowIndex = 0
        self.lowSmoothed = 0

        self.middlePeakIndex = 0
        self.middlePeakSmoothed = []

        self.lastPeakIndex = 0
        self.lastPeakSmoothed = []


def pre_edge(lineSet):
    return


def edge(lineSet):
    data = lineSet.get_data()

    if data.norm_corr is None:
        raise Exception('Calculate the abs_corr for ${0}'.format(lineSet.get_name()))

    edgeData = EdgeData()

    # Calculate the start and end points that match the *wanted* start and end positions of the edge
    for j in range(0, len(data.energy)):
        startEnergyD = abs(data.energy[j] - constants.EdgeData.startEnergy)
        if startEnergyD < abs(data.energy[edgeData.startIndex] - constants.EdgeData.startEnergy):
            edgeData.startIndexDiff = abs(data.energy[edgeData.startIndex] - constants.EdgeData.startEnergy)
            edgeData.startIndex = j

        endEnergyD = abs(data.energy[j] - constants.EdgeData.endEnergy)
        if endEnergyD < abs(data.energy[edgeData.endIndex] - constants.EdgeData.endEnergy):
            edgeData.endIndexDiff = abs(data.energy[edgeData.startIndex] - constants.EdgeData.endEnergy)
            edgeData.endIndex = j

    # Grab the actual values
    edgeData.startValue = data.norm_corr[edgeData.startIndex]
    edgeData.endValue = data.norm_corr[edgeData.endIndex]
    lastValue = edgeData.startValue

    # Create a linear line between the start and end values with same length
    for j in range(0, edgeData.endIndex - edgeData.startIndex):
        edgeData.linearLine.append(lastValue)
        lastValue += (edgeData.endValue - edgeData.startValue) / (edgeData.endIndex - edgeData.startIndex)

    edgeData.linearLine.append(edgeData.endValue)

    # Calculate the single point of largest deviation from linearity on the positive side (has to be first)
    for j in range(0, len(edgeData.linearLine)):
        diff = data.norm_corr[edgeData.startIndex + j] - edgeData.linearLine[j]

        if diff > 0 and diff > edgeData.farthestPositiveDiff:
            edgeData.farthestPositiveDiff = diff
            edgeData.farthestPositiveIndex = j

    # Calculate where the line intersects the linear line (has to be second)
    for j in range(edgeData.farthestPositiveIndex, len(edgeData.linearLine)):
        diff = data.norm_corr[edgeData.startIndex + j] - edgeData.linearLine[j]

        if diff < edgeData.closestDiff:
            edgeData.closestDiff = diff
            edgeData.closestIndex = j
        else:
            pass

    # Calculate the single point of largest deviation from linearity on the negative side (has to be last)
    for j in range(edgeData.closestIndex, len(edgeData.linearLine)):
        diff = data.norm_corr[edgeData.startIndex + j] - edgeData.linearLine[j]

        if diff < 0 and diff < edgeData.farthestNegativeDiff:
            edgeData.farthestNegativeDiff = diff
            edgeData.farthestNegativeIndex = j

    # Normalize the index values
    edgeData.closestIndex = edgeData.closestIndex + edgeData.startIndex
    edgeData.farthestPositiveIndex = edgeData.farthestPositiveIndex + edgeData.startIndex
    edgeData.farthestNegativeIndex = edgeData.farthestNegativeIndex + edgeData.startIndex

    # Calculate extra stuff
    edgeData.avgTangentSlope = (
                                       (data.norm_corr[edgeData.farthestPositiveIndex - 1] -
                                        data.norm_corr[edgeData.farthestPositiveIndex]) +

                                       (data.norm_corr[edgeData.farthestPositiveIndex] -
                                        data.norm_corr[edgeData.farthestPositiveIndex] + 1)
                               ) / 2

    edgeData.shoulderAngle = 180 - abs(math.degrees(math.atan(edgeData.avgTangentSlope)) - math.degrees(math.atan(0)))

    lineSet.set_store(constants.EdgeData.storeName, edgeData)
    return edgeData


def removePeaksAndDips(data, current):
    if data[0] != 0:
        data = removePeaksAndDips([0], data)

    if len(current) > 10:
        peak = current[0]
        dip = current[0]
        for item in current:
            if item[1] > peak[1]:
                peak = item
            if item[1] < dip[1]:
                dip = item

        if peak is current[len(current) - 1] and dip is current[0]:
            data.append(current)

    return data


def findSequence(data, current):
    if type(data) is not list:
        return [[[(0, current)]], current, 0]

    curSeq = data[0][len(data[0]) - 1]
    last = data[1]
    index = data[2] + 1

    if abs(last - current) <= 0.005:
        curSeq.append((index, current))
    else:
        if len(curSeq) <= 5:
            data[0][len(data[0]) - 1] = []
        else:
            data[0].append([(index, current)])

    data[1] = current
    data[2] = index

    return data

def main_peak(lineSet):
    data = lineSet.get_data()

    if data.norm_corr is None:
        raise Exception('Calculate the abs_corr for ${0}'.format(lineSet.get_name()))

    mainPeakData = MainPeakData()

    smoothedPeak = mainPeakData.smoothedPeak = signal.savgol_filter(data.norm_corr, 7, 3)

    # Calculate the start and end points that match the *wanted* start and end positions of the edge
    for j in range(0, len(data.energy)):
        startEnergyD = abs(data.energy[j] - constants.MainPeakData.startEnergy)
        if startEnergyD < abs(data.energy[mainPeakData.startIndex] - constants.MainPeakData.startEnergy):
            mainPeakData.startIndexDiff = abs(data.energy[mainPeakData.startIndex] - constants.EdgeData.startEnergy)
            mainPeakData.startIndex = j

        endEnergyD = abs(data.energy[j] - constants.MainPeakData.endEnergy)
        if endEnergyD < abs(data.energy[mainPeakData.endIndex] - constants.MainPeakData.endEnergy):
            mainPeakData.endIndexDiff = abs(data.energy[mainPeakData.startIndex] - constants.EdgeData.endEnergy)
            mainPeakData.endIndex = j

    derivative = []

    for i in range(mainPeakData.startIndex + 1, mainPeakData.endIndex + 1):
        derivative.append(data.norm_corr[i] - data.norm_corr[i - 1])

    mainPeakData.derivative = derivative

    if len(derivative) >= 9:

        sequences = reduce(removePeaksAndDips, reduce(findSequence, smoothedPeak[mainPeakData.startIndex : mainPeakData.endIndex])[0])[1:]

        secondDerivative = []
        smoothDerivative = signal.savgol_filter(derivative, 11, 2)

        for i in range(0, len(smoothDerivative)):
            secondDerivative.append(smoothDerivative[i] - smoothDerivative[i - 1])

        secondSmoothDerivative = signal.savgol_filter(secondDerivative, 11, 2)

        test = []

        for i in range(mainPeakData.startIndex, mainPeakData.endIndex):
            test.append(math.log2(data.norm_corr[i]))

        testFig, testPlt = plt.subplots()
        testPlt.set(xlabel='Energy (eV)',
                    ylabel='normalized $ \mu(E) $ D',
                    title=data.filename
                    )

        testPlt.plot(range(mainPeakData.startIndex, mainPeakData.endIndex), smoothDerivative)
        testPlt.plot(range(mainPeakData.startIndex, mainPeakData.endIndex), secondDerivative)
        testPlt.plot(range(mainPeakData.startIndex, mainPeakData.endIndex), secondSmoothDerivative)
        testPlt.plot(range(mainPeakData.startIndex, mainPeakData.endIndex), derivative, label="test")
        testPlt.plot(range(mainPeakData.startIndex, mainPeakData.endIndex), test, label="test1")

        for seq in sequences:
            if len(seq) >= 2:
                testPlt.plot(mainPeakData.startIndex + seq[0][0], test[seq[0][0]], marker='x')
                testPlt.plot(mainPeakData.startIndex + seq[len(seq) - 1][0], test[seq[len(seq) - 1][0]], marker='x')

        testFig.show()

    mainPeakData.startValue = data.norm_corr[mainPeakData.startIndex]
    mainPeakData.endValue = data.norm_corr[mainPeakData.endIndex]

    mainPeakData.initialPeakIndex = mainPeakData.startIndex
    mainPeakData.initialPeakSmoothed = mainPeakData.startIndex

    mainPeakData.middlePeakIndex = mainPeakData.startIndex
    mainPeakData.middlePeakSmoothed = mainPeakData.startIndex

    mainPeakData.lastPeakIndex = mainPeakData.startIndex
    mainPeakData.lastPeakSmoothed = mainPeakData.startIndex

    peakNumber = 0
    decreased = 0
    increased = 0
    for i in range(mainPeakData.startIndex, mainPeakData.endIndex):
        if decreased >= 10:
            peakNumber = 1
            if smoothedPeak[mainPeakData.lowIndex] > smoothedPeak[i]:
                increased = 0
                mainPeakData.lowIndex = i
            else:
                increased += 1

        if increased >= 10:
            break

        if peakNumber == 0:
            if smoothedPeak[mainPeakData.initialPeakIndex] < smoothedPeak[i]:
                decreased = 0
                mainPeakData.initialPeakIndex = i
                mainPeakData.lowIndex = i
            else:
                decreased += 1

    # Peak Boundaries
    initialPeakValue = smoothedPeak[mainPeakData.initialPeakIndex]

    for i in range(mainPeakData.startIndex, mainPeakData.initialPeakIndex):
        if initialPeakValue - smoothedPeak[i] < 0.01:
            mainPeakData.peakBound[0] = i
            break

    for i in range(mainPeakData.initialPeakIndex, mainPeakData.lowIndex):
        if initialPeakValue - smoothedPeak[i] < 0.01:
            mainPeakData.peakBound[1] = i

    actualDiff = abs(smoothedPeak[mainPeakData.peakBound[0]] - smoothedPeak[mainPeakData.peakBound[1]])
    if smoothedPeak[mainPeakData.peakBound[0]] > smoothedPeak[mainPeakData.peakBound[1]]:
        highDiff = abs(smoothedPeak[mainPeakData.peakBound[1]] - smoothedPeak[mainPeakData.peakBound[0] - 1])
        lowDiff = abs(smoothedPeak[mainPeakData.peakBound[1] - 1] - smoothedPeak[mainPeakData.peakBound[0]])
        if highDiff < lowDiff:
            if highDiff < actualDiff:
                mainPeakData.peakBound[0] = mainPeakData.peakBound[0] - 1
        else:
            if lowDiff < actualDiff:
                mainPeakData.peakBound[1] = mainPeakData.peakBound[1] - 1
    else:
        highDiff = abs(smoothedPeak[mainPeakData.peakBound[0]] - smoothedPeak[mainPeakData.peakBound[1] - 1])
        lowDiff = abs(smoothedPeak[mainPeakData.peakBound[0] - 1] - smoothedPeak[mainPeakData.peakBound[1]])
        if highDiff < lowDiff:
            if highDiff < actualDiff:
                mainPeakData.peakBound[1] = mainPeakData.peakBound[1] - 1
        else:
            if lowDiff < actualDiff:
                mainPeakData.peakBound[0] = mainPeakData.peakBound[0] - 1

    mainPeakData.peakCenter = data.energy[mainPeakData.peakBound[0]] + (
                data.energy[mainPeakData.peakBound[1]] - data.energy[mainPeakData.peakBound[0]]) / 2
    mainPeakData.peakCenterDiff = data.energy[mainPeakData.initialPeakIndex] - mainPeakData.peakCenter

    mainPeakData.peakCenterOffset = mainPeakData.initialPeakIndex - mainPeakData.peakBound[0]
    for i in range(mainPeakData.peakBound[0], mainPeakData.peakBound[1]):
        if data.energy[i] <= mainPeakData.peakCenter:
            mainPeakData.peakCenterOffset = i

    # Working backwards, find the last peak

    #    for i in range(mainPeakData.lowIndex, constants.MainPeakData.endEnergy)[::-1]:

    lineSet.set_store(constants.MainPeakData.storeName, mainPeakData)

    return
