import sys


class Fe:
    fe = 'Fe'
    pre1 = -67.40
    pre2 = -30.00
    norm1 = 77.96
    norm2 = 250.60


class EdgeData:
    storeName = 'edgeData'
    startEnergy = 7118.5
    endEnergy = 7123.5


class MainPeakData:
    storeName = 'mainPeakData'
    startEnergy = 7123.5
    endEnergy = 7135.0


class IO:
    sampleNameHeader = 'sample number'
    sampleFormulaHeader = 'formula'
    metaFileName = 'meta.csv'


class Const:
    version = '1.0.0'
    Fe = Fe()
    EdgeData = EdgeData()
    MainPeakData = MainPeakData()
    IO = IO()


sys.modules[__name__] = Const()
