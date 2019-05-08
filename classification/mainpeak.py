import constants


# Analyzes and constructs the peak definition of the initial peak in the main peak sector
# * Shoulder defines a unique shoulder is found where the initial peak would be
# * Shoulder(?) defines a possible shoulder that for some reason isn't detected correctly but is still there
# * Peak defines a peak located where the initial peak should be (yay?)
# * Centered/Skewed:
#     Centered - Center point lies between InitialPeakLow and InitialPeakHigh
#     Left Skewed - Center point lies below InitialPeakLow, high peakBound is between InitialPeakLow and InitialPeakHigh
#     Right Skewed - Center point lies above InitialPeakHigh,low peakBound is between InitialPeakLow and InitialPeakHigh
#     Far Skewed - Entire peakBound range is outside InitialPeakLow to InitialPeakHigh range to corresponding side
def initialPeak(lineSet):
    definition = []
    store = lineSet.get_store(constants.MainPeakData.storeName)

    # if we have a shoulder that occurs before the lowest point between the initial and second peak we need to check to
    #   see if the shoulder is replacing the initial peak, which it has to(?)
    if len(store.shoulders) > 0 and store.shoulders[0][0][0] < store.lowIndex:
        if store.initialPeakIsShoulder:
            definition.append('shoulder')
            if 7125.3 < store.shoulderCenter < 7125.7:
                definition.append('centered')
            elif store.shoulderCenter <= 7125.3 < store.shoulderBound[1]:
                definition.append('left skewed')
            elif store.shoulderBound[0] < 7125.7 <= store.shoulderCenter:
                definition.append('right skewed')
            elif store.shoulderBound[1] <= 7125.3:
                definition.append('far left skewed')
            elif store.shoulderBound[0] >= 7125.7:
                definition.append('far right skewed')
        else:
            definition.append('shoulder(?)')
    else:
        definition.append('peak')
        if 7125.3 < store.peakCenter < 7125.7:
            definition.append('centered')
        elif store.peakCenter <= 7125.3 < store.peakBound[1]:
            definition.append('left skewed')
        elif store.peakBound[0] < 7125.7 <= store.peakCenter:
            definition.append('right skewed')
        elif store.peakBound[1] <= 7125.3:
            definition.append('far left skewed')
        elif store.peakBound[0] >= 7125.7:
            definition.append('far right skewed')

    return definition


# Analyzes and constructs the peak definition of the second peak in the main peak sector
# * Tall/Short/Equal defines the height relative to the initial peak
# * Peak/Double Peak/Plateau/More than 2 Peaks
#     Plateau - No peaks are identified, can assume it's a plateau
#     Peak - One peak has been identified
#     Double Peak - Two peaks have been identified
#     More than 2 Peaks - Should never happen because there are 3 peaks in this bit, wat
def secondPeak(lineSet):
    definition = []
    store = lineSet.get_store(constants.MainPeakData.storeName)

    if len(store.peaks) == 0:
        definition.append('plateau')
    elif len(store.peaks) == 1:
        definition.append('peak')
        peak = store.peaks[0]

        if abs(store.smoothedPeak[peak.actualPeakIndex] - store.smoothedPeak[store.initialPeakIndex]) < 0.01:
            definition.append('equal')
        elif store.smoothedPeak[peak.actualPeakIndex] > store.smoothedPeak[store.initialPeakIndex]:
            definition.append('tall')
        else:
            definition.append('short')

    elif len(store.peaks) == 2:
        definition.append('double peak')
        peakOne = store.peaks[0]
        peakTwo = store.peaks[1]
    else:
        definition.append('More than 2 peaks')

    return definition
