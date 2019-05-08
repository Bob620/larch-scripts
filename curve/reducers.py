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


def findDipInList(lowest, current):
    if current[1] < lowest[1]:
        return current
    return lowest


def findPeakInList(highest, current):
    if current[1] > highest[1]:
        return current
    return highest

def findPeak(data, currentValue):
    if type(data) is not list:
        data = [[], [], (0, data)]

    peaks = data[0]
    currentSeq = data[1]
    lastPoint = data[2]
    currentPoint = (lastPoint[0] + 1, currentValue)

    if currentPoint[1] >= lastPoint[1]:
        currentSeq.append(currentPoint)
        if len(currentSeq) > 6:
            currentSeq.pop(0)
    elif len(currentSeq) > 5 and lastPoint[1] <= currentSeq[5][1] > currentSeq[0][1]:
        currentSeq.append(currentPoint)

    if len(currentSeq) >= 11:
        peaks.append(currentSeq)
        currentSeq = []

    data[1] = currentSeq
    data[2] = currentPoint
    return data
