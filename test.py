import os
import math
from multiprocessing import Process

import numpy as np
import matplotlib.pyplot as plt
from larch import Interpreter, Group
from larch_plugins.xafs import pre_edge, pre_edge_baseline, fluo_corr
from larch_plugins.io import read_ascii

from legend import interactive_legend

larchInstance = Interpreter()
version = '1.0.0'
edgeStartEnergy = 7118.5
edgeEndEnergy = 7123.5

baseUri = input('Enter the directory Location: ').replace('\\', '/')
outputNameRaw = input('Enter output project name(optional, enter for none): ')
metaName = (input('Enter metadata file name(default: \'meta.csv\'): ') or 'meta.csv')
defaultFormulaRaw = input('Enter a default formula(default: skips files without formula): ')
willGraph = input('Do you want to graph these?(y/n default: n) ').lower().startswith('y')

if not baseUri.endswith('/'):
	baseUri += '/'

outputName = ''
if outputNameRaw is not '' and not outputNameRaw.endswith('.prj'):
	outputName = outputNameRaw + '.prj'

defaultMeta = None
if defaultFormulaRaw is not '':
	defaultMeta = {'formula': defaultFormulaRaw.strip()}

# defaultMeta = {'formula': 'Si1.849Ti0.044Al0.256Cr0Fe0.334Mn0.008Mg0.588Ca0.835Na0.128O6'}
# baseUri = 'C:/Users/EPMA_Castaing/work/avishek/testdata/test/'
# outputName = 'output.prj'

# 7118.5
# 7125.0

sampleNameHeader = 'sample number'
sampleFormulaHeader = 'formula'
directory = None
meta = {}
outputData = []

try:
	directory = os.scandir(baseUri)
except IOError:
	print('\nDirectory not accessible.\n')
else:
	metaLines = []

	try:
		fh = open(baseUri + metaName, 'r')
	except IOError:
		print('No meta file found\n')
	else:
		metaLines = fh.readlines()
		fh.close()
		print('Meta file read in')

	metaColumnNames = []
	for line in metaLines:
		info = line.strip('\n').split(',')

		if len(metaColumnNames) == 0:
			for name in info:
				metaColumnNames.append(name.strip().lower())

		else:
			if len(info) >= len(metaColumnNames):
				meta[info[metaColumnNames.index(sampleNameHeader)].strip()] = {
					'formula': info[metaColumnNames
						.index(sampleFormulaHeader)]
						.strip().replace('\t', '').replace('"', '').replace('\'', '')
				}

if directory is not None:
	for entry in directory:
		if entry.is_file():
			if entry.name.endswith('.001'):
				print('Reading in', entry.name, '...')
				try:
					file = read_ascii(entry.path,
									  labels='energy 0 i0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 Fe_Ka1 Fe_Ka2 Fe_Ka3 Fe_Ka4')
				except Exception as err:
					print('not able to read', entry.name)
					print(err)
				else:
					print('Getting metadata...')
					thisMeta = None

					for metaName, metadata in meta.items():
						if entry.name.startswith(metaName):
							thisMeta = metadata
							pass

					if thisMeta is None:
						print('No metadata found.')
						if defaultMeta is not None:
							print('Using default metadata')
							thisMeta = defaultMeta

					if thisMeta is not None:
						formula = thisMeta['formula']
						print('Got metadata.')

						print('Calculating mu for fe_ka...')
						file.mu = (file.fe_ka1 + file.fe_ka2 + file.fe_ka3 + file.fe_ka4) / file.i0

						print('Calculating the Pre-Edge Subtraction/Normalization...')
						pre_edge(file, group=file, pre1=-67.40, pre2=-30.00, norm1=77.96, norm2=250.60,
								 _larch=larchInstance)

						print('Calculating the Over Absorption...')
						fluo_corr(energy=file.energy, mu=file.mu, group=file, elem='Fe', formula=formula,
								  _larch=larchInstance)

						# print('Calculating the Baseline Subtraction...')
						# pre_edge_baseline(energy=file,norm=file.norm_corr, group=file, emin=7105, _larch=larchInstance)

						outputData.append(file)

	directory.close()

print('Read in', len(outputData), 'files.')

mainFig, mainPlot = None, None
lines = {}

if willGraph:
	mainFig, mainPlot = plt.subplots()

if len(outputData) > 0:
	try:
		if willGraph:
			graphMade = False
			for data in outputData:
				print('Preparing', data.filename, '...')
				data.filename = data.filename + '_abs_corr_' + version

				if not graphMade:
					mainPlot.set(xlabel='Energy (eV)',
								 ylabel='normalized $ \mu(E) $',
								 title='normalized abscorr $ \mu(E) $'
								 )
					graphMade = True

				print('Graphing', data.filename, '...')
				line = mainPlot.plot(data.energy, data.norm_corr, label=data.filename, marker=None)[0]
				lines[data.filename] = {'name': data.filename, 'line': line, 'points': [], 'linear': None}

				print('Graphed', data.filename)
	except Exception as err:
		print(err)
		willGraph = False
		print('Graphing failed for unknown reason')

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

	print('\n')

	for data in outputData:
		if data.norm_corr is not None:
			startIndexDiff = 0
			endIndexDiff = 0
			startIndex = 0
			endIndex = 0

			for j in range(0, len(data.energy)):
				startEnergyD = abs(data.energy[j] - edgeStartEnergy)
				if startEnergyD < abs(data.energy[startIndex] - edgeStartEnergy):
					startIndexDiff = abs(data.energy[startIndex] - edgeStartEnergy)
					startIndex = j

				endEnergyD = abs(data.energy[j] - edgeEndEnergy)
				if endEnergyD < abs(data.energy[endIndex] - edgeEndEnergy):
					endIndexDiff = abs(data.energy[startIndex] - edgeEndEnergy)
					endIndex = j

			startValue = data.norm_corr[startIndex]
			endValue = data.norm_corr[endIndex]

			linearLine = []
			lastValue = startValue
			for j in range(0, endIndex - startIndex):
				linearLine.append(lastValue)
				lastValue += (endValue - startValue) / (endIndex - startIndex)

			linearLine.append(endValue)

			farthestPositiveIndex = 0
			farthestPositiveDiff = 0
			for j in range(0, len(linearLine)):
				diff = data.norm_corr[startIndex + j] - linearLine[j]

				if diff > 0 and diff > farthestPositiveDiff:
					farthestPositiveDiff = diff
					farthestPositiveIndex = j

			closestIndex = 0
			closestDiff = 9999
			for j in range(farthestPositiveIndex, len(linearLine)):
				diff = data.norm_corr[startIndex + j] - linearLine[j]

				if diff < closestDiff:
					closestDiff = diff
					closestIndex = j
				else:
					pass

			farthestNegativeIndex = 0
			farthestNegativeDiff = 0
			for j in range(closestIndex, len(linearLine)):
				diff = data.norm_corr[startIndex + j] - linearLine[j]

				if diff < 0 and diff < farthestNegativeDiff:
					farthestNegativeDiff = diff
					farthestNegativeIndex = j

			avgTangentSlope = ((data.norm_corr[farthestPositiveIndex - 1] - data.norm_corr[farthestPositiveIndex]) + (
					data.norm_corr[farthestPositiveIndex] - data.norm_corr[farthestPositiveIndex + 1])) / 2
			shoulderAngle = 180 - abs(math.degrees(math.atan(avgTangentSlope)) - math.degrees(math.atan(0)))

			print(data.filename.ljust(25)[:25], '   ',
				  str(farthestPositiveIndex).ljust(13), '   ',
				  str(farthestPositiveDiff).ljust(20)[:12], '   ',
				  str(data.norm_corr[farthestPositiveIndex + startIndex]).ljust(20)[:20], '   ',
				  str(data.energy[farthestPositiveIndex + startIndex]).ljust(20)[:15], '  ',
				  str(closestIndex).ljust(11), '   ',
				  str(closestDiff).ljust(20)[:10], '   ',
				  str(shoulderAngle).ljust(20)[:9].ljust(14)
				  )

			print(''.ljust(25), '   ',
				  str(farthestNegativeIndex).ljust(13), '  ',
				  str(farthestNegativeDiff).ljust(20)[:12], '    ',
				  str(data.norm_corr[farthestNegativeIndex + startIndex]).ljust(20)[:20], '   ',
				  str(data.energy[farthestNegativeIndex + startIndex]).ljust(20)[:15], '  ',
				  ''.ljust(11), '   ',
				  ''.ljust(20)[:10], '   ',
				  str(abs(farthestPositiveDiff - farthestNegativeDiff)).ljust(20)[:9].ljust(14)
				  )

			print('')

			if willGraph:
				lineSet = lines[data.filename]
				lineSet['points'].extend(mainPlot.plot(data.energy[farthestPositiveIndex + startIndex],
													   data.norm_corr[farthestPositiveIndex + startIndex],
													   marker='o',
													   markersize=5
													   )
										 )
				lineSet['points'].extend(mainPlot.plot(data.energy[farthestNegativeIndex + startIndex],
													   data.norm_corr[farthestNegativeIndex + startIndex],
													   marker='x',
													   markersize=5
													   )
										 )
				lineSet['linear'] = mainPlot.plot(data.energy[startIndex:endIndex + 1],
												  linearLine,
												  linestyle='--',
												  label='Linear ' + data.filename
												  )
		else:
			print(data.filename, ' has no norm_corr. Potential errors occurred\n')

	outputProject = None

if willGraph:
	print('Displaying graph...')
	plt.ioff()
	plt.grid()
	plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
			   ncol=2, borderaxespad=0)
	mainFig.subplots_adjust(right=0.55)
	legend = interactive_legend(mainPlot)
	for name in lines:
		lineSet = lines[name]
		elementSet = legend.labelReference['Linear ' + name]
		elementSet.clickable[1].set_text('Edge Data')
		elementSet.toggleable.extend(lineSet['points'])
		elementSet.toggleable.extend(lineSet['linear'])

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
