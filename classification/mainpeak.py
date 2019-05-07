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
def secondPeak(lineSet):
    pass
