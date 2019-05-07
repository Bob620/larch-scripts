def getShoulders(current):
    if len(current) > 10:
        peak = current[0]
        dip = current[0]
        for item in current:
            if item[1] > peak[1]:
                peak = item
            if item[1] < dip[1]:
                dip = item

        if (peak is current[len(current) - 1] and dip is current[0]) or \
                (peak is current[0] and dip is current[len(current) - 1]):
            return True
    return False


def getPeaks(current):
    if len(current) > 10:
        peak = current[0]
        dip = current[0]
        for item in current:
            if item[1] > peak[1]:
                peak = item
            if item[1] < dip[1]:
                dip = item

        if (dip is current[len(current) - 1] or dip is current[0]) and \
                (peak is not current[0] and peak is not current[len(current) - 1]):
            return True
    return False


def getDips(current):
    if len(current) > 10:
        peak = current[0]
        dip = current[0]
        for item in current:
            if item[1] > peak[1]:
                peak = item
            if item[1] < dip[1]:
                dip = item

        if (peak is current[len(current) - 1] or peak is current[0]) or \
                (dip is not current[0] and dip is not current[len(current) - 1]):
            return True
    return False


def removeEmptyLists(item):
    if len(item) == 0:
        return False
    return True