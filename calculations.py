import math

import constants


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


def main_peak(lineSet):
    return


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
