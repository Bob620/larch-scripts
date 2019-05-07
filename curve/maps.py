def normalizeIndex(point, index):
    return index + point[0], point[1]

def normalizeSeqIndex(seq, index):
    return list(map(normalizeIndex, seq, [index] * len(seq)))
