import os
import constants

from lineset import LineSet

from larch_plugins.io import read_ascii, read_athena


def extract_athenagroup(g, abscorr=False):
    g.datatype = 'xas'
    g.filename = g.label
    g.xdat = 1.0*g.energy
    if abscorr:
        g.norm_corr = 1.0*g.mu
    g.yerr = 1.0
    g.plot_xlabel = 'energy'
    g.plot_ylabel = 'mu'
    return g


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


def readAthenaProject(uri, abscorr=False):
    project = read_athena(uri)
    groups = []

    for item in dir(project):
        if not item.startswith('_'):
            groups.append(extract_athenagroup(getattr(project, item), abscorr=abscorr))

    return groups

# Most likely want to process these files manually to get the right labels automatically
def readFile(uri):
    return read_ascii(uri, labels='energy 0 i0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 Fe_Ka1 Fe_Ka2 Fe_Ka3 Fe_Ka4')


def readStructDirectory(dirUri, abscorr=False, metaFileName=constants.IO.metaFileName):
    directory = os.scandir(dirUri)
    metadata = None
    try:
        metadata = readMetaFile(dirUri + metaFileName)
    except Exception as err:
        if abscorr is False:
            raise err

    outputFiles = {}
    failed = []
    skipped = []

    for entry in directory:
        if entry.is_file():
            try:
                files = None
                if entry.name.endswith('.001'):  # TODO: expand this to cover more file types
                    files = [readFile(entry.path)]
                elif entry.name.endswith('.prj'):
                    files = readAthenaProject(entry.path, abscorr=abscorr)
                else:
                    skipped.append(entry.path)

                for file in files:
                    if not hasattr(file, 'norm_corr'):
                        thisMeta = None

                        for metaName, meta in metadata.items():
                            if entry.name.startswith(metaName):
                                thisMeta = meta
                                break

                        if thisMeta is not None:
                            formula = thisMeta['formula']
                            lineSet = LineSet(file, formula)
                            outputFiles[lineSet.get_uuid()] = lineSet
                        else:
                            skipped.append(entry.path)
                    else:
                        lineSet = LineSet(file)
                        outputFiles[lineSet.get_uuid()] = lineSet
            except Exception as err:
                failed.append(entry.name)
        else:
            skipped.append(entry.path)

    directory.close()
    return outputFiles, failed, skipped
