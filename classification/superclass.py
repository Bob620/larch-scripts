import constants


def classify(lineSet, edgeClasses, initialPeakClasses, secondPeakClasses):
    mainPeakStore = lineSet.get_store(constants.MainPeakData.storeName)
    data = lineSet.get_data()
    superClass = []

    if 'above' not in edgeClasses:
        superClass.append('slope')
    else:
        superClass.append('round')

    initPeakHeight = mainPeakStore.smoothedPeak[mainPeakStore.initialPeakIndex]
    if 'shoulder' in initialPeakClasses:
        initPeakHeight = mainPeakStore.smoothedPeak[mainPeakStore.shoulderCenterIndex]

    # Calculate the wanted energy value index for a plateau
    secondPeakIndex = 0
    for j in range(0, len(data.energy)):
        energyDiff = abs(data.energy[j] - 7130.0)
        if energyDiff < abs(data.energy[secondPeakIndex] - 7130.0):
            secondPeakIndex = j

    secondPeakHeight = mainPeakStore.smoothedPeak[secondPeakIndex]
    if 'peak' in secondPeakClasses:
        secondPeakHeight = mainPeakStore.peaks[0].peakSmoothed
        secondPeakIndex = mainPeakStore.peaks[0].actualPeakIndex
    if 'double peak' in secondPeakClasses and 'back' in secondPeakClasses:
        secondPeakHeight = mainPeakStore.peaks[1].peakSmoothed
        secondPeakIndex = mainPeakStore.peaks[1].actualPeakIndex

    superClass.append(str(initPeakHeight / secondPeakHeight).ljust(10)[:5])
    superClass.append(str(secondPeakIndex))
    superClass.append(str(data.energy[secondPeakIndex]).ljust(10)[:8])

    return superClass