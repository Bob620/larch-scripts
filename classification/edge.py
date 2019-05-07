import constants


# Analyzes and constructs the edge definition of the main peak's edge between the pre-edge and main peak
# * Balanced, Positive, and Negative are in relation to the linear line fit of the edge
# * Linear, Below, and Above are in relation to hte linear line fit of the edge
# * High defines an X-orientation-like edge peak
def features(lineSet):
    definition = []
    store = lineSet.get_store(constants.EdgeData.storeName)

    if abs(store.farthestPositiveDiff) <= 0.01 and abs(store.farthestNegativeDiff) <= 0.01:
        definition.append('linear')  # Neither pos nor neg are far away from linear, so it must fit *generally* linearly
    elif abs(store.farthestPositiveDiff) <= 0.01:
        definition.append('below')  # Since pos <= small value but neg isn't, must be negatively skewed
    elif abs(store.farthestNegativeDiff) <= 0.01:
        definition.append('above')  # Since neg <= small value but pos isn't, must be positively skewed

    posNegDiff = abs(store.farthestPositiveDiff) - abs(store.farthestNegativeDiff)
    if abs(posNegDiff) <= 0.01:
        definition.append('balanced')  # The negative and positive diffs are relatively equal-distance from linear
    elif posNegDiff >= 0.01:
        definition.append('pos skewed')
    elif posNegDiff <= -0.01:
        definition.append('neg skewed')

    if abs(store.farthestPositiveDiff) >= 0.1:
        definition.append('high')  # The farthest positive is insanely high, generally X orientation
    return definition
