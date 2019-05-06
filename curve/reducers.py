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
