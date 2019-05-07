import math

import numpy as np
import matplotlib.pyplot as plt
from larch import Interpreter

import constants
import calculations
import transformations
from larchio import readStructDirectory
from legend import interactive_legend

larchInstance = Interpreter()

baseUri = input('Enter the directory Location: ').replace('\\', '/')
outputNameRaw = input('Enter output project name(optional, enter for none): ')
metaName = (input('Enter metadata file name(default: \'meta.csv\'): ') or 'meta.csv')
# defaultFormulaRaw = input('Enter a default formula(default: skips files without formula): ').strip()
willGraph = input('Do you want to graph these?(y/n default: n) ').lower().startswith('y')

outputName = ''
# defaultMeta = None

if not baseUri.endswith('/'):
    baseUri += '/'

if outputNameRaw is not '' and not outputNameRaw.endswith('.prj'):
    outputName = outputNameRaw + '.prj'

# if defaultFormulaRaw is not '':
#    defaultMeta = {'formula': defaultFormulaRaw}

lines = {}
lineSearchSet = {}

try:
    lines, failedToRead, skippedFiles = readStructDirectory(baseUri)

    print('Failed to read in {:d} files from the directory.'.format(len(failedToRead)))
    print('Skipped {:d} files due to incorrect names or not files or no metadata.'.format(len(skippedFiles)))

    for uuid, lineSet in lines.items():
        print('Pre-Processing {}'.format(lineSet.get_name()))
        print('UUID: {}'.format(uuid))

        print('Calculating mu for fe_ka...')
        transformations.fe_calculate_mu(lineSet)

        print('Calculating the Pre-Edge Subtraction/Normalization...')
        transformations.calculate_pre_edge(lineSet)

        print('Calculating the Over Absorption...')
        transformations.fe_calculate_abs_corr(lineSet)

        # print('Calculating the Baseline Subtraction...')
        # pre_edge_baseline(energy=file,norm=file.norm_corr, group=file, emin=7105, larch=larchInstance)

except IOError as err:
    print(err)

print('Read in', len(lines), 'files.')

mainFig, mainPlot = None, None

if willGraph:
    mainFig, mainPlot = plt.subplots()
    mainPlot.set(xlabel='Energy (eV)',
                 ylabel='normalized $ \mu(E) $',
                 title='normalized abscorr $ \mu(E) $'
                 )
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
               ncol=2, borderaxespad=0
               )
    mainFig.subplots_adjust(right=0.55)


for name in lines:
    lineSet = lines[name]

    if willGraph:
        print('Graphing ${0}...'.format(lineSet.get_name()))
        lineSet.set_plot(mainPlot)
        lineSet.plot_abs_corr()

print('\nCalculating relative positions and energies...\n')

print('file name'.ljust(25), '   ',
      'far pos index'.ljust(13), '   ',
      'far pos diff'.ljust(12), '   ',
      'far pos norm_corr'.ljust(20), '   ',
      'far pos energy'.ljust(15), '  ',
      'close index'.ljust(11), '   ',
      'close diff'.ljust(10), '   ',
      'shoulder Angle'.ljust(14)
      )

print(''.ljust(25), '   ',
      'far neg index'.ljust(13), '   ',
      'far neg diff'.ljust(12), '   ',
      'far neg norm_corr'.ljust(20), '   ',
      'far neg energy'.ljust(15), '  ',
      ''.ljust(11), '   ',
      ''.ljust(10), '   ',
      'far pos-neg diff'.ljust(14)
      )

print(''.ljust(25), '   ',
      str('peakBoundLow').ljust(13), '   ',
      str('peakBoundHi').ljust(12), '   ',
      str('peakEnergy').ljust(20), '   ',
      str('peakCenter').ljust(15)[:15], '  ',
      str('peakDiff').ljust(11)[:11], '   ',
      str('peakOffset').ljust(10)[:10], '   ',
      str('peakIndex').ljust(14), '   ',
      str('indexOffset').ljust(14), '   ',
      str('boundDiff').ljust(11), '   ',
      str('initialShoulder').ljust(15), '   '
      )

print('\n')

for name in lines:
    lineSet = lines[name]

    # Stuff
    calculations.edge(lineSet)
    calculations.main_peak(lineSet)

    data = lineSet.get_data()
    edgeData = lineSet.get_store(constants.EdgeData.storeName)
    mainPeakData = lineSet.get_store(constants.MainPeakData.storeName)

    if willGraph:
        lineSet.plot_edge()
        lineSet.plot_main_peak()

    print(lineSet.get_name().ljust(25)[:25], '   ',
          str(edgeData.farthestPositiveIndex).ljust(13), '   ',
          str(edgeData.farthestPositiveDiff).ljust(20)[:12], '   ',
          str(data.norm_corr[edgeData.farthestPositiveIndex]).ljust(20)[:20], '   ',
          str(data.energy[edgeData.farthestPositiveIndex]).ljust(20)[:15], '  ',
          str(edgeData.closestIndex).ljust(11), '   ',
          str(edgeData.closestDiff).ljust(20)[:10], '   ',
          str(edgeData.shoulderAngle).ljust(20)[:9].ljust(14), '   ',
          )

    print(''.ljust(25), '   ',
          str(edgeData.farthestNegativeIndex).ljust(13), '  ',
          str(edgeData.farthestNegativeDiff).ljust(20)[:12], '    ',
          str(data.norm_corr[edgeData.farthestNegativeIndex]).ljust(20)[:20], '   ',
          str(data.energy[edgeData.farthestNegativeIndex]).ljust(20)[:15], '  ',
          ''.ljust(11), '   ',
          ''.ljust(20)[:10], '   ',
          str(abs(edgeData.farthestPositiveDiff - edgeData.farthestNegativeDiff)).ljust(20)[:9].ljust(14)
          )

    print(''.ljust(25), '   ',
          str(mainPeakData.peakBound[0]).ljust(13)[:13], '   ',
          str(mainPeakData.peakBound[1]).ljust(12), '   ',
          str(data.energy[mainPeakData.initialPeakIndex]).ljust(20), '   ',
          str(mainPeakData.peakCenter).ljust(15)[:15], '  ',
          '{:f}'.format(mainPeakData.peakCenterDiff).ljust(11)[:11], '   ',
          str(mainPeakData.peakCenterOffset).ljust(10)[:10], '   ',
          str(mainPeakData.initialPeakIndex).ljust(14), '   ',
          str(abs(mainPeakData.initialPeakIndex - mainPeakData.peakCenterOffset)).ljust(14), '   ',
          str(abs(mainPeakData.smoothedPeak[mainPeakData.peakBound[0]] - mainPeakData.smoothedPeak[mainPeakData.peakBound[1]])).ljust(11)[:11], '   ',
          str('').ljust(15)[:15], '   '
          )

    print('')

if willGraph:
    print('Displaying graph...')
    plt.ioff()
    plt.grid()
    legend = interactive_legend(mainPlot)
#    for name in lines:
#        lineSet = lines[name]
#        elementSet = legend.labelReference['Linear ' + name]
#        elementSet.clickable[1].set_text('Edge Data')
#        elementSet.add_toggleable(lineSet['points'])
#        elementSet.add_toggleable(lineSet['linear'])

    legend.show()
    print('Graph closed.')

"""
    if outputName is not '':
        try:
            os.remove(baseUri + outputName + '_abs_corr_' + version + '.prj')
        except Exception:
            pass

        outputProject = create_athena(baseUri + outputName + '_abs_corr_' + version + '.prj')

    for data in outputData:
        if data.norm_corr is not None:
            data.mufluor = data.norm_corr
            delattr(data, 'mu')

            if outputName is '':
                print('writing out data')
                try:
                    os.remove(baseUri + data.filename + '.prj')
                except Exception:
                    pass

                outputProject = create_athena(baseUri + data.filename + '.prj')
                outputProject.add_group(data)
                outputProject.save()
            else:
                outputProject.add_group(data)

        else:
            print(data.filename, 'has no norm_corr to write out')

    if outputName is not '':
        print('writing out data')
        outputProject.save()

else:
    print('Unable to read in any data')
"""
print('\n\nOutput Finished.')

# plot_prepeaks_baseline(dgroup=file)


"""
newplot(file.energy, file.norm, label='normalized $ \mu(E) $',
        xlabel='Energy (eV)',
        ylabel='normalized $ \mu(E) $',
        title='post-normalization ',
        show_legend=True)

newplot(file.energy, file.mu, label=' $ \mu(E) $ ',
        xlabel='Energy (eV)',
        ylabel='fe_ka/i0',
        title='pre-normalization ',
        show_legend=True)

plot(file.energy, file.pre_edge, label='pre-edge line',
     color='black', style='dashed' )

plot(file.energy, file.post_edge, label='normalization line',
     color='black', style='dotted' )
"""
