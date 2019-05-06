import os
import constants

from lineset import LineSet

from larch_plugins.io import read_ascii


def readMetaFile(metaUri):
    meta = {}

    try:
        metaFile = open(metaUri, 'r')
    except IOError:
        raise IOError('No metadata file found with the name \'{}\''.format(metaUri))
    else:
        metaLines = metaFile.readlines()
        metaFile.close()

        metaColumnNames = []
        for line in metaLines:
            info = line.strip('\n').split(',')

            if len(metaColumnNames) == 0:
                for name in info:
                    metaColumnNames.append(name.strip().lower())

            else:
                if len(info) >= len(metaColumnNames):
                    meta[info[metaColumnNames.index(constants.IO.sampleNameHeader)].strip()] = {
                        'formula': info[metaColumnNames.index(constants.IO.sampleFormulaHeader)]
                            .strip().replace('\t', '').replace('"', '').replace('\'', '')
                    }
    return meta


# Most likely want to process these files manually to get the right labels automatically
def readFile(uri):
    return read_ascii(uri, labels='energy 0 i0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 Fe_Ka1 Fe_Ka2 Fe_Ka3 Fe_Ka4')


def readStructDirectory(dirUri, metaFileName=constants.IO.metaFileName):
    directory = os.scandir(dirUri)
    metadata = readMetaFile(dirUri + metaFileName)

    files = {}
    failed = []
    skipped = []

    for entry in directory:
        if entry.is_file():
            if entry.name.endswith('.001'):  # TODO: expand this to cover more file types
                try:
                    file = readFile(entry.path)
                except Exception as err:
                    failed.append(entry.name)
                else:
                    thisMeta = None

                    for metaName, meta in metadata.items():
                        if entry.name.startswith(metaName):
                            thisMeta = meta
                            break

                    if thisMeta is not None:
                        formula = thisMeta['formula']
                        lineSet = LineSet(file, formula)
                        files[lineSet.get_uuid()] = lineSet
                    else:
                        skipped.append(entry.path)
            else:
                skipped.append(entry.path)
        else:
            skipped.append(entry.path)

    directory.close()
    return files, failed, skipped
