### Author: Zach Vernon
### RUN IN PYTHON 2; STILL HAS ISSUES IN 3
from __future__ import print_function
import csv
import math
import sqlite3
import os
import shutil

####### VARIABLES TO EDIT #######
# Edit to control the ACS year.
year = '2013_2017'

# Edit to control the ACS sequence numbers  (THESE CAN CHANGE EVERY YEAR)
acsAge = '002'  # B01001
acsMedAge = '003'  # B01002
acsRace = '005'  # B03002
acsMode = '028'  # B08203 / B08301 / B08136
acsPopHH = '034'  # B09019
acsHHType = '036'  # B11003
acsFamSize = '037'  # B11016
acsEdu = '043'  # B15002
acsLang = '045'  # C16001  (yes, C instead of B)
acsEng = '046'  # B16005
acsPov = '048'  # B17001
acsPovFam = '051'  # B17010
acsDis = '058'  # B18135
acsInc = '059'  # B19001 / B19013
acsPA = '063'  # B19056 / B19083
acsFamMedInc = '064'  # B19119
acsLbrFrc = '076'  # B23001
acsOccVac = '103'  # B25002 / B25004 / B25009
acsHUType = '104'  # B25017 / B25018 / B25024 / B25032
acsHAgeBRVehAv = '105'  # B25034 / B25037 / B25041 / B25046
acsRntCst = '106'  # B25070 / B25075 / B25077
acsHValOwnCst = '107'  # B25091
acsIncTenure = '109'  # B25106 / B25118
acsHIns = '124'  # B27001
acsVacImp = '133'  # B99253

# CCA processing flag
cca_proc_flag = True
###############################


### DEFINE HELPER FUNCTIONS ###
def csvSqlPrep(inpCsv, sqlName):
    ''' Create an SQL table and populate with values from a CSV. '''
    outList = []
    outIns = []
    try:
        for col in inpCsv.next():
            outList.append(col)
            #outListComb.append(col)  #### Uncomment and add print statement below final csv to generate output csv headers
    except AttributeError:
        for col in next(inpCsv):
            outList.append(col)
            #outListComb.append(col)  #### Uncomment and add print statement below final csv to generate output csv headers
    outIns = str('?,' * len(outList)).strip(',')
    outList = str(outList).replace("'", '').replace('[', '').replace(']', '').replace('"', '')
    cursor.execute('DROP TABLE IF EXISTS {}'.format(sqlName))
    cursor.execute('CREATE TABLE {} ({})'.format(sqlName, outList))
    cursor.executemany('INSERT INTO {} VALUES ({})'.format(sqlName, outIns), inpCsv)
    return None


def listBuild(maxIndex):
    ''' Return a list of 0s whose last index position is maxIndex, i.e. if
        maxIndex = 2, return [0.0, 0.0, 0.0] '''
    return [0.0] * (maxIndex + 1)


# Function to generate frequency sums
def listSum(L, maxIndex=None):
    ''' For all items in list L, sum all values up to and including the item
        with index position maxIndex. '''
    sum = 0.0
    if maxIndex is None:
        maxIndex = len(L) - 1
    for x in L[:maxIndex + 1]:
        try:
            sum += float(x)
        except ValueError:
            pass  # Value is non-numeric
    return sum


def medianCalc(binBreaks, binFreqs):
    ''' Use a grouped frequency distribution to estimate the median value from binned frequencies. '''
    # Verifies that number of bins = number of frequencies + 1
    if len(binBreaks) != len(binFreqs) + 1:
        raise Exception((
            'Number of bin breaks should be 1 greater than number of frequency bins! '
            'Verify that breaks list includes lower and upper bounds, '
            'and that frequency list only includes numbers (not geog name).'
        ))

    # Generates list of cumulative frequencies needed to identify median bin
    maxIndex = len(binFreqs) - 1
    cumFreqs = []
    for i in range(0, maxIndex + 1):
        cumFreqs.append(listSum(binFreqs, i))

    # Calculates frequency midpoint
    freqMid = cumFreqs[-1] / 2

    # Identifies bin that contains frequency midpoint, calculates variables needed to estimate median
    for cumFreq in cumFreqs:
        if cumFreq > freqMid:
            medBin = cumFreqs.index(cumFreq)
            medLowerBound = binBreaks[medBin]
            medUpperBound = binBreaks[medBin + 1]
            binWidth = medUpperBound - medLowerBound
            freqBelow = cumFreqs[medBin - 1]
            binFreq = binFreqs[medBin]
            break

    # Estimates/prints median
    median = medLowerBound + ((freqMid - freqBelow) / binFreq * binWidth)
    return median


def varSum(allVals, allVars, sumVars):
    ''' Return a float of the sum of specified values in a list, referenced by
        the index position of their variable names in another list. '''
    sum = 0.0
    for sumVar in sumVars:
        sum += float(allVals[allVars.index(sumVar)])
    return sum

def varSum2(allVals, allVars, sumVars):
    ''' Return a float of the sum of specified values in a list, referenced by
        the index position of their variable names in another list. '''
    sum = 0.0
    for sumVar in sumVars:
        try: 
            sum += float(allVals[allVars.index(sumVar)])
        except:
            pass
    return sum


###### BEGIN PROCESSING ######
geog_pairs = [('county', 'CNTY'), ('township', 'TOWN'), ('muni', 'MUNI'), ('tract', 'TR'), ('blockgroup', 'BLGP')]

for geog, geogAbbr in geog_pairs:
    # Age
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsAge), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsAge_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('NAME', 'GEOID', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85'))
            for row in csvInp:
                l1 = listBuild(9)
                l1[0] = str(row[csvFields.index('geogname')]).replace(', Illinois', '').strip().replace(' village', '').replace(' town', '').replace(' city', '')
                l1[1] = row[csvFields.index('geogkey')]
                l1[2] = varSum(row, csvFields, ['B01001e1'])
                l1[3] = varSum(row, csvFields, ['B01001e3', 'B01001e4', 'B01001e5', 'B01001e6', 'B01001e7', 'B01001e27', 'B01001e28', 'B01001e29', 'B01001e30', 'B01001e31'])  # 0 to 19
                l1[4] = varSum(row, csvFields, ['B01001e8', 'B01001e9', 'B01001e10', 'B01001e11', 'B01001e12', 'B01001e32', 'B01001e33', 'B01001e34', 'B01001e35', 'B01001e36'])  # 20 to 34
                l1[5] = varSum(row, csvFields, ['B01001e13', 'B01001e14', 'B01001e15', 'B01001e37', 'B01001e38', 'B01001e39'])  # 35 to 49
                l1[6] = varSum(row, csvFields, ['B01001e16', 'B01001e17', 'B01001e18', 'B01001e19', 'B01001e40', 'B01001e41', 'B01001e42', 'B01001e43'])  # 50 to 64
                l1[7] = varSum(row, csvFields, ['B01001e20', 'B01001e21', 'B01001e22', 'B01001e44', 'B01001e45', 'B01001e46'])  # 65 to 74
                l1[8] = varSum(row, csvFields, ['B01001e23', 'B01001e24', 'B01001e47', 'B01001e48'])  # 75 to 84
                l1[9] = varSum(row, csvFields, ['B01001e25', 'B01001e49'])  # Over 85
                csvOut.writerow(l1)

    # Med Age
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsMedAge), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsMedAge_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'MED_AGE'))
            for row in csvInp:
                l1 = listBuild(1)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B01002e1')] in ('', '.'):
                    l1[1] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B01002e1'])
                csvOut.writerow(l1)

    # Race
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsRace), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsRace_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER'))
            for row in csvInp:
                l1 = listBuild(5)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B03002e3'])
                l1[2] = varSum(row, csvFields, ['B03002e12'])
                l1[3] = varSum(row, csvFields, ['B03002e4'])
                l1[4] = varSum(row, csvFields, ['B03002e6'])
                l1[5] = varSum(row, csvFields, ['B03002e5', 'B03002e7', 'B03002e8', 'B03002e9'])
                csvOut.writerow(l1)


    # Modeshare
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsMode), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsMode_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'DROVE_AL_MEAN_TT', 'CARPOOL_MEAN_TT', 'TRANSIT_MEAN_TT', 'OTHER_INCL_WALK_BIKE_MEAN_TT', 'ALLMODES_MEAN_TT', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH'))
            for row in csvInp:
                l1 = listBuild(17)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = row[csvFields.index('B08301e21')]
                l1[2] = varSum(row, csvFields, ['B08301e2', 'B08301e10', 'B08301e16', 'B08301e17', 'B08301e18', 'B08301e19', 'B08301e20'])
                l1[3] = varSum(row, csvFields, ['B08301e3'])
                l1[4] = varSum(row, csvFields, ['B08301e4'])
                l1[5] = varSum(row, csvFields, ['B08301e10'])
                l1[6] = varSum(row, csvFields, ['B08301e18', 'B08301e19'])
                l1[7] = varSum(row, csvFields, ['B08301e16', 'B08301e17', 'B08301e20'])
                try:
                    l1[8] = varSum(row, csvFields, ['B08136e3']) / l1[3]
                except ValueError:
                    l1[8] = None
                try:
                    l1[9] = varSum(row, csvFields, ['B08136e4']) / l1[4]
                except ValueError:
                    l1[9] = None
                try:
                    l1[10] = varSum(row, csvFields, ['B08136e7']) / l1[5]
                except ValueError:
                    l1[10] = None
                try:
                    l1[11] = varSum(row, csvFields, ['B08136e11', 'B08136e12']) / (l1[6] + l1[7])
                except ValueError:
                    l1[11] = None
                try:
                    l1[12] = varSum(row, csvFields, ['B08136e1']) / l1[2]
                except ValueError:
                    l1[12] = None
                try:
                    l1[13] = varSum(row, csvFields, ['B08136e1'])
                except ValueError:
                    l1[13] = None
                try:
                    l1[14] = varSum(row, csvFields, ['B08201e2'])
                except ValueError:
                    l1[14] = None
                try:
                    l1[15] = varSum(row, csvFields, ['B08201e3'])
                except ValueError:
                    l1[15] = None
                try:
                    l1[16] = varSum(row, csvFields, ['B08201e4'])
                except ValueError:
                    l1[16] = None
                try:
                    l1[17] = varSum(row, csvFields, ['B08201e5',  'B08201e6'])
                except ValueError:
                    l1[17] = None

                csvOut.writerow(l1)


    # Pop HH
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsPopHH), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsPopHH_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_HH'))
            for row in csvInp:
                l1 = listBuild(1)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B09019e2'])
                csvOut.writerow(l1)


    # HH Type
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHHType), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsHHType_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'CT_SP_WCHILD'))
            for row in csvInp:
                l1 = listBuild(1)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B11003e10', 'B11003e16'])
                csvOut.writerow(l1)

    # Family Size
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsFamSize), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsFamSize_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_2PF', 'CT_3PF', 'CT_4PF', 'CT_5PF', 'CT_6PF', 'CT_7MPF', 'CT_NONFAM_HH', 'CT_2PNF', 'CT_3PNF', 'CT_4PNF', 'CT_5PNF', 'CT_6PNF', 'CT_7MPNF'))
            for row in csvInp:
                l1 = listBuild(18)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B11016e10'])
                l1[2] = varSum(row, csvFields, ['B11016e3', 'B11016e11'])
                l1[3] = varSum(row, csvFields, ['B11016e4', 'B11016e12'])
                l1[4] = varSum(row, csvFields, ['B11016e5', 'B11016e6', 'B11016e7', 'B11016e8', 'B11016e13', 'B11016e14', 'B11016e15', 'B11016e16'])
                l1[5] = varSum(row, csvFields, ['B11016e2'])
                l1[6] = varSum(row, csvFields, ['B11016e3'])
                l1[7] = varSum(row, csvFields, ['B11016e4'])
                l1[8] = varSum(row, csvFields, ['B11016e5'])
                l1[9] = varSum(row, csvFields, ['B11016e6'])
                l1[10] = varSum(row, csvFields, ['B11016e7'])
                l1[11] = varSum(row, csvFields, ['B11016e8'])
                l1[12] = varSum(row, csvFields, ['B11016e9'])
                l1[13] = varSum(row, csvFields, ['B11016e11'])
                l1[14] = varSum(row, csvFields, ['B11016e12'])
                l1[15] = varSum(row, csvFields, ['B11016e13'])
                l1[16] = varSum(row, csvFields, ['B11016e14'])
                l1[17] = varSum(row, csvFields, ['B11016e15'])
                l1[18] = varSum(row, csvFields, ['B11016e16'])
                csvOut.writerow(l1)


    # Educational attainment
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsEdu), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsEdu_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF'))
            for row in csvInp:
                l1 = listBuild(7)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B15003e1'])  # Over 25
                l1[2] = varSum(row, csvFields, ['B15003e2', 'B15003e3', 'B15003e4', 'B15003e5', 'B15003e6', 'B15003e7', 'B15003e8', 'B15003e9', 'B15003e10', 'B15003e11', 'B15003e12', 'B15003e13', 'B15003e14', 'B15003e15', 'B15003e16'])  # LT HS
                l1[3] = varSum(row, csvFields, ['B15003e17', 'B15003e18'])  # HS
                l1[4] = varSum(row, csvFields, ['B15003e19', 'B15003e20'])  # Some College
                l1[5] = varSum(row, csvFields, ['B15003e21'])  # Associates
                l1[6] = varSum(row, csvFields, ['B15003e22'])  # Bach
                l1[7] = varSum(row, csvFields, ['B15003e23', 'B15003e24', 'B15003e25'])  # Grad
                csvOut.writerow(l1)

    # Lang at home
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsLang), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsLang_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC'))
            for row in csvInp:
                l1 = listBuild(10)
                l1[0] = row[csvFields.index('geogkey')]
                try:
                    l1[1] = varSum(row, csvFields, ['C16001e2'])  # English
                    l1[2] = varSum(row, csvFields, ['C16001e3'])  # Spanish
                    l1[3] = varSum(row, csvFields, ['C16001e12'])  # Russian/Polish/Other Slavic
                    l1[4] = varSum(row, csvFields, ['C16001e21'])  # Chinese
                    l1[5] = varSum(row, csvFields, ['C16001e27'])  # Tagalog
                    l1[6] = varSum(row, csvFields, ['C16001e33'])  # Arabic
                    l1[7] = varSum(row, csvFields, ['C16001e18'])  # Korean
                    l1[8] = varSum(row, csvFields, ['C16001e24', 'C16001e30'])  # Other Asian
                    l1[9] = varSum(row, csvFields, ['C16001e6', 'C16001e9', 'C16001e15'])  # Other Euro
                    l1[10] = varSum(row, csvFields, ['C16001e36'])  # Other Unspecified
                except ValueError:
                    l1[1] = None
                    l1[2] = None
                    l1[3] = None
                    l1[4] = None
                    l1[5] = None
                    l1[6] = None
                    l1[7] = None
                    l1[8] = None
                    l1[9] = None
                    l1[10] = None
                csvOut.writerow(l1)


    # Linguistic isolation
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsEng), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsEng_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_OV5', 'NATIVE', 'FOR_BORN', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO'))
            for row in csvInp:
                l1 = listBuild(6)
                l1[0] = row[csvFields.index('geogkey')]
                try:
                    l1[1] = varSum(row, csvFields, ['B16005e1'])
                    l1[2] = varSum(row, csvFields, ['B16005e2'])
                    l1[3] = varSum(row, csvFields, ['B16005e24'])
                    l1[4] = varSum(row, csvFields, ['B16005e3', 'B16005e25'])
                    l1[5] = varSum(row, csvFields, ['B16005e4', 'B16005e9', 'B16005e14', 'B16005e19', 'B16005e26', 'B16005e31', 'B16005e36', 'B16005e41'])
                    l1[6] = varSum(row, csvFields, ['B16005e6', 'B16005e7', 'B16005e8', 'B16005e11', 'B16005e12', 'B16005e13', 'B16005e16', 'B16005e17', 'B16005e18', 'B16005e21', 'B16005e22', 'B16005e23', 'B16005e28', 'B16005e29', 'B16005e30', 'B16005e33', 'B16005e34', 'B16005e35', 'B16005e38', 'B16005e39', 'B16005e40', 'B16005e43', 'B16005e44', 'B16005e45'])
                except ValueError:
                    l1[1] = None
                    l1[2] = None
                    l1[3] = None
                    l1[4] = None
                    l1[5] = None
                    l1[6] = None
                csvOut.writerow(l1)

    # Pop Poverty
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsPov), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsPov_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POV_SURV', 'POV_POP'))
            for row in csvInp:
                l1 = listBuild(2)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B17001e1')] in ('', '.'):
                    l1[1] = None
                    l1[2] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B17001e1'])
                    l1[2] = varSum(row, csvFields, ['B17001e2'])
                csvOut.writerow(l1)

    # Fam Poverty
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsPovFam), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsPovFam_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'TOT_FAMILIES', 'POV_FAM'))
            for row in csvInp:
                l1 = listBuild(2)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B17010e1')] in ('', '.'):
                    l1[1] = None
                    l1[2] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B17010e1'])
                    l1[2] = varSum(row, csvFields, ['B17010e2'])
                csvOut.writerow(l1)

    # Disabled Pop
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsDis), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsDis_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_CIV_NONINST', 'DISABLED'))
            for row in csvInp:
                l1 = listBuild(2)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B18135e1')] in ('', '.'):
                    l1[1] = None
                    l1[2] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B18135e1'])
                    l1[2] = varSum(row, csvFields, ['B18135e3', 'B18135e14', 'B18135e25'])
                csvOut.writerow(l1)

    # Income
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsInc), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsInc_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'MEDINC', 'INC_LT_45K', 'MEDINC_1PHH'))
            for row in csvInp:
                l1 = listBuild(9)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B19001e2', 'B19001e3', 'B19001e4', 'B19001e5'])
                l1[2] = varSum(row, csvFields, ['B19001e6', 'B19001e7', 'B19001e8', 'B19001e9', 'B19001e10'])
                l1[3] = varSum(row, csvFields, ['B19001e11', 'B19001e12'])
                if row[csvFields.index('B19001e13')] in ('', '.'):
                    l1[4] = None
                else:
                    l1[4] = varSum(row, csvFields, ['B19001e13'])
                l1[5] = varSum(row, csvFields, ['B19001e14', 'B19001e15'])
                l1[6] = varSum(row, csvFields, ['B19001e16', 'B19001e17'])
                if row[csvFields.index('B19013e1')] in ('', '.'):
                    l1[7] = None
                else:
                    l1[7] = varSum(row, csvFields, ['B19013e1'])
                l1[8] = varSum(row, csvFields, ['B19001e2', 'B19001e3', 'B19001e4', 'B19001e5', 'B19001e6', 'B19001e7', 'B19001e8', 'B19001e9'])
                if row[csvFields.index('B19019e2')] in ('', '.'):
                    l1[9] = None
                else:
                    l1[9] = varSum(row, csvFields, ['B19019e2'])
                csvOut.writerow(l1)

    # Public Assistance or "Food Stamps"
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsPA), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            try:
                csvFields = csvInp.next()
            except AttributeError:
                csvFields = next(csvInp)
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsPA_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'HH_PUB_ASSIST_OR_FOOD_STAMPS', 'GINI_INDEX', 'FAM_INC_UND45K'))
            for row in csvInp:
                l1 = listBuild(3)
                l1[0] = row[csvFields.index('geogkey')]
                try:
                    l1[1] = varSum(row, csvFields, ['B19058e2'])
                except ValueError:
                    l1[1] = None
                try:
                    l1[2] = varSum(row, csvFields, ['B19083e1'])
                except ValueError:
                    l1[2] = None
                l1[3] = varSum(row, csvFields, ['B19101e2', 'B19101e3', 'B19101e4', 'B19101e5', 'B19101e6', 'B19101e7', 'B19101e8', 'B19101e9'])
                csvOut.writerow(l1)

    ######## Begin Vulnerable Population Scenario Pull ########

    # Family Median Income
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsFamMedInc), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsFamMedInc_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'MEDINC_ALL_FAM', 'MEDINC_2PF', 'MEDINC_3PF', 'MEDINC_4PF', 'MEDINC_5PF', 'MEDINC_6PF', 'MEDINC_7MPF'))
            for row in csvInp:
                l1 = listBuild(7)
                l1[0] = row[csvFields.index('geogkey')]
                try:
                    l1[1] = varSum(row, csvFields, ['B19119e1'])
                except ValueError:
                    l1[1] = None
                try:
                    l1[2] = varSum(row, csvFields, ['B19119e2'])
                except ValueError:
                    l1[2] = None
                try:
                    l1[3] = varSum(row, csvFields, ['B19119e3'])
                except ValueError:
                    l1[3] = None
                try:
                    l1[4] = varSum(row, csvFields, ['B19119e4'])
                except ValueError:
                    l1[4] = None
                try:
                    l1[5] = varSum(row, csvFields, ['B19119e5'])
                except ValueError:
                    l1[5] = None
                try:
                    l1[6] = varSum(row, csvFields, ['B19119e6'])
                except ValueError:
                    l1[6] = None
                try:
                    l1[7] = varSum(row, csvFields, ['B19119e7'])
                except ValueError:
                    l1[7] = None
                csvOut.writerow(l1)

    ######## End Vulnerable Population Scenario Pull ########

    # Labor Force
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsLbrFrc), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsLbrFrc_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC'))
            for row in csvInp:
                l1 = listBuild(5)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B23001e1')] in ('', '.'):
                    l1[1] = None
                    l1[2] = None
                    l1[3] = None
                    l1[4] = None
                    l1[5] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B23001e1'])
                    l1[2] = varSum(row, csvFields, ['B23001e4', 'B23001e11', 'B23001e18', 'B23001e25', 'B23001e32', 'B23001e39', 'B23001e46', 'B23001e53', 'B23001e60', 'B23001e67', 'B23001e74', 'B23001e79', 'B23001e84', 'B23001e90', 'B23001e97', 'B23001e104', 'B23001e111', 'B23001e118', 'B23001e125', 'B23001e132', 'B23001e139', 'B23001e146', 'B23001e153', 'B23001e160', 'B23001e165', 'B23001e170'])
                    l1[3] = varSum(row, csvFields, ['B23001e7', 'B23001e14', 'B23001e21', 'B23001e28', 'B23001e35', 'B23001e42', 'B23001e49', 'B23001e56', 'B23001e63', 'B23001e70', 'B23001e75', 'B23001e80', 'B23001e85', 'B23001e93', 'B23001e100', 'B23001e107', 'B23001e114', 'B23001e121', 'B23001e128', 'B23001e135', 'B23001e142', 'B23001e149', 'B23001e156', 'B23001e161', 'B23001e166', 'B23001e171'])
                    l1[4] = varSum(row, csvFields, ['B23001e8', 'B23001e15', 'B23001e22', 'B23001e29', 'B23001e36', 'B23001e43', 'B23001e50', 'B23001e57', 'B23001e64', 'B23001e71', 'B23001e76', 'B23001e81', 'B23001e86', 'B23001e94', 'B23001e101', 'B23001e108', 'B23001e115', 'B23001e122', 'B23001e129', 'B23001e136', 'B23001e143', 'B23001e150', 'B23001e157', 'B23001e162', 'B23001e167', 'B23001e172'])
                    l1[5] = varSum(row, csvFields, ['B23001e9', 'B23001e16', 'B23001e23', 'B23001e30', 'B23001e37', 'B23001e44', 'B23001e51', 'B23001e58', 'B23001e65', 'B23001e72', 'B23001e77', 'B23001e82', 'B23001e87', 'B23001e95', 'B23001e102', 'B23001e109', 'B23001e116', 'B23001e123', 'B23001e130', 'B23001e137', 'B23001e144', 'B23001e151', 'B23001e158', 'B23001e163', 'B23001e168', 'B23001e173'])
                csvOut.writerow(l1)

    # Occupied/Vacant HU
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsOccVac), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsOccVac_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'VAC_FOR_RENT', 'VAC_FOR_SALE', 'VAC_OTHER', 'OWN_1_PERS_HH', 'OWN_2_PERS_HH', 'OWN_3_PERS_HH', 'OWN_4_PERS_HH', 'OWN_5_PERS_HH', 'OWN_6_PERS_HH', 'OWN_7_MORE_HH', 'RENT_1_PERS_HH', 'RENT_2_PERS_HH', 'RENT_3_PERS_HH', 'RENT_4_PERS_HH', 'RENT_5_PERS_HH', 'RENT_6_PERS_HH', 'RENT_7_MORE_HH'))
            for row in csvInp:
                l1 = listBuild(21)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B25002e2'])
                l1[2] = varSum(row, csvFields, ['B25003e2'])
                l1[3] = varSum(row, csvFields, ['B25003e3'])
                l1[4] = varSum(row, csvFields, ['B25002e3'])
                l1[5] = varSum(row, csvFields, ['B25004e2', 'B25004e3'])
                l1[6] = varSum(row, csvFields, ['B25004e4', 'B25004e5'])
                l1[7] = varSum(row, csvFields, ['B25004e6', 'B25004e7', 'B25004e8'])
                l1[8] = varSum(row, csvFields, ['B25009e3'])
                l1[9] = varSum(row, csvFields, ['B25009e4'])
                l1[10] = varSum(row, csvFields, ['B25009e5'])
                l1[11] = varSum(row, csvFields, ['B25009e6'])
                l1[12] = varSum(row, csvFields, ['B25009e7'])
                l1[13] = varSum(row, csvFields, ['B25009e8'])
                l1[14] = varSum(row, csvFields, ['B25009e9'])
                l1[15] = varSum(row, csvFields, ['B25009e11'])
                l1[16] = varSum(row, csvFields, ['B25009e12'])
                l1[17] = varSum(row, csvFields, ['B25009e13'])
                l1[18] = varSum(row, csvFields, ['B25009e14'])
                l1[19] = varSum(row, csvFields, ['B25009e15'])
                l1[20] = varSum(row, csvFields, ['B25009e16'])
                l1[21] = varSum(row, csvFields, ['B25009e17'])
                csvOut.writerow(l1)

    # HU Type
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHUType), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsHUType_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'MED_ROOMS', 'HU_OWN_1DET', 'HU_OWN_1ATT', 'HU_OWN_2', 'HU_OWN_3_4', 'HU_OWN_5_9', 'HU_OWN_10_19', 'HU_OWN_20_49', 'HU_OWN_50OV', 'HU_OWN_MOB_HOME', 'HU_OWN_OTHER_MOB', 'HU_RENT_1DET', 'HU_RENT_1ATT', 'HU_RENT_2', 'HU_RENT_3_4', 'HU_RENT_5_9', 'HU_RENT_10_19', 'HU_RENT_20_49', 'HU_RENT_50OV', 'HU_RENT_MOB_HOME', 'HU_RENT_OTHER_MOB'))

            for row in csvInp:
                l1 = listBuild(27)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B25024e1'])
                l1[2] = varSum(row, csvFields, ['B25024e2'])
                l1[3] = varSum(row, csvFields, ['B25024e3'])
                l1[4] = varSum(row, csvFields, ['B25024e4'])
                l1[5] = varSum(row, csvFields, ['B25024e5'])
                l1[6] = varSum(row, csvFields, ['B25024e6', 'B25024e7', 'B25024e8','B25024e9'])
                if row[csvFields.index('B25018e1')] in ('', '.'):
                    l1[7] = None
                else:
                    l1[7] = varSum(row, csvFields, ['B25018e1'])
                l1[8] = varSum(row, csvFields, ['B25032e3'])
                l1[9] = varSum(row, csvFields, ['B25032e4'])
                l1[10] = varSum(row, csvFields, ['B25032e5'])
                l1[11] = varSum(row, csvFields, ['B25032e6'])
                l1[12] = varSum(row, csvFields, ['B25032e7'])
                l1[13] = varSum(row, csvFields, ['B25032e8'])
                l1[14] = varSum(row, csvFields, ['B25032e9'])
                l1[15] = varSum(row, csvFields, ['B25032e10'])
                l1[16] = varSum(row, csvFields, ['B25032e11'])
                l1[17] = varSum(row, csvFields, ['B25032e12'])
                l1[18] = varSum(row, csvFields, ['B25032e14'])
                l1[19] = varSum(row, csvFields, ['B25032e15'])
                l1[20] = varSum(row, csvFields, ['B25032e16'])
                l1[21] = varSum(row, csvFields, ['B25032e17'])
                l1[22] = varSum(row, csvFields, ['B25032e18'])
                l1[23] = varSum(row, csvFields, ['B25032e19'])
                l1[24] = varSum(row, csvFields, ['B25032e20'])
                l1[25] = varSum(row, csvFields, ['B25032e21'])
                l1[26] = varSum(row, csvFields, ['B25032e22'])
                l1[27] = varSum(row, csvFields, ['B25032e23'])
                csvOut.writerow(l1)

    # HU Age / Number of Bedrooms
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHAgeBRVehAv), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsHAgeBRVehAv_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'HA_AFT2000', 'HA_80_00', 'HA_70_00', 'HA_60_80', 'HA_40_70', 'HA_40_60', 'HA_BEF1940', 'MED_HA', 'MED_HA_OWN', 'MED_HA_RENT', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'AGG_VEH_AVAIL'))
            for row in csvInp:
                l1 = listBuild(16)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B25034e4', 'B25034e3', 'B25034e2'])  # 2000 or later
                l1[2] = varSum(row, csvFields, ['B25034e6', 'B25034e5'])  # 1980 to 2000
                l1[3] = varSum(row, csvFields, ['B25034e7', 'B25034e6', 'B25034e5'])  # 1970 to 2000
                l1[4] = varSum(row, csvFields, ['B25034e8', 'B25034e7'])  # 1960 to 1980
                l1[5] = varSum(row, csvFields, ['B25034e10', 'B25034e9', 'B25034e8'])  # 1940 to 1970
                l1[6] = varSum(row, csvFields, ['B25034e10', 'B25034e9'])  # 1940 to 1960
                l1[7] = varSum(row, csvFields, ['B25034e11'])  # before 1940
                if row[csvFields.index('B25035e1')] in ('', '.'):
                    l1[8] = None
                else:
                    l1[8] = varSum(row, csvFields, ['B25035e1'])
                if row[csvFields.index('B25037e2')] in ('', '.'):
                    l1[9] = None
                else:
                    l1[9] = varSum(row, csvFields, ['B25037e2'])
                if row[csvFields.index('B25037e3')] in ('', '.'):
                    l1[10] = None
                else:
                    l1[10] = varSum(row, csvFields, ['B25037e3'])
                l1[11] = varSum(row, csvFields, ['B25041e2', 'B25041e3'])
                l1[12] = varSum(row, csvFields, ['B25041e4'])
                l1[13] = varSum(row, csvFields, ['B25041e5'])
                l1[14] = varSum(row, csvFields, ['B25041e6'])
                l1[15] = varSum(row, csvFields, ['B25041e7'])
                if row[csvFields.index('B25046e1')] in ('', '.'):
                    l1[16] = None
                else:
                    l1[16] = varSum(row, csvFields, ['B25046e1'])
                csvOut.writerow(l1)

    # Rent/Owner Costs
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsRntCst), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsRntCst_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'RNTCST_OV30PCT', 'HV_LT_100K', 'HV_LT_150K', 'HV_100_250K', 'HV_150_300K', 'HV_250_400K', 'HV_300_500K', 'HV_400_750K', 'HV_GT_500K', 'HV_GT_750K', 'MED_HV'))
            for row in csvInp:
                l1 = listBuild(11)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B25070e7', 'B25070e8', 'B25070e9', 'B25070e10'])
                l1[2] = varSum(row, csvFields, ['B25075e2', 'B25075e3', 'B25075e4', 'B25075e5', 'B25075e6', 'B25075e7', 'B25075e8', 'B25075e9', 'B25075e10', 'B25075e11', 'B25075e12', 'B25075e13', 'B25075e14'])
                l1[3] = varSum(row, csvFields, ['B25075e2', 'B25075e3', 'B25075e4', 'B25075e5', 'B25075e6', 'B25075e7', 'B25075e8', 'B25075e9', 'B25075e10', 'B25075e11', 'B25075e12', 'B25075e13', 'B25075e14', 'B25075e15', 'B25075e16'])
                l1[4] = varSum(row, csvFields, ['B25075e15', 'B25075e16', 'B25075e17', 'B25075e18', 'B25075e19'])
                l1[5] = varSum(row, csvFields, ['B25075e17', 'B25075e18', 'B25075e19', 'B25075e20'])
                l1[6] = varSum(row, csvFields, ['B25075e20', 'B25075e21'])
                l1[7] = varSum(row, csvFields, ['B25075e21', 'B25075e22'])
                l1[8] = varSum(row, csvFields, ['B25075e22', 'B25075e23'])
                l1[9] = varSum(row, csvFields, ['B25075e23', 'B25075e24', 'B25075e25'])
                l1[10] = varSum(row, csvFields, ['B25075e24', 'B25075e25'])
                if row[csvFields.index('B25077e1')] in ('', '.'):
                    l1[11] = None
                else:
                    l1[11] = varSum(row, csvFields, ['B25077e1'])
                csvOut.writerow(l1)

    # Housing Value
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHValOwnCst), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsHValOwnCst_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'OWNCST_OV30PCT'))
            for row in csvInp:
                l1 = listBuild(1)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B25091e8', 'B25091e9', 'B25091e10', 'B25091e11', 'B25091e19', 'B25091e20', 'B25091e21', 'B25091e22'])
                csvOut.writerow(l1)

    # HU Inc Tenure
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsIncTenure), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsIncTenure_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'HU_OWN_INC_LT5K', 'HU_OWN_INC_5K_10K', 'HU_OWN_INC_10K_15K', 'HU_OWN_INC_15K_20K', 'HU_OWN_INC_20K_25K', 'HU_OWN_INC_25K_35K', 'HU_OWN_INC_35K_50K', 'HU_OWN_INC_50K_75K', 'HU_OWN_INC_75K_100K', 'HU_OWN_INC_100K_150K', 'HU_OWN_INC_150KOV', 'HU_RENT_INC_LT5K', 'HU_RENT_INC_5K_10K', 'HU_RENT_INC_10K_15K', 'HU_RENT_INC_15K_20K', 'HU_RENT_INC_20K_25K', 'HU_RENT_INC_25K_35K', 'HU_RENT_INC_35K_50K', 'HU_RENT_INC_50K_75K', 'HU_RENT_INC_75K_100K', 'HU_RENT_INC_100K_150K', 'HU_RENT_INC_150KOV', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT'))
            for row in csvInp:
                l1 = listBuild(38)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B25118e3')] in ('', '.'):
                    l1[1] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B25118e3'])
                if row[csvFields.index('B25118e4')] in ('', '.'):
                    l1[2] = None
                else:
                    l1[2] = varSum(row, csvFields, ['B25118e4'])
                if row[csvFields.index('B25118e5')] in ('', '.'):
                    l1[3] = None
                else:
                    l1[3] = varSum(row, csvFields, ['B25118e5'])
                if row[csvFields.index('B25118e6')] in ('', '.'):
                    l1[4] = None
                else:
                    l1[4] = varSum(row, csvFields, ['B25118e6'])
                if row[csvFields.index('B25118e7')] in ('', '.'):
                    l1[5] = None
                else:
                    l1[5] = varSum(row, csvFields, ['B25118e7'])
                if row[csvFields.index('B25118e8')] in ('', '.'):
                    l1[6] = None
                else:
                    l1[6] = varSum(row, csvFields, ['B25118e8'])
                if row[csvFields.index('B25118e9')] in ('', '.'):
                    l1[7] = None
                else:
                    l1[7] = varSum(row, csvFields, ['B25118e9'])
                if row[csvFields.index('B25118e10')] in ('', '.'):
                    l1[8] = None
                else:
                    l1[8] = varSum(row, csvFields, ['B25118e10'])
                if row[csvFields.index('B25118e11')] in ('', '.'):
                    l1[9] = None
                else:
                    l1[9] = varSum(row, csvFields, ['B25118e11'])
                if row[csvFields.index('B25118e12')] in ('', '.'):
                    l1[10] = None
                else:
                    l1[10] = varSum(row, csvFields, ['B25118e12'])
                if row[csvFields.index('B25118e13')] in ('', '.'):
                    l1[11] = None
                else:
                    l1[11] = varSum(row, csvFields, ['B25118e13'])
                if row[csvFields.index('B25118e15')] in ('', '.'):
                    l1[12] = None
                else:
                    l1[12] = varSum(row, csvFields, ['B25118e15'])
                if row[csvFields.index('B25118e16')] in ('', '.'):
                    l1[13] = None
                else:
                    l1[13] = varSum(row, csvFields, ['B25118e16'])
                if row[csvFields.index('B25118e17')] in ('', '.'):
                    l1[14] = None
                else:
                    l1[14] = varSum(row, csvFields, ['B25118e17'])
                if row[csvFields.index('B25118e18')] in ('', '.'):
                    l1[15] = None
                else:
                    l1[15] = varSum(row, csvFields, ['B25118e18'])
                if row[csvFields.index('B25118e19')] in ('', '.'):
                    l1[16] = None
                else:
                    l1[16] = varSum(row, csvFields, ['B25118e19'])
                if row[csvFields.index('B25118e20')] in ('', '.'):
                    l1[17] = None
                else:
                    l1[17] = varSum(row, csvFields, ['B25118e20'])
                if row[csvFields.index('B25118e21')] in ('', '.'):
                    l1[18] = None
                else:
                    l1[18] = varSum(row, csvFields, ['B25118e21'])
                if row[csvFields.index('B25118e22')] in ('', '.'):
                    l1[19] = None
                else:
                    l1[19] = varSum(row, csvFields, ['B25118e22'])
                if row[csvFields.index('B25118e23')] in ('', '.'):
                    l1[20] = None
                else:
                    l1[20] = varSum(row, csvFields, ['B25118e23'])
                if row[csvFields.index('B25118e24')] in ('', '.'):
                    l1[21] = None
                else:
                    l1[21] = varSum(row, csvFields, ['B25118e24'])
                if row[csvFields.index('B25118e25')] in ('', '.'):
                    l1[22] = None
                else:
                    l1[22] = varSum(row, csvFields, ['B25118e25'])

                try:
                    l1[23] = varSum(row, csvFields, ['B25106e3', 'B25106e25'])
                    l1[24] = varSum(row, csvFields, ['B25106e4', 'B25106e26'])
                    l1[25] = varSum(row, csvFields, ['B25106e5', 'B25106e27'])
                    l1[26] = varSum(row, csvFields, ['B25106e6', 'B25106e28'])

                    # 20K to 49K
                    l1[27] = varSum(row, csvFields, ['B25106e7', 'B25106e29', 'B25106e11', 'B25106e33'])
                    l1[28] = varSum(row, csvFields, ['B25106e8', 'B25106e30', 'B25106e12', 'B25106e34'])
                    l1[29] = varSum(row, csvFields, ['B25106e9', 'B25106e31', 'B25106e13', 'B25106e35'])
                    l1[30] = varSum(row, csvFields, ['B25106e10', 'B25106e32', 'B25106e14', 'B25106e36'])

                    l1[31] = varSum(row, csvFields, ['B25106e15', 'B25106e37'])
                    l1[32] = varSum(row, csvFields, ['B25106e16', 'B25106e38'])
                    l1[33] = varSum(row, csvFields, ['B25106e17', 'B25106e39'])
                    l1[34] = varSum(row, csvFields, ['B25106e18', 'B25106e40'])

                    l1[35] = varSum(row, csvFields, ['B25106e19', 'B25106e41'])
                    l1[36] = varSum(row, csvFields, ['B25106e20', 'B25106e42'])
                    l1[37] = varSum(row, csvFields, ['B25106e21', 'B25106e43'])
                    l1[38] = varSum(row, csvFields, ['B25106e22', 'B25106e44'])
                except ValueError:
                    l1[23] = None
                    l1[24] = None
                    l1[25] = None
                    l1[26] = None
                    l1[27] = None
                    l1[28] = None
                    l1[29] = None
                    l1[30] = None
                    l1[31] = None
                    l1[32] = None
                    l1[33] = None
                    l1[34] = None
                    l1[35] = None
                    l1[36] = None
                    l1[37] = None
                    l1[38] = None
                csvOut.writerow(l1)

    # Pop No Health Insurance
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHIns), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsHIns_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'POP_NO_HINS'))
            for row in csvInp:
                l1 = listBuild(1)
                l1[0] = row[csvFields.index('geogkey')]
                if row[csvFields.index('B27001e1')] in ('', '.'):
                    l1[1] = None
                else:
                    l1[1] = varSum(row, csvFields, ['B27001e5', 'B27001e8', 'B27001e11', 'B27001e14', 'B27001e17', 'B27001e20', 'B27001e23', 'B27001e26', 'B27001e29', 'B27001e33', 'B27001e36', 'B27001e39', 'B27001e42', 'B27001e45', 'B27001e48', 'B27001e51', 'B27001e54', 'B27001e57'])
                csvOut.writerow(l1)

    # Imputation of Vacancy Status
    with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsVacImp), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('{}acsVacImp_{}.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('GEOID', 'VAC_IMP', 'VAC_NOT_IMP'))
            for row in csvInp:
                l1 = listBuild(2)
                l1[0] = row[csvFields.index('geogkey')]
                l1[1] = varSum(row, csvFields, ['B99253e2'])
                l1[2] = varSum(row, csvFields, ['B99253e3'])
                csvOut.writerow(l1)


    # SQL join for Community Data Snapshots output
    # Creates the database.
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    ## outListComb = []

    with open('{}acsAge_{}.csv'.format(year, geog), 'rb') as rAge:
        sqlCsvAge = csv.reader(rAge)
        csvSqlPrep(sqlCsvAge,'sqlAge')

    with open('{}acsMedAge_{}.csv'.format(year, geog), 'rb') as rMedAge:
        sqlCsvMedAge = csv.reader(rMedAge)
        csvSqlPrep(sqlCsvMedAge,'sqlMedAge')

    with open('{}acsRace_{}.csv'.format(year, geog), 'rb') as rRace:
        sqlCsvRace = csv.reader(rRace)
        csvSqlPrep(sqlCsvRace,'sqlRace')

    with open('{}acsPopHH_{}.csv'.format(year, geog), 'rb') as rPopHH:
        sqlCsvPopHH = csv.reader(rPopHH)
        csvSqlPrep(sqlCsvPopHH,'sqlPopHH')

    with open('{}acsFamSize_{}.csv'.format(year, geog), 'rb') as rFamSize:
        sqlCsvFamSize = csv.reader(rFamSize)
        csvSqlPrep(sqlCsvFamSize,'sqlFamSize')

    with open('{}acsLbrFrc_{}.csv'.format(year, geog), 'rb') as rLbrFrc:
        sqlCsvLbrFrc = csv.reader(rLbrFrc)
        csvSqlPrep(sqlCsvLbrFrc,'sqlLbrFrc')

    with open('{}acsMode_{}.csv'.format(year, geog), 'rb') as rMode:
        sqlCsvMode = csv.reader(rMode)
        csvSqlPrep(sqlCsvMode,'sqlMode')

    with open('{}acsEdu_{}.csv'.format(year, geog), 'rb') as rEdu:
        sqlCsvEdu = csv.reader(rEdu)
        csvSqlPrep(sqlCsvEdu,'sqlEdu')

    with open('{}acsInc_{}.csv'.format(year, geog), 'rb') as rInc:
        sqlCsvInc = csv.reader(rInc)
        csvSqlPrep(sqlCsvInc,'sqlInc')

    with open('{}acsPA_{}.csv'.format(year, geog), 'rb') as rPA:
        sqlCsvPA = csv.reader(rPA)
        csvSqlPrep(sqlCsvPA,'sqlPA')

    with open('{}acsHHType_{}.csv'.format(year, geog), 'rb') as rHHType:
        sqlCsvHHType = csv.reader(rHHType)
        csvSqlPrep(sqlCsvHHType,'sqlHHType')

    with open('{}acsFamMedInc_{}.csv'.format(year, geog), 'rb') as rFMI:
        sqlCsvFMI = csv.reader(rFMI)
        csvSqlPrep(sqlCsvFMI,'sqlFMI')

    with open('{}acsOccVac_{}.csv'.format(year, geog), 'rb') as rOccVac:
        sqlCsvOccVac = csv.reader(rOccVac)
        csvSqlPrep(sqlCsvOccVac,'sqlOccVac')

    with open('{}acsHUType_{}.csv'.format(year, geog), 'rb') as rHUType:
        sqlCsvHUType = csv.reader(rHUType)
        csvSqlPrep(sqlCsvHUType,'sqlHUType')

    with open('{}acsIncTenure_{}.csv'.format(year, geog), 'rb') as rIncTenure:
        sqlCsvIncTenure = csv.reader(rIncTenure)
        csvSqlPrep(sqlCsvIncTenure,'sqlIncTenure')

    with open('{}acsHAgeBRVehAv_{}.csv'.format(year, geog), 'rb') as rHAgeBRVeh:
        sqlCsvHAgeBrVeh = csv.reader(rHAgeBRVeh)
        csvSqlPrep(sqlCsvHAgeBrVeh,'sqlHAgeBRVehAv')

    with open('{}acsHValOwnCst_{}.csv'.format(year, geog), 'rb') as rHValOwnCst:
        sqlCsvHValOwnCst = csv.reader(rHValOwnCst)
        csvSqlPrep(sqlCsvHValOwnCst,'sqlHValOwnCst')

    with open('{}acsRntCst_{}.csv'.format(year, geog), 'rb') as rRntCst:
        sqlCsvRntcst = csv.reader(rRntCst)
        csvSqlPrep(sqlCsvRntcst,'sqlRntcst')

    with open('{}acsLang_{}.csv'.format(year, geog), 'rb') as rLang:
        sqlCsvLang = csv.reader(rLang)
        csvSqlPrep(sqlCsvLang,'sqlLang')

    with open('{}acsEng_{}.csv'.format(year, geog), 'rb') as rEng:
        sqlCsvEng = csv.reader(rEng)
        csvSqlPrep(sqlCsvEng,'sqlEng')

    with open('{}acsPov_{}.csv'.format(year, geog), 'rb') as rPov:
        sqlCsvPov = csv.reader(rPov)
        csvSqlPrep(sqlCsvPov,'sqlPov')

    with open('{}acsPovFam_{}.csv'.format(year, geog), 'rb') as rPovFam:
        sqlCsvPovFam = csv.reader(rPovFam)
        csvSqlPrep(sqlCsvPovFam,'sqlPovFam')

    with open('{}acsDis_{}.csv'.format(year, geog), 'rb') as rDis:
        sqlCsvDis = csv.reader(rDis)
        csvSqlPrep(sqlCsvDis,'sqlDis')

    with open('{}acsHIns_{}.csv'.format(year, geog), 'rb') as rHins:
        sqlCsvHins = csv.reader(rHins)
        csvSqlPrep(sqlCsvHins,'sqlHins')

    with open('{}acsVacImp_{}.csv'.format(year, geog), 'rb') as rVacImp:
        sqlCsvVacImp = csv.reader(rVacImp)
        csvSqlPrep(sqlCsvVacImp,'sqlVacImp')

    with open('{}acsFamMedInc_{}.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOID,sqlFMI.MEDINC_ALL_FAM,sqlFMI.MEDINC_2PF,sqlFMI.MEDINC_3PF,sqlFMI.MEDINC_4PF,sqlFMI.MEDINC_5PF,sqlFMI.MEDINC_6PF,sqlFMI.MEDINC_7MPF'))

    # Creates output csv file
    with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariables{1}.csv'.format(year, geog), 'wb') as w_CDSagg:
        csvCDS_agg = csv.writer(w_CDSagg)
        csvCDS_agg.writerow(('GEOG', 'GEOID', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'MED_AGE', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_2PF', 'CT_3PF', 'CT_4PF', 'CT_5PF', 'CT_6PF', 'CT_7MPF', 'CT_NONFAM_HH', 'CT_2PNF', 'CT_3PNF', 'CT_4PNF', 'CT_5PNF', 'CT_6PNF', 'CT_7MPNF', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'DROVE_AL_MEAN_TT', 'CARPOOL_MEAN_TT', 'TRANSIT_MEAN_TT', 'OTHER_INCL_WALK_BIKE_MEAN_TT', 'ALLMODES_MEAN_TT', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'MEDINC', 'INC_LT_45K', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'VAC_IMP', 'VAC_NOT_IMP', 'VAC_FOR_RENT', 'VAC_FOR_SALE', 'VAC_OTHER', 'OWN_1_PERS_HH', 'OWN_2_PERS_HH', 'OWN_3_PERS_HH', 'OWN_4_PERS_HH', 'OWN_5_PERS_HH', 'OWN_6_PERS_HH', 'OWN_7_MORE_HH', 'RENT_1_PERS_HH', 'RENT_2_PERS_HH', 'RENT_3_PERS_HH', 'RENT_4_PERS_HH', 'RENT_5_PERS_HH', 'RENT_6_PERS_HH', 'RENT_7_MORE_HH', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'MED_ROOMS', 'HU_OWN_1DET', 'HU_OWN_1ATT', 'HU_OWN_2', 'HU_OWN_3_4', 'HU_OWN_5_9', 'HU_OWN_10_19', 'HU_OWN_20_49', 'HU_OWN_50OV', 'HU_OWN_MOB_HOME', 'HU_OWN_OTHER_MOB', 'HU_RENT_1DET', 'HU_RENT_1ATT', 'HU_RENT_2', 'HU_RENT_3_4', 'HU_RENT_5_9', 'HU_RENT_10_19', 'HU_RENT_20_49', 'HU_RENT_50OV', 'HU_RENT_MOB_HOME', 'HU_RENT_OTHER_MOB', 'HA_AFT2000', 'HA_80_00', 'HA_70_00', 'HA_60_80', 'HA_40_70', 'HA_40_60', 'HA_BEF1940', 'MED_HA', 'MED_HA_OWN', 'MED_HA_RENT', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'AGG_VEH_AVAIL', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'MED_HV', 'OWNCST_OV30PCT', 'HU_OWN_INC_LT5K', 'HU_OWN_INC_5K_10K', 'HU_OWN_INC_10K_15K', 'HU_OWN_INC_15K_20K', 'HU_OWN_INC_20K_25K', 'HU_OWN_INC_25K_35K', 'HU_OWN_INC_35K_50K', 'HU_OWN_INC_50K_75K', 'HU_OWN_INC_75K_100K', 'HU_OWN_INC_100K_150K', 'HU_OWN_INC_150KOV', 'HU_RENT_INC_LT5K', 'HU_RENT_INC_5K_10K', 'HU_RENT_INC_10K_15K', 'HU_RENT_INC_15K_20K', 'HU_RENT_INC_20K_25K', 'HU_RENT_INC_25K_35K', 'HU_RENT_INC_35K_50K', 'HU_RENT_INC_50K_75K', 'HU_RENT_INC_75K_100K', 'HU_RENT_INC_100K_150K', 'HU_RENT_INC_150KOV', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT', 'RNTCST_OV30PCT', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'POV_SURV', 'POV_POP', 'TOT_FAMILIES', 'POV_FAM', 'HH_PUB_ASSIST_OR_FOOD_STAMPS', 'GINI_INDEX', 'FAM_INC_UND45K', 'MEDINC_ALL_FAM', 'MEDINC_1PHH', 'MEDINC_2PF', 'MEDINC_3PF', 'MEDINC_4PF', 'MEDINC_5PF', 'MEDINC_6PF', 'MEDINC_7MPF', 'POP_CIV_NONINST', 'DISABLED', 'POP_NO_HINS'))

        # Join tables based on geoid
        cursor.execute('SELECT sqlAge.NAME,sqlAge.GEOID,TOT_POP,sqlAge.UND19,sqlAge.A20_34,sqlAge.A35_49,sqlAge.A50_64,sqlAge.A65_74,sqlAge.A75_84,sqlAge.OV85,sqlMedAge.MED_AGE,sqlRace.WHITE,sqlRace.HISP,sqlRace.BLACK,sqlRace.ASIAN,sqlRace.OTHER,sqlPopHH.POP_HH,sqlHHType.CT_SP_WCHILD,sqlFamSize.CT_1PHH,sqlFamSize.CT_2PHH,sqlFamSize.CT_3PHH,sqlFamSize.CT_4MPHH,sqlFamSize.CT_FAM_HH,sqlFamSize.CT_2PF,sqlFamSize.CT_3PF,sqlFamSize.CT_4PF,sqlFamSize.CT_5PF,sqlFamSize.CT_6PF,sqlFamSize.CT_7MPF,sqlFamSize.CT_NONFAM_HH,sqlFamSize.CT_2PNF,sqlFamSize.CT_3PNF,sqlFamSize.CT_4PNF,sqlFamSize.CT_5PNF,sqlFamSize.CT_6PNF,sqlFamSize.CT_7MPNF,sqlLbrFrc.POP_16OV,sqlLbrFrc.IN_LBFRC,sqlLbrFrc.EMP,sqlLbrFrc.UNEMP,sqlLbrFrc.NOT_IN_LBFRC,sqlMode.WORK_AT_HOME,sqlMode.TOT_COMM,sqlMode.DROVE_AL,sqlMode.CARPOOL,sqlMode.TRANSIT,sqlMode.WALK_BIKE,sqlMode.COMM_OTHER,sqlMode.DROVE_AL_MEAN_TT,sqlMode.CARPOOL_MEAN_TT,sqlMode.TRANSIT_MEAN_TT,sqlMode.OTHER_INCL_WALK_BIKE_MEAN_TT,sqlMode.ALLMODES_MEAN_TT,sqlMode.AGG_TT,sqlMode.NO_VEH,sqlMode.ONE_VEH,sqlMode.TWO_VEH,sqlMode.THREEOM_VEH,sqlEdu.POP_25OV,sqlEdu.LT_HS,sqlEdu.HS,sqlEdu.SOME_COLL,sqlEdu.ASSOC,sqlEdu.BACH,sqlEdu.GRAD_PROF,sqlInc.INC_LT_25K,sqlInc.INC_25_50K,sqlInc.INC_50_75K,sqlInc.INC_75_100K,sqlInc.INC_100_150K,sqlInc.INC_GT_150,sqlInc.MEDINC,sqlInc.INC_LT_45K,sqlOccVac.TOT_HH,sqlOccVac.OWN_OCC_HU,sqlOccVac.RENT_OCC_HU,sqlOccVac.VAC_HU,sqlVacImp.VAC_IMP,sqlVacImp.VAC_NOT_IMP,sqlOccVac.VAC_FOR_RENT,sqlOccVac.VAC_FOR_SALE,sqlOccVac.VAC_OTHER,sqlOccVac.OWN_1_PERS_HH,sqlOccVac.OWN_2_PERS_HH,sqlOccVac.OWN_3_PERS_HH,sqlOccVac.OWN_4_PERS_HH,sqlOccVac.OWN_5_PERS_HH,sqlOccVac.OWN_6_PERS_HH,sqlOccVac.OWN_7_MORE_HH,sqlOccVac.RENT_1_PERS_HH,sqlOccVac.RENT_2_PERS_HH,sqlOccVac.RENT_3_PERS_HH,sqlOccVac.RENT_4_PERS_HH,sqlOccVac.RENT_5_PERS_HH,sqlOccVac.RENT_6_PERS_HH,sqlOccVac.RENT_7_MORE_HH,sqlHUType.HU_TOT,sqlHUType.HU_SNG_DET,sqlHUType.HU_SNG_ATT,sqlHUType.HU_2UN,sqlHUType.HU_3_4UN,sqlHUType.HU_GT_5UN,sqlHUType.MED_ROOMS,sqlHUType.HU_OWN_1DET,sqlHUType.HU_OWN_1ATT,sqlHUType.HU_OWN_2,sqlHUType.HU_OWN_3_4,sqlHUType.HU_OWN_5_9,sqlHUType.HU_OWN_10_19,sqlHUType.HU_OWN_20_49,sqlHUType.HU_OWN_50OV,sqlHUType.HU_OWN_MOB_HOME,sqlHUType.HU_OWN_OTHER_MOB,sqlHUType.HU_RENT_1DET,sqlHUType.HU_RENT_1ATT,sqlHUType.HU_RENT_2,sqlHUType.HU_RENT_3_4,sqlHUType.HU_RENT_5_9,sqlHUType.HU_RENT_10_19,sqlHUType.HU_RENT_20_49,sqlHUType.HU_RENT_50OV,sqlHUType.HU_RENT_MOB_HOME,sqlHUType.HU_RENT_OTHER_MOB,sqlHAgeBRVehAv.HA_AFT2000,sqlHAgeBRVehAv.HA_80_00,sqlHAgeBRVehAv.HA_70_00,sqlHAgeBRVehAv.HA_60_80,sqlHAgeBRVehAv.HA_40_70,sqlHAgeBRVehAv.HA_40_60,sqlHAgeBRVehAv.HA_BEF1940,sqlHAgeBRVehAv.MED_HA,sqlHAgeBRVehAv.MED_HA_OWN,sqlHAgeBRVehAv.MED_HA_RENT,sqlHAgeBRVehAv.BR_0_1,sqlHAgeBRVehAv.BR_2,sqlHAgeBRVehAv.BR_3,sqlHAgeBRVehAv.BR_4,sqlHAgeBRVehAv.BR_5,sqlHAgeBRVehAv.AGG_VEH_AVAIL,sqlRntCst.HV_LT_150K,sqlRntCst.HV_150_300K,sqlRntCst.HV_300_500K,sqlRntCst.HV_GT_500K,sqlRntCst.MED_HV,sqlHValOwnCst.OWNCST_OV30PCT,sqlIncTenure.HU_OWN_INC_LT5K,sqlIncTenure.HU_OWN_INC_5K_10K,sqlIncTenure.HU_OWN_INC_10K_15K,sqlIncTenure.HU_OWN_INC_15K_20K,sqlIncTenure.HU_OWN_INC_20K_25K,sqlIncTenure.HU_OWN_INC_25K_35K,sqlIncTenure.HU_OWN_INC_35K_50K,sqlIncTenure.HU_OWN_INC_50K_75K,sqlIncTenure.HU_OWN_INC_75K_100K,sqlIncTenure.HU_OWN_INC_100K_150K,sqlIncTenure.HU_OWN_INC_150KOV,sqlIncTenure.HU_RENT_INC_LT5K,sqlIncTenure.HU_RENT_INC_5K_10K,sqlIncTenure.HU_RENT_INC_10K_15K,sqlIncTenure.HU_RENT_INC_15K_20K,sqlIncTenure.HU_RENT_INC_20K_25K,sqlIncTenure.HU_RENT_INC_25K_35K,sqlIncTenure.HU_RENT_INC_35K_50K,sqlIncTenure.HU_RENT_INC_50K_75K,sqlIncTenure.HU_RENT_INC_75K_100K,sqlIncTenure.HU_RENT_INC_100K_150K,sqlIncTenure.HU_RENT_INC_150KOV,sqlIncTenure.HCUND20K,sqlIncTenure.HCUND20K_LT20PCT,sqlIncTenure.HCUND20K_20_29PCT,sqlIncTenure.HCUND20K_30MPCT,sqlIncTenure.HC20Kto49K,sqlIncTenure.HC20Kto49K_LT20PCT,sqlIncTenure.HC20Kto49K_20_29PCT,sqlIncTenure.HC20Kto49K_30MPCT,sqlIncTenure.HC50Kto75K,sqlIncTenure.HC50Kto75K_LT20PCT,sqlIncTenure.HC50Kto75K_20_29PCT,sqlIncTenure.HC50Kto75K_30MPCT,sqlIncTenure.HCOV75K,sqlIncTenure.HCOV75K_LT20PCT,sqlIncTenure.HCOV75K_20_29PCT,sqlIncTenure.HCOV75K_30MPCT,sqlRntcst.RNTCST_OV30PCT,sqlLang.ENGLISH,sqlLang.SPANISH,sqlLang.SLAVIC,sqlLang.CHINESE,sqlLang.TAGALOG,sqlLang.ARABIC,sqlLang.KOREAN,sqlLang.OTHER_ASIAN,sqlLang.OTHER_EURO,sqlLang.OTHER_UNSPEC,sqlEng.NATIVE,sqlEng.FOR_BORN,sqlEng.POP_OV5,sqlEng.ONLY_ENGLISH,sqlEng.NOT_ENGLISH,sqlEng.LING_ISO,sqlPov.POV_SURV,sqlPov.POV_POP,sqlPovFam.TOT_FAMILIES,sqlPovFam.POV_FAM,sqlPA.HH_PUB_ASSIST_OR_FOOD_STAMPS,sqlPA.GINI_INDEX,sqlPA.FAM_INC_UND45K,sqlFMI.MEDINC_ALL_FAM,sqlInc.MEDINC_1PHH,sqlFMI.MEDINC_2PF,sqlFMI.MEDINC_3PF,sqlFMI.MEDINC_4PF,sqlFMI.MEDINC_5PF,sqlFMI.MEDINC_6PF,sqlFMI.MEDINC_7MPF,sqlDis.POP_CIV_NONINST,sqlDis.DISABLED,sqlHins.POP_NO_HINS FROM sqlAge INNER JOIN sqlMedAge ON (sqlAge.GEOID =  sqlMedAge.GEOID) INNER JOIN sqlRace ON (sqlMedAge.GEOID =  sqlRace.GEOID) INNER JOIN sqlPopHH ON (sqlRace.GEOID =  sqlPopHH.GEOID) INNER JOIN sqlLbrFrc ON (sqlPopHH.GEOID =  sqlLbrFrc.GEOID) INNER JOIN sqlMode ON (sqlLbrFrc.GEOID =  sqlMode.GEOID) INNER JOIN sqlEdu ON (sqlMode.GEOID =  sqlEdu.GEOID) INNER JOIN sqlInc ON (sqlEdu.GEOID =  sqlInc.GEOID) INNER JOIN sqlOccVac ON (sqlInc.GEOID =  sqlOccVac.GEOID) INNER JOIN sqlHUType ON (sqlOccVac.GEOID =  sqlHUType.GEOID) INNER JOIN sqlIncTenure ON (sqlOccVac.GEOID =  sqlIncTenure.GEOID) INNER JOIN sqlHAgeBRVehAv ON (sqlHUType.GEOID =  sqlHAgeBRVehAv.GEOID) INNER JOIN sqlHValOwnCst ON (sqlHAgeBRVehAv.GEOID =  sqlHValOwnCst.GEOID) INNER JOIN sqlRntcst ON (sqlHValOwnCst.GEOID =  sqlRntcst.GEOID) INNER JOIN sqlEng ON (sqlRntcst.GEOID =  sqlEng.GEOID) INNER JOIN sqlPov ON (sqlEng.GEOID =  sqlPov.GEOID) INNER JOIN sqlPovFam ON (sqlEng.GEOID =  sqlPovFam.GEOID) INNER JOIN sqlPA ON (sqlPA.GEOID =  sqlPov.GEOID) INNER JOIN sqlDis ON (sqlPA.GEOID =  sqlDis.GEOID) INNER JOIN sqlHins ON (sqlDis.GEOID =  sqlHins.GEOID) INNER JOIN sqlVacImp ON (sqlHins.GEOID =  sqlVacImp.GEOID) INNER JOIN sqlFMI ON (sqlVacImp.GEOID =  sqlFMI.GEOID) INNER JOIN sqlFamSize ON (sqlFamSize.GEOID =  sqlFMI.GEOID) INNER JOIN sqlHHType ON (sqlFMI.GEOID =  sqlHHType.GEOID) INNER JOIN sqlLang ON (sqlHHType.GEOID = sqlLang.GEOID)')
        for i in cursor:
            i = list(i)
            csvCDS_agg.writerow(i)

        # Deletes intermediate csvs
        csv_list = ['{}acsAge_{}.csv'.format(year, geog), '{}acsMedAge_{}.csv'.format(year, geog), '{}acsRace_{}.csv'.format(year, geog), '{}acsPopHH_{}.csv'.format(year, geog), '{}acsLbrFrc_{}.csv'.format(year, geog), '{}acsMode_{}.csv'.format(year, geog), '{}acsEdu_{}.csv'.format(year, geog), '{}acsInc_{}.csv'.format(year, geog), '{}acsPA_{}.csv'.format(year, geog), '{}acsOccVac_{}.csv'.format(year, geog), '{}acsHUType_{}.csv'.format(year, geog), '{}acsHAgeBRVehAv_{}.csv'.format(year, geog), '{}acsHValOwnCst_{}.csv'.format(year, geog), '{}acsRntCst_{}.csv'.format(year, geog), '{}acsEng_{}.csv'.format(year, geog), '{}acsPov_{}.csv'.format(year, geog), '{}acsPovFam_{}.csv'.format(year, geog), '{}acsDis_{}.csv'.format(year, geog), '{}acsHIns_{}.csv'.format(year, geog), '{}acsVacImp_{}.csv'.format(year, geog), '{}acsFamMedInc_{}.csv'.format(year, geog), '{}acsFamSize_{}.csv'.format(year, geog), '{}acsLang_{}.csv'.format(year, geog), '{}acsHHType_{}.csv'.format(year, geog), '{}acsIncTenure_{}.csv'.format(year, geog)]
        for csv_file in csv_list:
            try:
                os.remove(csv_file)
            except:
                pass

        print(geog, 'complete.')


if cca_proc_flag:
    ## CCA List
    cca_list = ['Albany Park', 'Archer Heights', 'Armour Square', 'Ashburn', 'Auburn Gresham', 'Austin', 'Avalon Park', 'Avondale', 'Belmont Cragin', 'Beverly', 'Bridgeport', 'Brighton Park', 'Burnside', 'Calumet Heights', 'Chatham', 'Chicago Lawn', 'Clearing', 'Douglas', 'Dunning', 'East Garfield Park', 'East Side', 'Edgewater', 'Edison Park', 'Englewood', 'Forest Glen', 'Fuller Park', 'Gage Park', 'Garfield Ridge', 'Grand Boulevard', 'Greater Grand Crossing', 'Hegewisch', 'Hermosa', 'Humboldt Park', 'Hyde Park', 'Irving Park', 'Jefferson Park', 'Kenwood', 'Lake View', 'Lincoln Park', 'Lincoln Square', 'Logan Square', 'Lower West Side', 'McKinley Park', 'Montclare', 'Morgan Park', 'Mount Greenwood', 'Near North Side', 'Near South Side', 'Near West Side', 'New City', 'North Center', 'North Lawndale', 'North Park', 'Norwood Park', 'Oakland', "O'Hare", 'Portage Park', 'Pullman', 'Riverdale', 'Rogers Park', 'Roseland', 'South Chicago', 'South Deering', 'South Lawndale', 'South Shore', 'The Loop', 'Uptown', 'Washington Heights', 'Washington Park', 'West Elsdon', 'West Englewood', 'West Garfield Park', 'West Lawn', 'West Pullman', 'West Ridge', 'West Town', 'Woodlawn']

    # Defines blockgroup geography.
    geog = 'blockgroup'

    # Opens BG/CCA ratio crosswalk and loads to list of tuples
    with open('Blocks_to_CCA_BG.csv', 'rb') as rfile:
        rfile.readline()
        crosswalk_list = []
        for row in rfile:
            if row.startswith('17'):
                crosswalk_list.append(tuple(row.strip().split(',')))

    # Joins each block to BG data, filters fields and multiplies by appropriate ratio
    with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariables{1}.csv'.format(year, geog)) as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('CCA_All_{}_{}_Allocated.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('CCA', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_NONFAM_HH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'HA_AFT2000', 'HA_70_00', 'HA_40_70', 'HA_BEF1940', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'OWNCST_OV30PCT', 'RNTCST_OV30PCT'))
            for block, blockgroup, cca, bg_pop_rat, bg_hh_rat, bg_hu_rat in crosswalk_list:
                for row in csvInp:
                    if row[1] == blockgroup:
                        l1 = listBuild(59)
                        l1[0] = cca
                        l1[1] = varSum(row, csvFields, ['TOT_POP']) * float(bg_pop_rat)
                        l1[2] = varSum(row, csvFields, ['UND19']) * float(bg_pop_rat)
                        l1[3] = varSum(row, csvFields, ['A20_34']) * float(bg_pop_rat)
                        l1[4] = varSum(row, csvFields, ['A35_49']) * float(bg_pop_rat)
                        l1[5] = varSum(row, csvFields, ['A50_64']) * float(bg_pop_rat)
                        l1[6] = varSum(row, csvFields, ['A65_74']) * float(bg_pop_rat)
                        l1[7] = varSum(row, csvFields, ['A75_84']) * float(bg_pop_rat)
                        l1[8] = varSum(row, csvFields, ['OV85']) * float(bg_pop_rat)
                        l1[9] = varSum(row, csvFields, ['WHITE']) * float(bg_pop_rat)
                        l1[10] = varSum(row, csvFields, ['HISP']) * float(bg_pop_rat)
                        l1[11] = varSum(row, csvFields, ['BLACK']) * float(bg_pop_rat)
                        l1[12] = varSum(row, csvFields, ['ASIAN']) * float(bg_pop_rat)
                        l1[13] = varSum(row, csvFields, ['OTHER']) * float(bg_pop_rat)
                        l1[14] = varSum(row, csvFields, ['POP_HH']) * float(bg_hh_rat)
                        l1[15] = varSum(row, csvFields, ['CT_SP_WCHILD']) * float(bg_hh_rat)
                        l1[16] = varSum(row, csvFields, ['CT_1PHH']) * float(bg_hh_rat)
                        l1[17] = varSum(row, csvFields, ['CT_2PHH']) * float(bg_hh_rat)
                        l1[18] = varSum(row, csvFields, ['CT_3PHH']) * float(bg_hh_rat)
                        l1[19] = varSum(row, csvFields, ['CT_4MPHH']) * float(bg_hh_rat)
                        l1[20] = varSum(row, csvFields, ['CT_FAM_HH']) * float(bg_hh_rat)
                        l1[21] = varSum(row, csvFields, ['CT_NONFAM_HH']) * float(bg_hh_rat)
                        l1[22] = varSum(row, csvFields, ['POP_25OV']) * float(bg_pop_rat)
                        l1[23] = varSum(row, csvFields, ['LT_HS']) * float(bg_pop_rat)
                        l1[24] = varSum(row, csvFields, ['HS']) * float(bg_pop_rat)
                        l1[25] = varSum(row, csvFields, ['SOME_COLL']) * float(bg_pop_rat)
                        l1[26] = varSum(row, csvFields, ['ASSOC']) * float(bg_pop_rat)
                        l1[27] = varSum(row, csvFields, ['BACH']) * float(bg_pop_rat)
                        l1[28] = varSum(row, csvFields, ['GRAD_PROF']) * float(bg_pop_rat)
                        l1[29] = varSum(row, csvFields, ['INC_LT_25K']) * float(bg_hh_rat)
                        l1[30] = varSum(row, csvFields, ['INC_25_50K']) * float(bg_hh_rat)
                        l1[31] = varSum(row, csvFields, ['INC_50_75K']) * float(bg_hh_rat)
                        l1[32] = varSum(row, csvFields, ['INC_75_100K']) * float(bg_hh_rat)
                        l1[33] = varSum(row, csvFields, ['INC_100_150K']) * float(bg_hh_rat)
                        l1[34] = varSum(row, csvFields, ['INC_GT_150']) * float(bg_hh_rat)
                        l1[35] = varSum(row, csvFields, ['TOT_HH']) * float(bg_hh_rat)
                        l1[36] = varSum(row, csvFields, ['OWN_OCC_HU']) * float(bg_hu_rat)
                        l1[37] = varSum(row, csvFields, ['RENT_OCC_HU']) * float(bg_hu_rat)
                        l1[38] = varSum(row, csvFields, ['VAC_HU']) * float(bg_hu_rat)
                        l1[39] = varSum(row, csvFields, ['HU_TOT']) * float(bg_hu_rat)
                        l1[40] = varSum(row, csvFields, ['HU_SNG_DET']) * float(bg_hu_rat)
                        l1[41] = varSum(row, csvFields, ['HU_SNG_ATT']) * float(bg_hu_rat)
                        l1[42] = varSum(row, csvFields, ['HU_2UN']) * float(bg_hu_rat)
                        l1[43] = varSum(row, csvFields, ['HU_3_4UN']) * float(bg_hu_rat)
                        l1[44] = varSum(row, csvFields, ['HU_GT_5UN']) * float(bg_hu_rat)
                        l1[45] = varSum(row, csvFields, ['HA_AFT2000']) * float(bg_hu_rat)
                        l1[46] = varSum(row, csvFields, ['HA_70_00']) * float(bg_hu_rat)
                        l1[47] = varSum(row, csvFields, ['HA_40_70']) * float(bg_hu_rat)
                        l1[48] = varSum(row, csvFields, ['HA_BEF1940']) * float(bg_hu_rat)
                        l1[49] = varSum(row, csvFields, ['BR_0_1']) * float(bg_hu_rat)
                        l1[50] = varSum(row, csvFields, ['BR_2']) * float(bg_hu_rat)
                        l1[51] = varSum(row, csvFields, ['BR_3']) * float(bg_hu_rat)
                        l1[52] = varSum(row, csvFields, ['BR_4']) * float(bg_hu_rat)
                        l1[53] = varSum(row, csvFields, ['BR_5']) * float(bg_hu_rat)
                        l1[54] = varSum(row, csvFields, ['HV_LT_150K']) * float(bg_hh_rat)
                        l1[55] = varSum(row, csvFields, ['HV_150_300K']) * float(bg_hh_rat)
                        l1[56] = varSum(row, csvFields, ['HV_300_500K']) * float(bg_hh_rat)
                        l1[57] = varSum(row, csvFields, ['HV_GT_500K']) * float(bg_hh_rat)
                        l1[58] = varSum(row, csvFields, ['OWNCST_OV30PCT']) * float(bg_hh_rat)
                        l1[59] = varSum(row, csvFields, ['RNTCST_OV30PCT']) * float(bg_hh_rat)
                        csvOut.writerow(l1)
                        break
                    else:
                        pass
                rfile.seek(0)

    # Defines tract geography.
    geog = 'tract'

    # Opens BG/CCA ratio crosswalk and loads to list of tuples
    with open('Blocks_to_CCA_TR.csv', 'rb') as rfile:
        rfile.readline()
        crosswalk_list = []
        for row in rfile:
            if row.startswith('17'):
                crosswalk_list.append(tuple(row.strip().split(',')))

    # Joins each block to TR data, filters fields and multiplies by appropriate ratio
    with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariables{1}.csv'.format(year, geog)) as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('CCA_All_{}_{}_Allocated.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('CCA', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT'))
            for block, tract, cca, tr_pop_rat, tr_hh_rat, tr_hu_rat in crosswalk_list:
                for row in csvInp:
                    if row[1] == tract:
                        l1 = listBuild(49)
                        l1[0] = cca
                        l1[1] = varSum(row, csvFields, ['POP_16OV']) * float(tr_pop_rat)
                        l1[2] = varSum(row, csvFields, ['IN_LBFRC']) * float(tr_pop_rat)
                        l1[3] = varSum(row, csvFields, ['EMP']) * float(tr_pop_rat)
                        l1[4] = varSum(row, csvFields, ['UNEMP']) * float(tr_pop_rat)
                        l1[5] = varSum(row, csvFields, ['NOT_IN_LBFRC']) * float(tr_pop_rat)
                        l1[6] = varSum(row, csvFields, ['WORK_AT_HOME']) * float(tr_pop_rat)
                        l1[7] = varSum(row, csvFields, ['TOT_COMM']) * float(tr_pop_rat)
                        l1[8] = varSum(row, csvFields, ['DROVE_AL']) * float(tr_pop_rat)
                        l1[9] = varSum(row, csvFields, ['CARPOOL']) * float(tr_pop_rat)
                        l1[10] = varSum(row, csvFields, ['TRANSIT']) * float(tr_pop_rat)
                        l1[11] = varSum(row, csvFields, ['WALK_BIKE']) * float(tr_pop_rat)
                        l1[12] = varSum(row, csvFields, ['COMM_OTHER']) * float(tr_pop_rat)
                        try:
                            l1[13] = varSum(row, csvFields, ['AGG_TT']) * float(tr_pop_rat)
                        except ValueError:
                            l1[13] = 'N/A'
                        l1[14] = varSum(row, csvFields, ['NO_VEH']) * float(tr_hh_rat)
                        l1[15] = varSum(row, csvFields, ['ONE_VEH']) * float(tr_hh_rat)
                        l1[16] = varSum(row, csvFields, ['TWO_VEH']) * float(tr_hh_rat)
                        l1[17] = varSum(row, csvFields, ['THREEOM_VEH']) * float(tr_hh_rat)
                        l1[18] = varSum(row, csvFields, ['ENGLISH']) * float(tr_pop_rat)
                        l1[19] = varSum(row, csvFields, ['SPANISH']) * float(tr_pop_rat)
                        l1[20] = varSum(row, csvFields, ['SLAVIC']) * float(tr_pop_rat)
                        l1[21] = varSum(row, csvFields, ['CHINESE']) * float(tr_pop_rat)
                        l1[22] = varSum(row, csvFields, ['TAGALOG']) * float(tr_pop_rat)
                        l1[23] = varSum(row, csvFields, ['ARABIC']) * float(tr_pop_rat)
                        l1[24] = varSum(row, csvFields, ['KOREAN']) * float(tr_pop_rat)
                        l1[25] = varSum(row, csvFields, ['OTHER_ASIAN']) * float(tr_pop_rat)
                        l1[26] = varSum(row, csvFields, ['OTHER_EURO']) * float(tr_pop_rat)
                        l1[27] = varSum(row, csvFields, ['OTHER_UNSPEC']) * float(tr_pop_rat)
                        l1[28] = varSum(row, csvFields, ['NATIVE']) * float(tr_pop_rat)
                        l1[29] = varSum(row, csvFields, ['FOR_BORN']) * float(tr_pop_rat)
                        l1[30] = varSum(row, csvFields, ['POP_OV5']) * float(tr_pop_rat)
                        l1[31] = varSum(row, csvFields, ['ONLY_ENGLISH']) * float(tr_pop_rat)
                        l1[32] = varSum(row, csvFields, ['NOT_ENGLISH']) * float(tr_pop_rat)
                        l1[33] = varSum(row, csvFields, ['LING_ISO']) * float(tr_pop_rat)
                        l1[34] = varSum(row, csvFields, ['HCUND20K']) * float(tr_hh_rat)
                        l1[35] = varSum(row, csvFields, ['HCUND20K_LT20PCT']) * float(tr_hh_rat)
                        l1[36] = varSum(row, csvFields, ['HCUND20K_20_29PCT']) * float(tr_hh_rat)
                        l1[37] = varSum(row, csvFields, ['HCUND20K_30MPCT']) * float(tr_hh_rat)
                        l1[38] = varSum(row, csvFields, ['HC20Kto49K']) * float(tr_hh_rat)
                        l1[39] = varSum(row, csvFields, ['HC20Kto49K_LT20PCT']) * float(tr_hh_rat)
                        l1[40] = varSum(row, csvFields, ['HC20Kto49K_20_29PCT']) * float(tr_hh_rat)
                        l1[41] = varSum(row, csvFields, ['HC20Kto49K_30MPCT']) * float(tr_hh_rat)
                        l1[42] = varSum(row, csvFields, ['HC50Kto75K']) * float(tr_hh_rat)
                        l1[43] = varSum(row, csvFields, ['HC50Kto75K_LT20PCT']) * float(tr_hh_rat)
                        l1[44] = varSum(row, csvFields, ['HC50Kto75K_20_29PCT']) * float(tr_hh_rat)
                        l1[45] = varSum(row, csvFields, ['HC50Kto75K_30MPCT']) * float(tr_hh_rat)
                        l1[46] = varSum(row, csvFields, ['HCOV75K']) * float(tr_hh_rat)
                        l1[47] = varSum(row, csvFields, ['HCOV75K_LT20PCT']) * float(tr_hh_rat)
                        l1[48] = varSum(row, csvFields, ['HCOV75K_20_29PCT']) * float(tr_hh_rat)
                        l1[49] = varSum(row, csvFields, ['HCOV75K_30MPCT']) * float(tr_hh_rat)
                        csvOut.writerow(l1)
                        break
                    else:
                        pass
                rfile.seek(0)

    # Defines blockgroup geography.
    geog = 'blockgroup'

    # Summarizes filtered csvs by CCA
    with open('CCA_All_{}_{}_Allocated.csv'.format(year, geog), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('CCA_All_{}_{}_Summarized.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('CCA', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_NONFAM_HH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'HA_AFT2000', 'HA_70_00', 'HA_40_70', 'HA_BEF1940', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'OWNCST_OV30PCT', 'RNTCST_OV30PCT'))
            for cca in cca_list:
                l1 = listBuild(59)
                l1[0] = cca
                for row in csvInp:
                    if row[0] == cca:
                        l1[1] += varSum(row, csvFields, ['TOT_POP'])
                        l1[2] += varSum(row, csvFields, ['UND19'])
                        l1[3] += varSum(row, csvFields, ['A20_34'])
                        l1[4] += varSum(row, csvFields, ['A35_49'])
                        l1[5] += varSum(row, csvFields, ['A50_64'])
                        l1[6] += varSum(row, csvFields, ['A65_74'])
                        l1[7] += varSum(row, csvFields, ['A75_84'])
                        l1[8] += varSum(row, csvFields, ['OV85'])
                        l1[9] += varSum(row, csvFields, ['WHITE'])
                        l1[10] += varSum(row, csvFields, ['HISP'])
                        l1[11] += varSum(row, csvFields, ['BLACK'])
                        l1[12] += varSum(row, csvFields, ['ASIAN'])
                        l1[13] += varSum(row, csvFields, ['OTHER'])
                        l1[14] += varSum(row, csvFields, ['POP_HH'])
                        l1[15] += varSum(row, csvFields, ['CT_SP_WCHILD'])
                        l1[16] += varSum(row, csvFields, ['CT_1PHH'])
                        l1[17] += varSum(row, csvFields, ['CT_2PHH'])
                        l1[18] += varSum(row, csvFields, ['CT_3PHH'])
                        l1[19] += varSum(row, csvFields, ['CT_4MPHH'])
                        l1[20] += varSum(row, csvFields, ['CT_FAM_HH'])
                        l1[21] += varSum(row, csvFields, ['CT_NONFAM_HH'])
                        l1[22] += varSum(row, csvFields, ['POP_25OV'])
                        l1[23] += varSum(row, csvFields, ['LT_HS'])
                        l1[24] += varSum(row, csvFields, ['HS'])
                        l1[25] += varSum(row, csvFields, ['SOME_COLL'])
                        l1[26] += varSum(row, csvFields, ['ASSOC'])
                        l1[27] += varSum(row, csvFields, ['BACH'])
                        l1[28] += varSum(row, csvFields, ['GRAD_PROF'])
                        l1[29] += varSum(row, csvFields, ['INC_LT_25K'])
                        l1[30] += varSum(row, csvFields, ['INC_25_50K'])
                        l1[31] += varSum(row, csvFields, ['INC_50_75K'])
                        l1[32] += varSum(row, csvFields, ['INC_75_100K'])
                        l1[33] += varSum(row, csvFields, ['INC_100_150K'])
                        l1[34] += varSum(row, csvFields, ['INC_GT_150'])
                        l1[35] += varSum(row, csvFields, ['TOT_HH'])
                        l1[36] += varSum(row, csvFields, ['OWN_OCC_HU'])
                        l1[37] += varSum(row, csvFields, ['RENT_OCC_HU'])
                        l1[38] += varSum(row, csvFields, ['VAC_HU'])
                        l1[39] += varSum(row, csvFields, ['HU_TOT'])
                        l1[40] += varSum(row, csvFields, ['HU_SNG_DET'])
                        l1[41] += varSum(row, csvFields, ['HU_SNG_ATT'])
                        l1[42] += varSum(row, csvFields, ['HU_2UN'])
                        l1[43] += varSum(row, csvFields, ['HU_3_4UN'])
                        l1[44] += varSum(row, csvFields, ['HU_GT_5UN'])
                        l1[45] += varSum(row, csvFields, ['HA_AFT2000'])
                        l1[46] += varSum(row, csvFields, ['HA_70_00'])
                        l1[47] += varSum(row, csvFields, ['HA_40_70'])
                        l1[48] += varSum(row, csvFields, ['HA_BEF1940'])
                        l1[49] += varSum(row, csvFields, ['BR_0_1'])
                        l1[50] += varSum(row, csvFields, ['BR_2'])
                        l1[51] += varSum(row, csvFields, ['BR_3'])
                        l1[52] += varSum(row, csvFields, ['BR_4'])
                        l1[53] += varSum(row, csvFields, ['BR_5'])
                        l1[54] += varSum(row, csvFields, ['HV_LT_150K'])
                        l1[55] += varSum(row, csvFields, ['HV_150_300K'])
                        l1[56] += varSum(row, csvFields, ['HV_300_500K'])
                        l1[57] += varSum(row, csvFields, ['HV_GT_500K'])
                        l1[58] += varSum(row, csvFields, ['OWNCST_OV30PCT'])
                        l1[59] += varSum(row, csvFields, ['RNTCST_OV30PCT'])

                # Return to start of input csv
                rfile.seek(0)

                # Rounds to whole number, writes to out csv
                for i in range(1, len(l1)):
                    l1[i] = round(l1[i], 0)
                csvOut.writerow(l1)

    # Defines tract geography.
    geog = 'tract'

    # Summarizes filtered csvs by CCA
    with open('CCA_All_{}_{}_Allocated.csv'.format(year, geog), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        try:
            csvFields = csvInp.next()
        except AttributeError:
            csvFields = next(csvInp)
        with open('CCA_All_{}_{}_Summarized.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('CCA', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT'))
            for cca in cca_list:
                l1 = listBuild(49)
                l1[0] = cca
                for row in csvInp:
                    if row[0] == cca:
                        l1[1] += varSum(row, csvFields, ['POP_16OV'])
                        l1[2] += varSum(row, csvFields, ['IN_LBFRC'])
                        l1[3] += varSum(row, csvFields, ['EMP'])
                        l1[4] += varSum(row, csvFields, ['UNEMP'])
                        l1[5] += varSum(row, csvFields, ['NOT_IN_LBFRC'])
                        l1[6] += varSum(row, csvFields, ['WORK_AT_HOME'])
                        l1[7] += varSum(row, csvFields, ['TOT_COMM'])
                        l1[8] += varSum(row, csvFields, ['DROVE_AL'])
                        l1[9] += varSum(row, csvFields, ['CARPOOL'])
                        l1[10] += varSum(row, csvFields, ['TRANSIT'])
                        l1[11] += varSum(row, csvFields, ['WALK_BIKE'])
                        l1[12] += varSum(row, csvFields, ['COMM_OTHER'])
                        try:
                            l1[13] += varSum(row, csvFields, ['AGG_TT'])
                        except ValueError:
                            l1[13] = 'N/A'
                        except TypeError:
                            l1[13] = 'N/A'
                        l1[14] += varSum(row, csvFields, ['NO_VEH'])
                        l1[15] += varSum(row, csvFields, ['ONE_VEH'])
                        l1[16] += varSum(row, csvFields, ['TWO_VEH'])
                        l1[17] += varSum(row, csvFields, ['THREEOM_VEH'])
                        l1[18] += varSum(row, csvFields, ['ENGLISH'])
                        l1[19] += varSum(row, csvFields, ['SPANISH'])
                        l1[20] += varSum(row, csvFields, ['SLAVIC'])
                        l1[21] += varSum(row, csvFields, ['CHINESE'])
                        l1[22] += varSum(row, csvFields, ['TAGALOG'])
                        l1[23] += varSum(row, csvFields, ['ARABIC'])
                        l1[24] += varSum(row, csvFields, ['KOREAN'])
                        l1[25] += varSum(row, csvFields, ['OTHER_ASIAN'])
                        l1[26] += varSum(row, csvFields, ['OTHER_EURO'])
                        l1[27] += varSum(row, csvFields, ['OTHER_UNSPEC'])
                        l1[28] += varSum(row, csvFields, ['NATIVE'])
                        l1[29] += varSum(row, csvFields, ['FOR_BORN'])
                        l1[30] += varSum(row, csvFields, ['POP_OV5'])
                        l1[31] += varSum(row, csvFields, ['ONLY_ENGLISH'])
                        l1[32] += varSum(row, csvFields, ['NOT_ENGLISH'])
                        l1[33] += varSum(row, csvFields, ['LING_ISO'])
                        l1[34] += varSum(row, csvFields, ['HCUND20K'])
                        l1[35] += varSum(row, csvFields, ['HCUND20K_LT20PCT'])
                        l1[36] += varSum(row, csvFields, ['HCUND20K_20_29PCT'])
                        l1[37] += varSum(row, csvFields, ['HCUND20K_30MPCT'])
                        l1[38] += varSum(row, csvFields, ['HC20Kto49K'])
                        l1[39] += varSum(row, csvFields, ['HC20Kto49K_LT20PCT'])
                        l1[40] += varSum(row, csvFields, ['HC20Kto49K_20_29PCT'])
                        l1[41] += varSum(row, csvFields, ['HC20Kto49K_30MPCT'])
                        l1[42] += varSum(row, csvFields, ['HC50Kto75K'])
                        l1[43] += varSum(row, csvFields, ['HC50Kto75K_LT20PCT'])
                        l1[44] += varSum(row, csvFields, ['HC50Kto75K_20_29PCT'])
                        l1[45] += varSum(row, csvFields, ['HC50Kto75K_30MPCT'])
                        l1[46] += varSum(row, csvFields, ['HCOV75K'])
                        l1[47] += varSum(row, csvFields, ['HCOV75K_LT20PCT'])
                        l1[48] += varSum(row, csvFields, ['HCOV75K_20_29PCT'])
                        l1[49] += varSum(row, csvFields, ['HCOV75K_30MPCT'])

                # Return to start of input csv
                rfile.seek(0)

                # Rounds to whole number, writes to out csv
                for i in range(1, len(l1)):
                    try:
                        l1[i] = round(l1[i], 0)
                    except TypeError:
                        l1[i] = 'N/A'
                csvOut.writerow(l1)

    # Open summarized csvs for use in SQL join
    # Creates the database.
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    with open('CCA_All_{}_blockgroup_Summarized.csv'.format(year), 'rb') as rBG:
        sqlCsvBG = csv.reader(rBG)
        csvSqlPrep(sqlCsvBG, 'sqlBG')

    with open('CCA_All_{}_tract_Summarized.csv'.format(year), 'rb') as rTR:
        sqlCsvTR = csv.reader(rTR)
        csvSqlPrep(sqlCsvTR, 'sqlTR')

    # Creates output csv file
    with open(r'ACS{}_selVariables_no_medians_CCA.csv'.format(year), 'wb') as w_CDSagg:
        ccaCDS_jn = csv.writer(w_CDSagg)
        ccaCDS_jn.writerow(('CCA', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_NONFAM_HH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'HA_AFT2000', 'HA_70_00', 'HA_40_70', 'HA_BEF1940', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'OWNCST_OV30PCT', 'RNTCST_OV30PCT', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT'))

        # Join tables based on geoid
        cursor.execute('SELECT sqlBG.CCA,sqlBG.TOT_POP,sqlBG.UND19,sqlBG.A20_34,sqlBG.A35_49,sqlBG.A50_64,sqlBG.A65_74,sqlBG.A75_84,sqlBG.OV85,sqlBG.WHITE,sqlBG.HISP,sqlBG.BLACK,sqlBG.ASIAN,sqlBG.OTHER,sqlBG.POP_HH,sqlBG.CT_SP_WCHILD,sqlBG.CT_1PHH,sqlBG.CT_2PHH,sqlBG.CT_3PHH,sqlBG.CT_4MPHH,sqlBG.CT_FAM_HH,sqlBG.CT_NONFAM_HH,sqlBG.POP_25OV,sqlBG.LT_HS,sqlBG.HS,sqlBG.SOME_COLL,sqlBG.ASSOC,sqlBG.BACH,sqlBG.GRAD_PROF,sqlBG.INC_LT_25K,sqlBG.INC_25_50K,sqlBG.INC_50_75K,sqlBG.INC_75_100K,sqlBG.INC_100_150K,sqlBG.INC_GT_150,sqlBG.TOT_HH,sqlBG.OWN_OCC_HU,sqlBG.RENT_OCC_HU,sqlBG.VAC_HU,sqlBG.HU_TOT,sqlBG.HU_SNG_DET,sqlBG.HU_SNG_ATT,sqlBG.HU_2UN,sqlBG.HU_3_4UN,sqlBG.HU_GT_5UN,sqlBG.HA_AFT2000,sqlBG.HA_70_00,sqlBG.HA_40_70,sqlBG.HA_BEF1940,sqlBG.BR_0_1,sqlBG.BR_2,sqlBG.BR_3,sqlBG.BR_4,sqlBG.BR_5,sqlBG.HV_LT_150K,sqlBG.HV_150_300K,sqlBG.HV_300_500K,sqlBG.HV_GT_500K,sqlBG.OWNCST_OV30PCT,sqlBG.RNTCST_OV30PCT,sqlTR.POP_16OV,sqlTR.IN_LBFRC,sqlTR.EMP,sqlTR.UNEMP,sqlTR.NOT_IN_LBFRC,sqlTR.WORK_AT_HOME,sqlTR.TOT_COMM,sqlTR.DROVE_AL,sqlTR.CARPOOL,sqlTR.TRANSIT,sqlTR.WALK_BIKE,sqlTR.COMM_OTHER,sqlTR.AGG_TT,sqlTR.NO_VEH,sqlTR.ONE_VEH,sqlTR.TWO_VEH,sqlTR.THREEOM_VEH,sqlTR.ENGLISH,sqlTR.SPANISH,sqlTR.SLAVIC,sqlTR.CHINESE,sqlTR.TAGALOG,sqlTR.ARABIC,sqlTR.KOREAN,sqlTR.OTHER_ASIAN,sqlTR.OTHER_EURO,sqlTR.OTHER_UNSPEC,sqlTR.NATIVE,sqlTR.FOR_BORN,sqlTR.POP_OV5,sqlTR.ONLY_ENGLISH,sqlTR.NOT_ENGLISH,sqlTR.LING_ISO,sqlTR.HCUND20K,sqlTR.HCUND20K_LT20PCT,sqlTR.HCUND20K_20_29PCT,sqlTR.HCUND20K_30MPCT,sqlTR.HC20Kto49K,sqlTR.HC20Kto49K_LT20PCT,sqlTR.HC20Kto49K_20_29PCT,sqlTR.HC20Kto49K_30MPCT,sqlTR.HC50Kto75K,sqlTR.HC50Kto75K_LT20PCT,sqlTR.HC50Kto75K_20_29PCT,sqlTR.HC50Kto75K_30MPCT,sqlTR.HCOV75K,sqlTR.HCOV75K_LT20PCT,sqlTR.HCOV75K_20_29PCT,sqlTR.HCOV75K_30MPCT FROM sqlBG INNER JOIN sqlTR ON (sqlBG.CCA =  sqlTR.CCA)')
        for i in cursor:
            i = list(i)
            ccaCDS_jn.writerow(i)

    print('CCA counts complete.')

    # Defines blockgroup geography.
    geog = 'blockgroup'
    geogAbbr = 'BLGP'

    # Writes temp CSVs for calculating CCA medians.
    with open('CCA_MedianCalc_Age_{}_{}_raw.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'A_Und5', 'A_5_10', 'A_10_15', 'A_15_18', 'A_19', 'A_20', 'A_21', 'A_22_25', 'A_25_30', 'A_30_35', 'A_35_40', 'A_40_45', 'A_45_50', 'A_50_55', 'A_55_60', 'A_60_62', 'A_62_65', 'A_65_67', 'A_67_70', 'A_70_75', 'A_75_80', 'A_80_85', 'A_OV85'))
        with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsAge), 'rb') as rAgeFile:
            csvAgeInp = csv.reader(rAgeFile)
            csvAgeFields = csvAgeInp.next()
            for row in csvAgeInp:
                l1 = listBuild(23)
                l1[0] = row[csvAgeFields.index('geogkey')]
                l1[1] = varSum(row, csvAgeFields, ['B01001e3', 'B01001e27'])
                l1[2] = varSum(row, csvAgeFields, ['B01001e4', 'B01001e28'])
                l1[3] = varSum(row, csvAgeFields, ['B01001e5', 'B01001e29'])
                l1[4] = varSum(row, csvAgeFields, ['B01001e6', 'B01001e30'])
                l1[5] = varSum(row, csvAgeFields, ['B01001e7', 'B01001e31'])
                l1[6] = varSum(row, csvAgeFields, ['B01001e8', 'B01001e32'])
                l1[7] = varSum(row, csvAgeFields, ['B01001e9', 'B01001e33'])
                l1[8] = varSum(row, csvAgeFields, ['B01001e10', 'B01001e34'])
                l1[9] = varSum(row, csvAgeFields, ['B01001e11', 'B01001e35'])
                l1[10] = varSum(row, csvAgeFields, ['B01001e12', 'B01001e36'])
                l1[11] = varSum(row, csvAgeFields, ['B01001e13', 'B01001e37'])
                l1[12] = varSum(row, csvAgeFields, ['B01001e14', 'B01001e38'])
                l1[13] = varSum(row, csvAgeFields, ['B01001e15', 'B01001e39'])
                l1[14] = varSum(row, csvAgeFields, ['B01001e16', 'B01001e40'])
                l1[15] = varSum(row, csvAgeFields, ['B01001e17', 'B01001e41'])
                l1[16] = varSum(row, csvAgeFields, ['B01001e18', 'B01001e42'])
                l1[17] = varSum(row, csvAgeFields, ['B01001e19', 'B01001e43'])
                l1[18] = varSum(row, csvAgeFields, ['B01001e20', 'B01001e44'])
                l1[19] = varSum(row, csvAgeFields, ['B01001e21', 'B01001e45'])
                l1[20] = varSum(row, csvAgeFields, ['B01001e22', 'B01001e46'])
                l1[21] = varSum(row, csvAgeFields, ['B01001e23', 'B01001e47'])
                l1[22] = varSum(row, csvAgeFields, ['B01001e24', 'B01001e48'])
                l1[23] = varSum(row, csvAgeFields, ['B01001e25', 'B01001e49'])
                csvOut.writerow(l1)

    with open('CCA_MedianCalc_Inc_{}_{}_raw.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'INC_LT10000', 'INC_10_15000', 'INC_15_20000', 'INC_20_25000', 'INC_25_30000', 'INC_30_35000', 'INC_35_40000', 'INC_40_45000', 'INC_45_50000', 'INC_50_60000', 'INC_60_75000', 'INC_75_100000', 'INC_100_125000', 'INC_125_150000', 'INC_150_200000', 'INC_OV200000'))
        with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsInc), 'rb') as rIncFile:
            csvIncInp = csv.reader(rIncFile)
            csvIncFields = csvIncInp.next()
            for row in csvIncInp:
                l1 = listBuild(16)
                l1[0] = row[csvIncFields.index('geogkey')]
                l1[1] = varSum(row, csvIncFields, ['B19001e2'])
                l1[2] = varSum(row, csvIncFields, ['B19001e3'])
                l1[3] = varSum(row, csvIncFields, ['B19001e4'])
                l1[4] = varSum(row, csvIncFields, ['B19001e5'])
                l1[5] = varSum(row, csvIncFields, ['B19001e6'])
                l1[6] = varSum(row, csvIncFields, ['B19001e7'])
                l1[7] = varSum(row, csvIncFields, ['B19001e8'])
                l1[8] = varSum(row, csvIncFields, ['B19001e9'])
                l1[9] = varSum(row, csvIncFields, ['B19001e10'])
                l1[10] = varSum(row, csvIncFields, ['B19001e11'])
                l1[11] = varSum(row, csvIncFields, ['B19001e12'])
                l1[12] = varSum(row, csvIncFields, ['B19001e13'])
                l1[13] = varSum(row, csvIncFields, ['B19001e14'])
                l1[14] = varSum(row, csvIncFields, ['B19001e15'])
                l1[15] = varSum(row, csvIncFields, ['B19001e16'])
                l1[16] = varSum(row, csvIncFields, ['B19001e17'])
                csvOut.writerow(l1)

    with open('CCA_MedianCalc_BR_{}_{}_raw.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'R_1', 'R_2', 'R_3', 'R_4', 'R_5', 'R_6', 'R_7', 'R_8', 'R_OV9'))
        with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHUType), 'rb') as rBRFile:
            csvBRInp = csv.reader(rBRFile)
            csvBRFields = csvBRInp.next()
            for row in csvBRInp:
                l1 = listBuild(9)
                l1[0] = row[csvBRFields.index('geogkey')]
                l1[1] = varSum(row, csvBRFields, ['B25017e2'])
                l1[2] = varSum(row, csvBRFields, ['B25017e3'])
                l1[3] = varSum(row, csvBRFields, ['B25017e4'])
                l1[4] = varSum(row, csvBRFields, ['B25017e5'])
                l1[5] = varSum(row, csvBRFields, ['B25017e6'])
                l1[6] = varSum(row, csvBRFields, ['B25017e7'])
                l1[7] = varSum(row, csvBRFields, ['B25017e8'])
                l1[8] = varSum(row, csvBRFields, ['B25017e9'])
                l1[9] = varSum(row, csvBRFields, ['B25017e10'])
                csvOut.writerow(l1)

    with open('CCA_MedianCalc_HAge_{}_{}_raw.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'HA_PRE1940', 'HA_1940_50', 'HA_1950_60', 'HA_1960_70', 'HA_1970_80', 'HA_1980_90', 'HA_1990_00', 'HA_2000_10', 'HA_AFT2010'))
        with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHAgeBRVehAv), 'rb') as rHAgeFile:
            csvHAgeInp = csv.reader(rHAgeFile)
            csvHAgeFields = csvHAgeInp.next()
            for row in csvHAgeInp:
                l1 = listBuild(9)
                l1[0] = row[csvHAgeFields.index('geogkey')]
                l1[1] = varSum(row, csvHAgeFields, ['B25034e11'])
                l1[2] = varSum(row, csvHAgeFields, ['B25034e10'])
                l1[3] = varSum(row, csvHAgeFields, ['B25034e9'])
                l1[4] = varSum(row, csvHAgeFields, ['B25034e8'])
                l1[5] = varSum(row, csvHAgeFields, ['B25034e7'])
                l1[6] = varSum(row, csvHAgeFields, ['B25034e6'])
                l1[7] = varSum(row, csvHAgeFields, ['B25034e5'])
                l1[8] = varSum(row, csvHAgeFields, ['B25034e4'])
                l1[9] = varSum(row, csvHAgeFields, ['B25034e3', 'B25034e2'])
                csvOut.writerow(l1)

    with open('CCA_MedianCalc_HVal_{}_{}_raw.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'HV_LT10000', 'HV_15000', 'HV_20000', 'HV_25000', 'HV_30000', 'HV_35000', 'HV_40000', 'HV_50000', 'HV_60000', 'HV_70000', 'HV_80000', 'HV_90000', 'HV_100000', 'HV_125000', 'HV_150000', 'HV_175000', 'HV_200000', 'HV_250000', 'HV_300000', 'HV_400000', 'HV_500000', 'HV_750000', 'HV_1000000', 'HV_OV1000000'))
        with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsRntCst), 'rb') as rHValFile:
            csvHValInp = csv.reader(rHValFile)
            csvHValFields = csvHValInp.next()
            for row in csvHValInp:
                l1 = listBuild(24)
                l1[0] = row[csvHValFields.index('geogkey')]
                l1[1] = varSum(row, csvHValFields, ['B25075e2'])
                l1[2] = varSum(row, csvHValFields, ['B25075e3'])
                l1[3] = varSum(row, csvHValFields, ['B25075e4'])
                l1[4] = varSum(row, csvHValFields, ['B25075e5'])
                l1[5] = varSum(row, csvHValFields, ['B25075e6'])
                l1[6] = varSum(row, csvHValFields, ['B25075e7'])
                l1[7] = varSum(row, csvHValFields, ['B25075e8'])
                l1[8] = varSum(row, csvHValFields, ['B25075e9'])
                l1[9] = varSum(row, csvHValFields, ['B25075e10'])
                l1[10] = varSum(row, csvHValFields, ['B25075e11'])
                l1[11] = varSum(row, csvHValFields, ['B25075e12'])
                l1[12] = varSum(row, csvHValFields, ['B25075e13'])
                l1[13] = varSum(row, csvHValFields, ['B25075e14'])
                l1[14] = varSum(row, csvHValFields, ['B25075e15'])
                l1[15] = varSum(row, csvHValFields, ['B25075e16'])
                l1[16] = varSum(row, csvHValFields, ['B25075e17'])
                l1[17] = varSum(row, csvHValFields, ['B25075e18'])
                l1[18] = varSum(row, csvHValFields, ['B25075e19'])
                l1[19] = varSum(row, csvHValFields, ['B25075e20'])
                l1[20] = varSum(row, csvHValFields, ['B25075e21'])
                l1[21] = varSum(row, csvHValFields, ['B25075e22'])
                l1[22] = varSum(row, csvHValFields, ['B25075e23'])
                l1[23] = varSum(row, csvHValFields, ['B25075e24'])
                l1[24] = varSum(row, csvHValFields, ['B25075e25'])
                csvOut.writerow(l1)

    # Open summarized csvs for use in SQL join
    # Creates the database.
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    with open('CCA_MedianCalc_Age_{}_{}_raw.csv'.format(year, geog), 'rb') as rAge:
        sqlCsvAge = csv.reader(rAge)
        csvSqlPrep(sqlCsvAge, 'sqlAge')
    with open('CCA_MedianCalc_Inc_{}_{}_raw.csv'.format(year, geog), 'rb') as rInc:
        sqlCsvInc = csv.reader(rInc)
        csvSqlPrep(sqlCsvInc, 'sqlInc')
    with open('CCA_MedianCalc_BR_{}_{}_raw.csv'.format(year, geog), 'rb') as rBR:
        sqlCsvBR = csv.reader(rBR)
        csvSqlPrep(sqlCsvBR, 'sqlBR')
    with open('CCA_MedianCalc_HAge_{}_{}_raw.csv'.format(year, geog), 'rb') as rHage:
        sqlCsvHage = csv.reader(rHage)
        csvSqlPrep(sqlCsvHage, 'sqlHage')
    with open('CCA_MedianCalc_HVal_{}_{}_raw.csv'.format(year, geog), 'rb') as rHval:
        sqlCsvHval = csv.reader(rHval)
        csvSqlPrep(sqlCsvHval, 'sqlHval')

    # Creates output csv file
    with open(r'CCA_MedianCalc_Joined_{}.csv'.format(year), 'wb') as w_CDSagg:
        ccaCDS_jn = csv.writer(w_CDSagg)
        ccaCDS_jn.writerow(('GEOG', 'A_Und5', 'A_5_10', 'A_10_15', 'A_15_18', 'A_19', 'A_20', 'A_21', 'A_22_25', 'A_25_30', 'A_30_35', 'A_35_40', 'A_40_45', 'A_45_50', 'A_50_55', 'A_55_60', 'A_60_62', 'A_62_65', 'A_65_67', 'A_67_70', 'A_70_75', 'A_75_80', 'A_80_85', 'A_OV85', 'INC_LT10000', 'INC_10_15000', 'INC_15_20000', 'INC_20_25000', 'INC_25_30000', 'INC_30_35000', 'INC_35_40000', 'INC_40_45000', 'INC_45_50000', 'INC_50_60000', 'INC_60_75000', 'INC_75_100000', 'INC_100_125000', 'INC_125_150000', 'INC_150_200000', 'INC_OV200000', 'R_1', 'R_2', 'R_3', 'R_4', 'R_5', 'R_6', 'R_7', 'R_8', 'R_OV9', 'HA_PRE1940', 'HA_1940_50', 'HA_1950_60', 'HA_1960_70', 'HA_1970_80', 'HA_1980_90', 'HA_1990_00', 'HA_2000_10', 'HA_AFT2010', 'HV_LT10000', 'HV_15000', 'HV_20000', 'HV_25000', 'HV_30000', 'HV_35000', 'HV_40000', 'HV_50000', 'HV_60000', 'HV_70000', 'HV_80000', 'HV_90000', 'HV_100000', 'HV_125000', 'HV_150000', 'HV_175000', 'HV_200000', 'HV_250000', 'HV_300000', 'HV_400000', 'HV_500000', 'HV_750000', 'HV_1000000', 'HV_OV1000000'))

        # Join tables based on geoid
        cursor.execute('SELECT sqlAge.GEOG,sqlAge.A_Und5,sqlAge.A_5_10,sqlAge.A_10_15,sqlAge.A_15_18,sqlAge.A_19,sqlAge.A_20,sqlAge.A_21,sqlAge.A_22_25,sqlAge.A_25_30,sqlAge.A_30_35,sqlAge.A_35_40,sqlAge.A_40_45,sqlAge.A_45_50,sqlAge.A_50_55,sqlAge.A_55_60,sqlAge.A_60_62,sqlAge.A_62_65,sqlAge.A_65_67,sqlAge.A_67_70,sqlAge.A_70_75,sqlAge.A_75_80,sqlAge.A_80_85,sqlAge.A_OV85,sqlInc.INC_LT10000,sqlInc.INC_10_15000,sqlInc.INC_15_20000,sqlInc.INC_20_25000,sqlInc.INC_25_30000,sqlInc.INC_30_35000,sqlInc.INC_35_40000,sqlInc.INC_40_45000,sqlInc.INC_45_50000,sqlInc.INC_50_60000,sqlInc.INC_60_75000,sqlInc.INC_75_100000,sqlInc.INC_100_125000,sqlInc.INC_125_150000,sqlInc.INC_150_200000,sqlInc.INC_OV200000,sqlBR.R_1,sqlBR.R_2,sqlBR.R_3,sqlBR.R_4,sqlBR.R_5,sqlBR.R_6,sqlBR.R_7,sqlBR.R_8,sqlBR.R_OV9,sqlHage.HA_PRE1940,sqlHage.HA_1940_50,sqlHage.HA_1950_60,sqlHage.HA_1960_70,sqlHage.HA_1970_80,sqlHage.HA_1980_90,sqlHage.HA_1990_00,sqlHage.HA_2000_10,sqlHage.HA_AFT2010,sqlHval.HV_LT10000,sqlHval.HV_15000,sqlHval.HV_20000,sqlHval.HV_25000,sqlHval.HV_30000,sqlHval.HV_35000,sqlHval.HV_40000,sqlHval.HV_50000,sqlHval.HV_60000,sqlHval.HV_70000,sqlHval.HV_80000,sqlHval.HV_90000,sqlHval.HV_100000,sqlHval.HV_125000,sqlHval.HV_150000,sqlHval.HV_175000,sqlHval.HV_200000,sqlHval.HV_250000,sqlHval.HV_300000,sqlHval.HV_400000,sqlHval.HV_500000,sqlHval.HV_750000,sqlHval.HV_1000000,sqlHval.HV_OV1000000 FROM sqlAge INNER JOIN sqlInc ON (sqlAge.GEOG =  sqlInc.GEOG) INNER JOIN sqlBR ON (sqlAge.GEOG =  sqlBR.GEOG) INNER JOIN sqlHage ON (sqlAge.GEOG =  sqlHage.GEOG) INNER JOIN sqlHval ON (sqlAge.GEOG =  sqlHval.GEOG)')
        for i in cursor:
            i = list(i)
            ccaCDS_jn.writerow(i)

    # Opens BG/TR/CCA ratio crosswalk and loads to list of tuples
    with open('Blocks_to_CCA_BG.csv', 'rb') as rfile:
        rfile.readline()
        crosswalk_list = []
        for row in rfile:
            if row.startswith('17'):
                crosswalk_list.append(tuple(row.strip().split(',')))

    # Allocate tracts to blocks
    with open('CCA_MedianCalc_Joined_{}_{}_Allocated.csv'.format(year, geog), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('CCA', 'A_Und5', 'A_5_10', 'A_10_15', 'A_15_18', 'A_19', 'A_20', 'A_21', 'A_22_25', 'A_25_30', 'A_30_35', 'A_35_40', 'A_40_45', 'A_45_50', 'A_50_55', 'A_55_60', 'A_60_62', 'A_62_65', 'A_65_67', 'A_67_70', 'A_70_75', 'A_75_80', 'A_80_85', 'A_OV85', 'INC_LT10000', 'INC_10_15000', 'INC_15_20000', 'INC_20_25000', 'INC_25_30000', 'INC_30_35000', 'INC_35_40000', 'INC_40_45000', 'INC_45_50000', 'INC_50_60000', 'INC_60_75000', 'INC_75_100000', 'INC_100_125000', 'INC_125_150000', 'INC_150_200000', 'INC_OV200000', 'R_1', 'R_2', 'R_3', 'R_4', 'R_5', 'R_6', 'R_7', 'R_8', 'R_OV9', 'HA_PRE1940', 'HA_1940_50', 'HA_1950_60', 'HA_1960_70', 'HA_1970_80', 'HA_1980_90', 'HA_1990_00', 'HA_2000_10', 'HA_AFT2010', 'HV_LT10000', 'HV_15000', 'HV_20000', 'HV_25000', 'HV_30000', 'HV_35000', 'HV_40000', 'HV_50000', 'HV_60000', 'HV_70000', 'HV_80000', 'HV_90000', 'HV_100000', 'HV_125000', 'HV_150000', 'HV_175000', 'HV_200000', 'HV_250000', 'HV_300000', 'HV_400000', 'HV_500000', 'HV_750000', 'HV_1000000', 'HV_OV1000000'))
        with open(r'CCA_MedianCalc_Joined_{}.csv'.format(year), 'rb') as rAll:
            csvAllInp = csv.reader(rAll)
            csvAllFields = csvAllInp.next()
            for BLOCK, BLOCKGROUP, CCA, BG_POP_RAT, BG_HH_RAT, BG_HU_RAT in crosswalk_list:
                l1 = listBuild(81)
                for row in csvAllInp:
                    if row[csvAllFields.index('GEOG')] == BLOCKGROUP:
                        l1[0] = CCA
                        l1[1] = varSum(row, csvAllFields, ['A_Und5']) * float(BG_POP_RAT)
                        l1[2] = varSum(row, csvAllFields, ['A_5_10']) * float(BG_POP_RAT)
                        l1[3] = varSum(row, csvAllFields, ['A_10_15']) * float(BG_POP_RAT)
                        l1[4] = varSum(row, csvAllFields, ['A_15_18']) * float(BG_POP_RAT)
                        l1[5] = varSum(row, csvAllFields, ['A_19']) * float(BG_POP_RAT)
                        l1[6] = varSum(row, csvAllFields, ['A_20']) * float(BG_POP_RAT)
                        l1[7] = varSum(row, csvAllFields, ['A_21']) * float(BG_POP_RAT)
                        l1[8] = varSum(row, csvAllFields, ['A_22_25']) * float(BG_POP_RAT)
                        l1[9] = varSum(row, csvAllFields, ['A_25_30']) * float(BG_POP_RAT)
                        l1[10] = varSum(row, csvAllFields, ['A_30_35']) * float(BG_POP_RAT)
                        l1[11] = varSum(row, csvAllFields, ['A_35_40']) * float(BG_POP_RAT)
                        l1[12] = varSum(row, csvAllFields, ['A_40_45']) * float(BG_POP_RAT)
                        l1[13] = varSum(row, csvAllFields, ['A_45_50']) * float(BG_POP_RAT)
                        l1[14] = varSum(row, csvAllFields, ['A_50_55']) * float(BG_POP_RAT)
                        l1[15] = varSum(row, csvAllFields, ['A_55_60']) * float(BG_POP_RAT)
                        l1[16] = varSum(row, csvAllFields, ['A_60_62']) * float(BG_POP_RAT)
                        l1[17] = varSum(row, csvAllFields, ['A_62_65']) * float(BG_POP_RAT)
                        l1[18] = varSum(row, csvAllFields, ['A_65_67']) * float(BG_POP_RAT)
                        l1[19] = varSum(row, csvAllFields, ['A_67_70']) * float(BG_POP_RAT)
                        l1[20] = varSum(row, csvAllFields, ['A_70_75']) * float(BG_POP_RAT)
                        l1[21] = varSum(row, csvAllFields, ['A_75_80']) * float(BG_POP_RAT)
                        l1[22] = varSum(row, csvAllFields, ['A_80_85']) * float(BG_POP_RAT)
                        l1[23] = varSum(row, csvAllFields, ['A_OV85']) * float(BG_POP_RAT)
                        l1[24] = varSum(row, csvAllFields, ['INC_LT10000']) * float(BG_HH_RAT)
                        l1[25] = varSum(row, csvAllFields, ['INC_10_15000']) * float(BG_HH_RAT)
                        l1[26] = varSum(row, csvAllFields, ['INC_15_20000']) * float(BG_HH_RAT)
                        l1[27] = varSum(row, csvAllFields, ['INC_20_25000']) * float(BG_HH_RAT)
                        l1[28] = varSum(row, csvAllFields, ['INC_25_30000']) * float(BG_HH_RAT)
                        l1[29] = varSum(row, csvAllFields, ['INC_30_35000']) * float(BG_HH_RAT)
                        l1[30] = varSum(row, csvAllFields, ['INC_35_40000']) * float(BG_HH_RAT)
                        l1[31] = varSum(row, csvAllFields, ['INC_40_45000']) * float(BG_HH_RAT)
                        l1[32] = varSum(row, csvAllFields, ['INC_45_50000']) * float(BG_HH_RAT)
                        l1[33] = varSum(row, csvAllFields, ['INC_50_60000']) * float(BG_HH_RAT)
                        l1[34] = varSum(row, csvAllFields, ['INC_60_75000']) * float(BG_HH_RAT)
                        l1[35] = varSum(row, csvAllFields, ['INC_75_100000']) * float(BG_HH_RAT)
                        l1[36] = varSum(row, csvAllFields, ['INC_100_125000']) * float(BG_HH_RAT)
                        l1[37] = varSum(row, csvAllFields, ['INC_125_150000']) * float(BG_HH_RAT)
                        l1[38] = varSum(row, csvAllFields, ['INC_150_200000']) * float(BG_HH_RAT)
                        l1[39] = varSum(row, csvAllFields, ['INC_OV200000']) * float(BG_HH_RAT)
                        l1[40] = varSum(row, csvAllFields, ['R_1']) * float(BG_HU_RAT)
                        l1[41] = varSum(row, csvAllFields, ['R_2']) * float(BG_HU_RAT)
                        l1[42] = varSum(row, csvAllFields, ['R_3']) * float(BG_HU_RAT)
                        l1[43] = varSum(row, csvAllFields, ['R_4']) * float(BG_HU_RAT)
                        l1[44] = varSum(row, csvAllFields, ['R_5']) * float(BG_HU_RAT)
                        l1[45] = varSum(row, csvAllFields, ['R_6']) * float(BG_HU_RAT)
                        l1[46] = varSum(row, csvAllFields, ['R_7']) * float(BG_HU_RAT)
                        l1[47] = varSum(row, csvAllFields, ['R_8']) * float(BG_HU_RAT)
                        l1[48] = varSum(row, csvAllFields, ['R_OV9']) * float(BG_HU_RAT)
                        l1[49] = varSum(row, csvAllFields, ['HA_PRE1940']) * float(BG_HU_RAT)
                        l1[50] = varSum(row, csvAllFields, ['HA_1940_50']) * float(BG_HU_RAT)
                        l1[51] = varSum(row, csvAllFields, ['HA_1950_60']) * float(BG_HU_RAT)
                        l1[52] = varSum(row, csvAllFields, ['HA_1960_70']) * float(BG_HU_RAT)
                        l1[53] = varSum(row, csvAllFields, ['HA_1970_80']) * float(BG_HU_RAT)
                        l1[54] = varSum(row, csvAllFields, ['HA_1980_90']) * float(BG_HU_RAT)
                        l1[55] = varSum(row, csvAllFields, ['HA_1990_00']) * float(BG_HU_RAT)
                        l1[56] = varSum(row, csvAllFields, ['HA_2000_10']) * float(BG_HU_RAT)
                        l1[57] = varSum(row, csvAllFields, ['HA_AFT2010']) * float(BG_HU_RAT)
                        l1[58] = varSum(row, csvAllFields, ['HV_LT10000']) * float(BG_HH_RAT)
                        l1[59] = varSum(row, csvAllFields, ['HV_15000']) * float(BG_HH_RAT)
                        l1[60] = varSum(row, csvAllFields, ['HV_20000']) * float(BG_HH_RAT)
                        l1[61] = varSum(row, csvAllFields, ['HV_25000']) * float(BG_HH_RAT)
                        l1[62] = varSum(row, csvAllFields, ['HV_30000']) * float(BG_HH_RAT)
                        l1[63] = varSum(row, csvAllFields, ['HV_35000']) * float(BG_HH_RAT)
                        l1[64] = varSum(row, csvAllFields, ['HV_40000']) * float(BG_HH_RAT)
                        l1[65] = varSum(row, csvAllFields, ['HV_50000']) * float(BG_HH_RAT)
                        l1[66] = varSum(row, csvAllFields, ['HV_60000']) * float(BG_HH_RAT)
                        l1[67] = varSum(row, csvAllFields, ['HV_70000']) * float(BG_HH_RAT)
                        l1[68] = varSum(row, csvAllFields, ['HV_80000']) * float(BG_HH_RAT)
                        l1[69] = varSum(row, csvAllFields, ['HV_90000']) * float(BG_HH_RAT)
                        l1[70] = varSum(row, csvAllFields, ['HV_100000']) * float(BG_HH_RAT)
                        l1[71] = varSum(row, csvAllFields, ['HV_125000']) * float(BG_HH_RAT)
                        l1[72] = varSum(row, csvAllFields, ['HV_150000']) * float(BG_HH_RAT)
                        l1[73] = varSum(row, csvAllFields, ['HV_175000']) * float(BG_HH_RAT)
                        l1[74] = varSum(row, csvAllFields, ['HV_200000']) * float(BG_HH_RAT)
                        l1[75] = varSum(row, csvAllFields, ['HV_250000']) * float(BG_HH_RAT)
                        l1[76] = varSum(row, csvAllFields, ['HV_300000']) * float(BG_HH_RAT)
                        l1[77] = varSum(row, csvAllFields, ['HV_400000']) * float(BG_HH_RAT)
                        l1[78] = varSum(row, csvAllFields, ['HV_500000']) * float(BG_HH_RAT)
                        l1[79] = varSum(row, csvAllFields, ['HV_750000']) * float(BG_HH_RAT)
                        l1[80] = varSum(row, csvAllFields, ['HV_1000000']) * float(BG_HH_RAT)
                        l1[81] = varSum(row, csvAllFields, ['HV_OV1000000']) * float(BG_HH_RAT)
                        csvOut.writerow(l1)
                        break
                    else:
                        pass
                rAll.seek(0)

    # Summarizes filtered csvs by CCA
    with open('CCA_MedianCalc_Joined_{}_{}_Allocated.csv'.format(year, geog), 'rb') as rfile:
        csvInp = csv.reader(rfile)
        csvAllFields = csvInp.next()
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'wb') as wfile:
            csvOut = csv.writer(wfile)
            csvOut.writerow(('CCA', 'A_Und5', 'A_5_10', 'A_10_15', 'A_15_18', 'A_19', 'A_20', 'A_21', 'A_22_25', 'A_25_30', 'A_30_35', 'A_35_40', 'A_40_45', 'A_45_50', 'A_50_55', 'A_55_60', 'A_60_62', 'A_62_65', 'A_65_67', 'A_67_70', 'A_70_75', 'A_75_80', 'A_80_85', 'A_OV85', 'INC_LT10000', 'INC_10_15000', 'INC_15_20000', 'INC_20_25000', 'INC_25_30000', 'INC_30_35000', 'INC_35_40000', 'INC_40_45000', 'INC_45_50000', 'INC_50_60000', 'INC_60_75000', 'INC_75_100000', 'INC_100_125000', 'INC_125_150000', 'INC_150_200000', 'INC_OV200000', 'R_1', 'R_2', 'R_3', 'R_4', 'R_5', 'R_6', 'R_7', 'R_8', 'R_OV9', 'HA_PRE1940', 'HA_1940_50', 'HA_1950_60', 'HA_1960_70', 'HA_1970_80', 'HA_1980_90', 'HA_1990_00', 'HA_2000_10', 'HA_AFT2010', 'HV_LT10000', 'HV_15000', 'HV_20000', 'HV_25000', 'HV_30000', 'HV_35000', 'HV_40000', 'HV_50000', 'HV_60000', 'HV_70000', 'HV_80000', 'HV_90000', 'HV_100000', 'HV_125000', 'HV_150000', 'HV_175000', 'HV_200000', 'HV_250000', 'HV_300000', 'HV_400000', 'HV_500000', 'HV_750000', 'HV_1000000', 'HV_OV1000000'))
            for cca in cca_list:
                l1 = listBuild(81)
                l1[0] = cca
                for row in csvInp:
                    if row[0] == cca:
                        l1[1] += varSum(row, csvAllFields, ['A_Und5'])
                        l1[2] += varSum(row, csvAllFields, ['A_5_10'])
                        l1[3] += varSum(row, csvAllFields, ['A_10_15'])
                        l1[4] += varSum(row, csvAllFields, ['A_15_18'])
                        l1[5] += varSum(row, csvAllFields, ['A_19'])
                        l1[6] += varSum(row, csvAllFields, ['A_20'])
                        l1[7] += varSum(row, csvAllFields, ['A_21'])
                        l1[8] += varSum(row, csvAllFields, ['A_22_25'])
                        l1[9] += varSum(row, csvAllFields, ['A_25_30'])
                        l1[10] += varSum(row, csvAllFields, ['A_30_35'])
                        l1[11] += varSum(row, csvAllFields, ['A_35_40'])
                        l1[12] += varSum(row, csvAllFields, ['A_40_45'])
                        l1[13] += varSum(row, csvAllFields, ['A_45_50'])
                        l1[14] += varSum(row, csvAllFields, ['A_50_55'])
                        l1[15] += varSum(row, csvAllFields, ['A_55_60'])
                        l1[16] += varSum(row, csvAllFields, ['A_60_62'])
                        l1[17] += varSum(row, csvAllFields, ['A_62_65'])
                        l1[18] += varSum(row, csvAllFields, ['A_65_67'])
                        l1[19] += varSum(row, csvAllFields, ['A_67_70'])
                        l1[20] += varSum(row, csvAllFields, ['A_70_75'])
                        l1[21] += varSum(row, csvAllFields, ['A_75_80'])
                        l1[22] += varSum(row, csvAllFields, ['A_80_85'])
                        l1[23] += varSum(row, csvAllFields, ['A_OV85'])
                        l1[24] += varSum(row, csvAllFields, ['INC_LT10000'])
                        l1[25] += varSum(row, csvAllFields, ['INC_10_15000'])
                        l1[26] += varSum(row, csvAllFields, ['INC_15_20000'])
                        l1[27] += varSum(row, csvAllFields, ['INC_20_25000'])
                        l1[28] += varSum(row, csvAllFields, ['INC_25_30000'])
                        l1[29] += varSum(row, csvAllFields, ['INC_30_35000'])
                        l1[30] += varSum(row, csvAllFields, ['INC_35_40000'])
                        l1[31] += varSum(row, csvAllFields, ['INC_40_45000'])
                        l1[32] += varSum(row, csvAllFields, ['INC_45_50000'])
                        l1[33] += varSum(row, csvAllFields, ['INC_50_60000'])
                        l1[34] += varSum(row, csvAllFields, ['INC_60_75000'])
                        l1[35] += varSum(row, csvAllFields, ['INC_75_100000'])
                        l1[36] += varSum(row, csvAllFields, ['INC_100_125000'])
                        l1[37] += varSum(row, csvAllFields, ['INC_125_150000'])
                        l1[38] += varSum(row, csvAllFields, ['INC_150_200000'])
                        l1[39] += varSum(row, csvAllFields, ['INC_OV200000'])
                        l1[40] += varSum(row, csvAllFields, ['R_1'])
                        l1[41] += varSum(row, csvAllFields, ['R_2'])
                        l1[42] += varSum(row, csvAllFields, ['R_3'])
                        l1[43] += varSum(row, csvAllFields, ['R_4'])
                        l1[44] += varSum(row, csvAllFields, ['R_5'])
                        l1[45] += varSum(row, csvAllFields, ['R_6'])
                        l1[46] += varSum(row, csvAllFields, ['R_7'])
                        l1[47] += varSum(row, csvAllFields, ['R_8'])
                        l1[48] += varSum(row, csvAllFields, ['R_OV9'])
                        l1[49] += varSum(row, csvAllFields, ['HA_PRE1940'])
                        l1[50] += varSum(row, csvAllFields, ['HA_1940_50'])
                        l1[51] += varSum(row, csvAllFields, ['HA_1950_60'])
                        l1[52] += varSum(row, csvAllFields, ['HA_1960_70'])
                        l1[53] += varSum(row, csvAllFields, ['HA_1970_80'])
                        l1[54] += varSum(row, csvAllFields, ['HA_1980_90'])
                        l1[55] += varSum(row, csvAllFields, ['HA_1990_00'])
                        l1[56] += varSum(row, csvAllFields, ['HA_2000_10'])
                        l1[57] += varSum(row, csvAllFields, ['HA_AFT2010'])
                        l1[58] += varSum(row, csvAllFields, ['HV_LT10000'])
                        l1[59] += varSum(row, csvAllFields, ['HV_15000'])
                        l1[60] += varSum(row, csvAllFields, ['HV_20000'])
                        l1[61] += varSum(row, csvAllFields, ['HV_25000'])
                        l1[62] += varSum(row, csvAllFields, ['HV_30000'])
                        l1[63] += varSum(row, csvAllFields, ['HV_35000'])
                        l1[64] += varSum(row, csvAllFields, ['HV_40000'])
                        l1[65] += varSum(row, csvAllFields, ['HV_50000'])
                        l1[66] += varSum(row, csvAllFields, ['HV_60000'])
                        l1[67] += varSum(row, csvAllFields, ['HV_70000'])
                        l1[68] += varSum(row, csvAllFields, ['HV_80000'])
                        l1[69] += varSum(row, csvAllFields, ['HV_90000'])
                        l1[70] += varSum(row, csvAllFields, ['HV_100000'])
                        l1[71] += varSum(row, csvAllFields, ['HV_125000'])
                        l1[72] += varSum(row, csvAllFields, ['HV_150000'])
                        l1[73] += varSum(row, csvAllFields, ['HV_175000'])
                        l1[74] += varSum(row, csvAllFields, ['HV_200000'])
                        l1[75] += varSum(row, csvAllFields, ['HV_250000'])
                        l1[76] += varSum(row, csvAllFields, ['HV_300000'])
                        l1[77] += varSum(row, csvAllFields, ['HV_400000'])
                        l1[78] += varSum(row, csvAllFields, ['HV_500000'])
                        l1[79] += varSum(row, csvAllFields, ['HV_750000'])
                        l1[80] += varSum(row, csvAllFields, ['HV_1000000'])
                        l1[81] += varSum(row, csvAllFields, ['HV_OV1000000'])

                # Return to start of input csv
                rfile.seek(0)

                # Rounds to whole number, writes to out csv
                for i in range(1, len(l1)):
                    l1[i] = round(l1[i], 0)
                csvOut.writerow(l1)

    # Median Age Calculation
    # Defines categorical breaks
    binBreakList = [0, 5, 10, 15, 18, 20, 21, 22, 25, 30, 35, 40, 45, 50, 55, 60, 62, 65, 67, 70, 75, 80, 85, 100]

    with open('CCA_MedAge_{}.csv'.format(year), 'wb') as medOut:
        csvOut = csv.writer(medOut)
        csvOut.writerow(('CCA', 'MED_AGE'))
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'rb') as medfile:
            csvMed = csv.reader(medfile)
            csvFields = csvMed.next()
            l1 = listBuild(23)
            for row in csvMed:
                l1[0] = row[csvFields.index('CCA')]
                l1[1] = varSum(row, csvFields, ['A_Und5'])
                l1[2] = varSum(row, csvFields, ['A_5_10'])
                l1[3] = varSum(row, csvFields, ['A_10_15'])
                l1[4] = varSum(row, csvFields, ['A_15_18'])
                l1[5] = varSum(row, csvFields, ['A_19'])
                l1[6] = varSum(row, csvFields, ['A_20'])
                l1[7] = varSum(row, csvFields, ['A_21'])
                l1[8] = varSum(row, csvFields, ['A_22_25'])
                l1[9] = varSum(row, csvFields, ['A_25_30'])
                l1[10] = varSum(row, csvFields, ['A_30_35'])
                l1[11] = varSum(row, csvFields, ['A_35_40'])
                l1[12] = varSum(row, csvFields, ['A_40_45'])
                l1[13] = varSum(row, csvFields, ['A_45_50'])
                l1[14] = varSum(row, csvFields, ['A_50_55'])
                l1[15] = varSum(row, csvFields, ['A_55_60'])
                l1[16] = varSum(row, csvFields, ['A_60_62'])
                l1[17] = varSum(row, csvFields, ['A_62_65'])
                l1[18] = varSum(row, csvFields, ['A_65_67'])
                l1[19] = varSum(row, csvFields, ['A_67_70'])
                l1[20] = varSum(row, csvFields, ['A_70_75'])
                l1[21] = varSum(row, csvFields, ['A_75_80'])
                l1[22] = varSum(row, csvFields, ['A_80_85'])
                l1[23] = varSum(row, csvFields, ['A_OV85'])

                l2 = [l1[0], medianCalc(binBreakList, l1[1:])]
                csvOut.writerow(l2)

    # Median Income Calculation
    # Defines categorical breaks
    binBreakList = [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 75000, 100000, 125000, 150000, 200000, 1000000]

    # Creates list with counts by category
    with open('CCA_MedInc_{}.csv'.format(year), 'wb') as medOut:
        csvOut = csv.writer(medOut)
        csvOut.writerow(('CCA', 'MED_INC'))
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'rb') as medfile:
            csvMed = csv.reader(medfile)
            csvFields = csvMed.next()
            l1 = listBuild(16)
            for row in csvMed:
                l1[0] = row[csvFields.index('CCA')]
                l1[1] = varSum(row, csvFields, ['INC_LT10000'])
                l1[2] = varSum(row, csvFields, ['INC_10_15000'])
                l1[3] = varSum(row, csvFields, ['INC_15_20000'])
                l1[4] = varSum(row, csvFields, ['INC_20_25000'])
                l1[5] = varSum(row, csvFields, ['INC_25_30000'])
                l1[6] = varSum(row, csvFields, ['INC_30_35000'])
                l1[7] = varSum(row, csvFields, ['INC_35_40000'])
                l1[8] = varSum(row, csvFields, ['INC_40_45000'])
                l1[9] = varSum(row, csvFields, ['INC_45_50000'])
                l1[10] = varSum(row, csvFields, ['INC_50_60000'])
                l1[11] = varSum(row, csvFields, ['INC_60_75000'])
                l1[12] = varSum(row, csvFields, ['INC_75_100000'])
                l1[13] = varSum(row, csvFields, ['INC_100_125000'])
                l1[14] = varSum(row, csvFields, ['INC_125_150000'])
                l1[15] = varSum(row, csvFields, ['INC_150_200000'])
                l1[16] = varSum(row, csvFields, ['INC_OV200000'])

                l2 = [l1[0], medianCalc(binBreakList, l1[1:])]
                csvOut.writerow(l2)

    # Median Rooms Calculation
    # Defines categorical breaks
    binBreakList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 20]

    # Creates list with counts by category
    with open('CCA_MedRooms_{}.csv'.format(year), 'wb') as medOut:
        csvOut = csv.writer(medOut)
        csvOut.writerow(('CCA', 'MED_ROOMS'))
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'rb') as medfile:
            csvMed = csv.reader(medfile)
            csvAllFields = csvMed.next()
            l1 = listBuild(9)
            for row in csvMed:
                l1[0] = row[csvFields.index('CCA')]
                l1[1] = varSum(row, csvAllFields, ['R_1'])
                l1[2] = varSum(row, csvAllFields, ['R_2'])
                l1[3] = varSum(row, csvAllFields, ['R_3'])
                l1[4] = varSum(row, csvAllFields, ['R_4'])
                l1[5] = varSum(row, csvAllFields, ['R_5'])
                l1[6] = varSum(row, csvAllFields, ['R_6'])
                l1[7] = varSum(row, csvAllFields, ['R_7'])
                l1[8] = varSum(row, csvAllFields, ['R_8'])
                l1[9] = varSum(row, csvAllFields, ['R_OV9'])

                l2 = [l1[0], medianCalc(binBreakList, l1[1:])]
                csvOut.writerow(l2)


    # Median H Age Calculation
    # Defines categorical breaks
    binBreakList = [1850, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2015]

    # Creates list with counts by category.
    with open('CCA_MedHAge_{}.csv'.format(year), 'wb') as medOut:
        csvOut = csv.writer(medOut)
        csvOut.writerow(('CCA', 'MED_HA'))
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'rb') as medfile:
            csvMed = csv.reader(medfile)
            csvAllFields = csvMed.next()
            l1 = listBuild(9)
            for row in csvMed:
                l1[0] = row[csvFields.index('CCA')]
                l1[1] = varSum(row, csvAllFields, ['HA_PRE1940'])
                l1[2] = varSum(row, csvAllFields, ['HA_1940_50'])
                l1[3] = varSum(row, csvAllFields, ['HA_1950_60'])
                l1[4] = varSum(row, csvAllFields, ['HA_1960_70'])
                l1[5] = varSum(row, csvAllFields, ['HA_1970_80'])
                l1[6] = varSum(row, csvAllFields, ['HA_1980_90'])
                l1[7] = varSum(row, csvAllFields, ['HA_1990_00'])
                l1[8] = varSum(row, csvAllFields, ['HA_2000_10'])
                l1[9] = varSum(row, csvAllFields, ['HA_AFT2010'])

                #l2 = [l1[0], medianCalc(binBreakList, l1[1:])]
                # NOTE: since much of Chicago housing was built pre-1940, the estimated medians
                # for certain neighborhoods skew far below 1940 (due to the large range of years
                # in the pre-1940 group), resulting in unreasonable estimates.
                l2 = [l1[0], None]
                csvOut.writerow(l2)


    # Median H Val Calculation
    # Defines categorical breaks
    binBreakList = [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000, 10000000]

    # Creates list with counts by category
    with open('CCA_MedHVal_{}.csv'.format(year), 'wb') as medOut:
        csvOut = csv.writer(medOut)
        csvOut.writerow(('CCA', 'MED_HV'))
        with open('CCA_MedianCalc_{}_{}_Summarized.csv'.format(year, geog), 'rb') as medfile:
            csvMed = csv.reader(medfile)
            csvAllFields = csvMed.next()
            l1 = listBuild(24)
            for row in csvMed:
                l1[0] = row[csvFields.index('CCA')]
                l1[1] = varSum(row, csvAllFields, ['HV_LT10000'])
                l1[2] = varSum(row, csvAllFields, ['HV_15000'])
                l1[3] = varSum(row, csvAllFields, ['HV_20000'])
                l1[4] = varSum(row, csvAllFields, ['HV_25000'])
                l1[5] = varSum(row, csvAllFields, ['HV_30000'])
                l1[6] = varSum(row, csvAllFields, ['HV_35000'])
                l1[7] = varSum(row, csvAllFields, ['HV_40000'])
                l1[8] = varSum(row, csvAllFields, ['HV_50000'])
                l1[9] = varSum(row, csvAllFields, ['HV_60000'])
                l1[10] = varSum(row, csvAllFields, ['HV_70000'])
                l1[11] = varSum(row, csvAllFields, ['HV_80000'])
                l1[12] = varSum(row, csvAllFields, ['HV_90000'])
                l1[13] = varSum(row, csvAllFields, ['HV_100000'])
                l1[14] = varSum(row, csvAllFields, ['HV_125000'])
                l1[15] = varSum(row, csvAllFields, ['HV_150000'])
                l1[16] = varSum(row, csvAllFields, ['HV_175000'])
                l1[17] = varSum(row, csvAllFields, ['HV_200000'])
                l1[18] = varSum(row, csvAllFields, ['HV_250000'])
                l1[19] = varSum(row, csvAllFields, ['HV_300000'])
                l1[20] = varSum(row, csvAllFields, ['HV_400000'])
                l1[21] = varSum(row, csvAllFields, ['HV_500000'])
                l1[22] = varSum(row, csvAllFields, ['HV_750000'])
                l1[23] = varSum(row, csvAllFields, ['HV_1000000'])
                l1[24] = varSum(row, csvAllFields, ['HV_OV1000000'])

                l2 = [l1[0], medianCalc(binBreakList, l1[1:])]
                csvOut.writerow(l2)


    # Open summarized csvs for use in SQL join
    # Creates the database.
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    with open('CCA_MedHVal_{}.csv'.format(year), 'rb') as rHVal:
        sqlCsvHVal = csv.reader(rHVal)
        csvSqlPrep(sqlCsvHVal, 'sqlHVal')

    with open('CCA_MedHAge_{}.csv'.format(year), 'rb') as rHAge:
        sqlCsvHAge = csv.reader(rHAge)
        csvSqlPrep(sqlCsvHAge, 'sqlHAge')

    with open('CCA_MedRooms_{}.csv'.format(year), 'rb') as rRooms:
        sqlCsvRooms= csv.reader(rRooms)
        csvSqlPrep(sqlCsvRooms, 'sqlRooms')

    with open('CCA_MedInc_{}.csv'.format(year), 'rb') as rInc:
        sqlCsvInc = csv.reader(rInc)
        csvSqlPrep(sqlCsvInc, 'sqlInc')

    with open('CCA_MedAge_{}.csv'.format(year), 'rb') as rAge:
        sqlCsvAge = csv.reader(rAge)
        csvSqlPrep(sqlCsvAge, 'sqlAge')

    with open('ACS{}_selVariables_no_medians_CCA.csv'.format(year), 'rb') as rAll:
        sqlCsvAll = csv.reader(rAll)
        csvSqlPrep(sqlCsvAll, 'sqlAll')

    # Creates output csv file
    with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariablesCCA.csv'.format(year), 'wb') as w_ccaMed:
        ccaMed_jn = csv.writer(w_ccaMed)
        ccaMed_jn.writerow(('GEOG', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'MED_AGE', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_NONFAM_HH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'MEDINC', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'HA_AFT2000', 'HA_70_00', 'HA_40_70', 'HA_BEF1940', 'MED_HA', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'MED_ROOMS', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'MED_HV', 'OWNCST_OV30PCT', 'RNTCST_OV30PCT', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT'))

        # Join tables based on geoid
        cursor.execute('SELECT sqlAll.CCA,sqlAll.TOT_POP,sqlAll.UND19,sqlAll.A20_34,sqlAll.A35_49,sqlAll.A50_64,sqlAll.A65_74,sqlAll.A75_84,sqlAll.OV85,sqlAge.MED_AGE,sqlAll.WHITE,sqlAll.HISP,sqlAll.BLACK,sqlAll.ASIAN,sqlAll.OTHER,sqlAll.POP_HH,sqlAll.CT_SP_WCHILD,sqlAll.CT_1PHH,sqlAll.CT_2PHH,sqlAll.CT_3PHH,sqlAll.CT_4MPHH,sqlAll.CT_FAM_HH,sqlAll.CT_NONFAM_HH,sqlAll.POP_25OV,sqlAll.LT_HS,sqlAll.HS,sqlAll.SOME_COLL,sqlAll.ASSOC,sqlAll.BACH,sqlAll.GRAD_PROF,sqlAll.INC_LT_25K,sqlAll.INC_25_50K,sqlAll.INC_50_75K,sqlAll.INC_75_100K,sqlAll.INC_100_150K,sqlAll.INC_GT_150,sqlInc.MED_INC,sqlAll.TOT_HH,sqlAll.OWN_OCC_HU,sqlAll.RENT_OCC_HU,sqlAll.VAC_HU,sqlAll.HU_TOT,sqlAll.HU_SNG_DET,sqlAll.HU_SNG_ATT,sqlAll.HU_2UN,sqlAll.HU_3_4UN,sqlAll.HU_GT_5UN,sqlAll.HA_AFT2000,sqlAll.HA_70_00,sqlAll.HA_40_70,sqlAll.HA_BEF1940,sqlHAge.MED_HA,sqlAll.BR_0_1,sqlAll.BR_2,sqlAll.BR_3,sqlAll.BR_4,sqlAll.BR_5,sqlRooms.MED_ROOMS,sqlAll.HV_LT_150K,sqlAll.HV_150_300K,sqlAll.HV_300_500K,sqlAll.HV_GT_500K,sqlHVal.MED_HV,sqlAll.OWNCST_OV30PCT,sqlAll.RNTCST_OV30PCT,sqlAll.POP_16OV,sqlAll.IN_LBFRC,sqlAll.EMP,sqlAll.UNEMP,sqlAll.NOT_IN_LBFRC,sqlAll.WORK_AT_HOME,sqlAll.TOT_COMM,sqlAll.DROVE_AL,sqlAll.CARPOOL,sqlAll.TRANSIT,sqlAll.WALK_BIKE,sqlAll.COMM_OTHER,sqlAll.AGG_TT,sqlAll.NO_VEH,sqlAll.ONE_VEH,sqlAll.TWO_VEH,sqlAll.THREEOM_VEH,sqlAll.ENGLISH,sqlAll.SPANISH,sqlAll.SLAVIC,sqlAll.CHINESE,sqlAll.TAGALOG,sqlAll.ARABIC,sqlAll.KOREAN,sqlAll.OTHER_ASIAN,sqlAll.OTHER_EURO,sqlAll.OTHER_UNSPEC,sqlAll.NATIVE,sqlAll.FOR_BORN,sqlAll.POP_OV5,sqlAll.ONLY_ENGLISH,sqlAll.NOT_ENGLISH,sqlAll.LING_ISO,sqlAll.HCUND20K,sqlAll.HCUND20K_LT20PCT,sqlAll.HCUND20K_20_29PCT,sqlAll.HCUND20K_30MPCT,sqlAll.HC20Kto49K,sqlAll.HC20Kto49K_LT20PCT,sqlAll.HC20Kto49K_20_29PCT,sqlAll.HC20Kto49K_30MPCT,sqlAll.HC50Kto75K,sqlAll.HC50Kto75K_LT20PCT,sqlAll.HC50Kto75K_20_29PCT,sqlAll.HC50Kto75K_30MPCT,sqlAll.HCOV75K,sqlAll.HCOV75K_LT20PCT,sqlAll.HCOV75K_20_29PCT,sqlAll.HCOV75K_30MPCT FROM sqlAge INNER JOIN sqlInc ON (sqlAge.CCA = sqlInc.CCA) INNER JOIN sqlRooms ON (sqlAge.CCA = sqlRooms.CCA) INNER JOIN sqlHAge ON (sqlAge.CCA = sqlHAge.CCA) INNER JOIN sqlHVal ON (sqlAge.CCA =  sqlHVal.CCA) INNER JOIN sqlAll ON (sqlAge.CCA = sqlAll.CCA)')
        for i in cursor:
            i = list(i)
            ccaMed_jn.writerow(i)

# Deletes intermediate csvs
csv_list = ['CCA_MedRooms_{}.csv'.format(year), 'CCA_MedInc_{}.csv'.format(year), 'CCA_MedRooms_{}.csv'.format(year), 'CCA_MedianCalc_Joined_{}_blockgroup_Allocated.csv'.format(year), 'CCA_MedianCalc_Joined_{}.csv'.format(year), 'CCA_MedianCalc_Inc_{}_blockgroup_raw.csv'.format(year), 'CCA_MedianCalc_HVal_{}_blockgroup_raw.csv'.format(year), 'CCA_MedianCalc_HAge_{}_blockgroup_raw.csv'.format(year), 'CCA_MedianCalc_BR_{}_blockgroup_raw.csv'.format(year), 'CCA_MedianCalc_Age_{}_blockgroup_raw.csv'.format(year), 'CCA_MedianCalc_{}_blockgroup_Summarized.csv'.format(year), 'CCA_MedHVal_{}.csv'.format(year), 'CCA_MedHAge_{}.csv'.format(year), 'CCA_MedAge_{}.csv'.format(year), 'CCA_All_{}_tract_Summarized.csv'.format(year), 'CCA_All_{}_tract_Allocated.csv'.format(year), 'CCA_All_{}_blockgroup_Summarized.csv'.format(year), 'CCA_All_{}_blockgroup_Allocated.csv'.format(year), 'CCA_All_2006_2010_blockgroup_Allocated.csv', 'ACS{}_selVariables_no_medians_CCA.csv'.format(year)]
for csv_file in csv_list:
    try:
        os.remove(csv_file)
    except:
        pass

if cca_proc_flag:
    print('CCA medians complete.')
else:
    print('!!! CCA not run !!!')

# Edit to control the geog level.
geog = 'county'
geogAbbr = 'CNTY'

# Median Age Calculation
# Defines categorical breaks
binBreakList = [0, 5, 10, 15, 18, 20, 21, 22, 25, 30, 35, 40, 45, 50, 55, 60, 62, 65, 67, 70, 75, 80, 85, 100]
l1 = listBuild(23)

# Creates list with counts by category
with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsAge), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    for row in csvInp:
        l1[0] = 'Region'
        l1[1] += varSum(row, csvFields, ['B01001e3', 'B01001e27'])
        l1[2] += varSum(row, csvFields, ['B01001e4', 'B01001e28'])
        l1[3] += varSum(row, csvFields, ['B01001e5', 'B01001e29'])
        l1[4] += varSum(row, csvFields, ['B01001e6', 'B01001e30'])
        l1[5] += varSum(row, csvFields, ['B01001e7', 'B01001e31'])
        l1[6] += varSum(row, csvFields, ['B01001e8', 'B01001e32'])
        l1[7] += varSum(row, csvFields, ['B01001e9', 'B01001e33'])
        l1[8] += varSum(row, csvFields, ['B01001e10', 'B01001e34'])
        l1[9] += varSum(row, csvFields, ['B01001e11', 'B01001e35'])
        l1[10] += varSum(row, csvFields, ['B01001e12', 'B01001e36'])
        l1[11] += varSum(row, csvFields, ['B01001e13', 'B01001e37'])
        l1[12] += varSum(row, csvFields, ['B01001e14', 'B01001e38'])
        l1[13] += varSum(row, csvFields, ['B01001e15', 'B01001e39'])
        l1[14] += varSum(row, csvFields, ['B01001e16', 'B01001e40'])
        l1[15] += varSum(row, csvFields, ['B01001e17', 'B01001e41'])
        l1[16] += varSum(row, csvFields, ['B01001e18', 'B01001e42'])
        l1[17] += varSum(row, csvFields, ['B01001e19', 'B01001e43'])
        l1[18] += varSum(row, csvFields, ['B01001e20', 'B01001e44'])
        l1[19] += varSum(row, csvFields, ['B01001e21', 'B01001e45'])
        l1[20] += varSum(row, csvFields, ['B01001e22', 'B01001e46'])
        l1[21] += varSum(row, csvFields, ['B01001e23', 'B01001e47'])
        l1[22] += varSum(row, csvFields, ['B01001e24', 'B01001e48'])
        l1[23] += varSum(row, csvFields, ['B01001e25', 'B01001e49'])

# Estimates/prints median
reg_med_age = medianCalc(binBreakList, l1[1:])


# Median Income Calculation
# Defines categorical breaks
binBreakList = [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 75000, 100000, 125000, 150000, 200000, 1000000]
l1 = listBuild(16)

# Creates list with counts by category
with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsInc), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    for row in csvInp:
        l1[0] = 'Region'
        l1[1] += varSum(row, csvFields, ['B19001e2'])
        l1[2] += varSum(row, csvFields, ['B19001e3'])
        l1[3] += varSum(row, csvFields, ['B19001e4'])
        l1[4] += varSum(row, csvFields, ['B19001e5'])
        l1[5] += varSum(row, csvFields, ['B19001e6'])
        l1[6] += varSum(row, csvFields, ['B19001e7'])
        l1[7] += varSum(row, csvFields, ['B19001e8'])
        l1[8] += varSum(row, csvFields, ['B19001e9'])
        l1[9] += varSum(row, csvFields, ['B19001e10'])
        l1[10] += varSum(row, csvFields, ['B19001e11'])
        l1[11] += varSum(row, csvFields, ['B19001e12'])
        l1[12] += varSum(row, csvFields, ['B19001e13'])
        l1[13] += varSum(row, csvFields, ['B19001e14'])
        l1[14] += varSum(row, csvFields, ['B19001e15'])
        l1[15] += varSum(row, csvFields, ['B19001e16'])
        l1[16] += varSum(row, csvFields, ['B19001e17'])

# Estimates/prints median
reg_med_inc = medianCalc(binBreakList, l1[1:])

# Median Rooms Calculation
# Defines categorical breaks
binBreakList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 20]
l1 = listBuild(9)

# Creates list with counts by category
with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHUType), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    for row in csvInp:
        l1[0] = 'Region'
        l1[1] += varSum(row, csvFields, ['B25017e2'])
        l1[2] += varSum(row, csvFields, ['B25017e3'])
        l1[3] += varSum(row, csvFields, ['B25017e4'])
        l1[4] += varSum(row, csvFields, ['B25017e5'])
        l1[5] += varSum(row, csvFields, ['B25017e6'])
        l1[6] += varSum(row, csvFields, ['B25017e7'])
        l1[7] += varSum(row, csvFields, ['B25017e8'])
        l1[8] += varSum(row, csvFields, ['B25017e9'])
        l1[9] += varSum(row, csvFields, ['B25017e10'])

# Estimates/prints median
reg_med_rooms = medianCalc(binBreakList, l1[1:])


# Median H Age Calculation
# Defines categorical breaks
binBreakList = [1850, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2016]
l1 = listBuild(9)

# Creates list with counts by category
with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsHAgeBRVehAv), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    for row in csvInp:
        l1[0] = 'Region'
        l1[1] += varSum(row, csvFields, ['B25034e11'])
        l1[2] += varSum(row, csvFields, ['B25034e10'])
        l1[3] += varSum(row, csvFields, ['B25034e9'])
        l1[4] += varSum(row, csvFields, ['B25034e8'])
        l1[5] += varSum(row, csvFields, ['B25034e7'])
        l1[6] += varSum(row, csvFields, ['B25034e6'])
        l1[7] += varSum(row, csvFields, ['B25034e5'])
        l1[8] += varSum(row, csvFields, ['B25034e4'])
        l1[9] += varSum(row, csvFields, ['B25034e3', 'B25034e2'])

# Estimates/prints median
reg_med_ha = medianCalc(binBreakList, l1[1:])


# Median H Val Calculation
# Defines categorical breaks
binBreakList = [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000, 10000000]
l1 = listBuild(24)

# Creates list with counts by category
with open(r'V:\Demographic_and_Forecast\Census\ACS\{}\Data\CMAP\{}\SF{}0{}ile.csv'.format(year, geog, geogAbbr, acsRntCst), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    for row in csvInp:
        l1[0] = 'Region'
        l1[1] += varSum(row, csvFields, ['B25075e2'])
        l1[2] += varSum(row, csvFields, ['B25075e3'])
        l1[3] += varSum(row, csvFields, ['B25075e4'])
        l1[4] += varSum(row, csvFields, ['B25075e5'])
        l1[5] += varSum(row, csvFields, ['B25075e6'])
        l1[6] += varSum(row, csvFields, ['B25075e7'])
        l1[7] += varSum(row, csvFields, ['B25075e8'])
        l1[8] += varSum(row, csvFields, ['B25075e9'])
        l1[9] += varSum(row, csvFields, ['B25075e10'])
        l1[10] += varSum(row, csvFields, ['B25075e11'])
        l1[11] += varSum(row, csvFields, ['B25075e12'])
        l1[12] += varSum(row, csvFields, ['B25075e13'])
        l1[13] += varSum(row, csvFields, ['B25075e14'])
        l1[14] += varSum(row, csvFields, ['B25075e15'])
        l1[15] += varSum(row, csvFields, ['B25075e16'])
        l1[16] += varSum(row, csvFields, ['B25075e17'])
        l1[17] += varSum(row, csvFields, ['B25075e18'])
        l1[18] += varSum(row, csvFields, ['B25075e19'])
        l1[19] += varSum(row, csvFields, ['B25075e20'])
        l1[20] += varSum(row, csvFields, ['B25075e21'])
        l1[21] += varSum(row, csvFields, ['B25075e22'])
        l1[22] += varSum(row, csvFields, ['B25075e23'])
        l1[23] += varSum(row, csvFields, ['B25075e24'])
        l1[24] += varSum(row, csvFields, ['B25075e25'])

# Estimates/prints median
reg_med_hv = medianCalc(binBreakList, l1[1:])

# Writes out regional medians
with open('ACS{}_regional_medians.csv'.format(year), 'wb') as w_ccaMed:
    ccaMed_jn = csv.writer(w_ccaMed)
    ccaMed_jn.writerow(('GEOG', 'MED_AGE', 'MED_ROOMS', 'MEDINC', 'MED_HA', 'MED_HV'))
    ccaMed_jn.writerow(('Region', reg_med_age, reg_med_rooms, reg_med_inc, reg_med_ha, reg_med_hv))

# Summarizes county data to region
with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariablescounty.csv'.format(year), 'rb') as rfile:
    csvInp = csv.reader(rfile)
    try:
        csvFields = csvInp.next()
    except AttributeError:
        csvFields = next(csvInp)
    with open('ACS{}_regional_summary.csv'.format(year), 'wb') as wfile:
        csvOut = csv.writer(wfile)
        csvOut.writerow(('GEOG', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_2PF', 'CT_3PF', 'CT_4PF', 'CT_5PF', 'CT_6PF', 'CT_7MPF', 'CT_NONFAM_HH', 'CT_2PNF', 'CT_3PNF', 'CT_4PNF', 'CT_5PNF', 'CT_6PNF', 'CT_7MPNF', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'INC_LT_45K', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'VAC_IMP', 'VAC_NOT_IMP', 'VAC_FOR_RENT', 'VAC_FOR_SALE', 'VAC_OTHER', 'OWN_1_PERS_HH', 'OWN_2_PERS_HH', 'OWN_3_PERS_HH', 'OWN_4_PERS_HH', 'OWN_5_PERS_HH', 'OWN_6_PERS_HH', 'OWN_7_MORE_HH', 'RENT_1_PERS_HH', 'RENT_2_PERS_HH', 'RENT_3_PERS_HH', 'RENT_4_PERS_HH', 'RENT_5_PERS_HH', 'RENT_6_PERS_HH', 'RENT_7_MORE_HH', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'HU_OWN_1DET', 'HU_OWN_1ATT', 'HU_OWN_2', 'HU_OWN_3_4', 'HU_OWN_5_9', 'HU_OWN_10_19', 'HU_OWN_20_49', 'HU_OWN_50OV', 'HU_OWN_MOB_HOME', 'HU_OWN_OTHER_MOB', 'HU_RENT_1DET', 'HU_RENT_1ATT', 'HU_RENT_2', 'HU_RENT_3_4', 'HU_RENT_5_9', 'HU_RENT_10_19', 'HU_RENT_20_49', 'HU_RENT_50OV', 'HU_RENT_MOB_HOME', 'HU_RENT_OTHER_MOB', 'HA_AFT2000', 'HA_80_00', 'HA_70_00', 'HA_60_80', 'HA_40_70', 'HA_40_60', 'HA_BEF1940', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'AGG_VEH_AVAIL', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'OWNCST_OV30PCT', 'HU_OWN_INC_LT5K', 'HU_OWN_INC_5K_10K', 'HU_OWN_INC_10K_15K', 'HU_OWN_INC_15K_20K', 'HU_OWN_INC_20K_25K', 'HU_OWN_INC_25K_35K', 'HU_OWN_INC_35K_50K', 'HU_OWN_INC_50K_75K', 'HU_OWN_INC_75K_100K', 'HU_OWN_INC_100K_150K', 'HU_OWN_INC_150KOV', 'HU_RENT_INC_LT5K', 'HU_RENT_INC_5K_10K', 'HU_RENT_INC_10K_15K', 'HU_RENT_INC_15K_20K', 'HU_RENT_INC_20K_25K', 'HU_RENT_INC_25K_35K', 'HU_RENT_INC_35K_50K', 'HU_RENT_INC_50K_75K', 'HU_RENT_INC_75K_100K', 'HU_RENT_INC_100K_150K', 'HU_RENT_INC_150KOV', 'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT', 'RNTCST_OV30PCT', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'POV_SURV', 'POV_POP', 'TOT_FAMILIES', 'POV_FAM', 'HH_PUB_ASSIST_OR_FOOD_STAMPS', 'FAM_INC_UND45K', 'POP_CIV_NONINST', 'DISABLED', 'POP_NO_HINS'))
        l1 = listBuild(195)
        l1[0] = 'Region'
        for row in csvInp:
            l1[1] += varSum(row, csvFields, ['TOT_POP'])
            l1[2] += varSum(row, csvFields, ['UND19'])
            l1[3] += varSum(row, csvFields, ['A20_34'])
            l1[4] += varSum(row, csvFields, ['A35_49'])
            l1[5] += varSum(row, csvFields, ['A50_64'])
            l1[6] += varSum(row, csvFields, ['A65_74'])
            l1[7] += varSum(row, csvFields, ['A75_84'])
            l1[8] += varSum(row, csvFields, ['OV85'])
            l1[9] += varSum(row, csvFields, ['WHITE'])
            l1[10] += varSum(row, csvFields, ['HISP'])
            l1[11] += varSum(row, csvFields, ['BLACK'])
            l1[12] += varSum(row, csvFields, ['ASIAN'])
            l1[13] += varSum(row, csvFields, ['OTHER'])
            l1[14] += varSum(row, csvFields, ['POP_HH'])
            l1[15] += varSum(row, csvFields, ['CT_SP_WCHILD'])
            l1[16] += varSum(row, csvFields, ['CT_1PHH'])
            l1[17] += varSum(row, csvFields, ['CT_2PHH'])
            l1[18] += varSum(row, csvFields, ['CT_3PHH'])
            l1[19] += varSum(row, csvFields, ['CT_4MPHH'])
            l1[20] += varSum(row, csvFields, ['CT_FAM_HH'])
            l1[21] += varSum(row, csvFields, ['CT_2PF'])
            l1[22] += varSum(row, csvFields, ['CT_3PF'])
            l1[23] += varSum(row, csvFields, ['CT_4PF'])
            l1[24] += varSum(row, csvFields, ['CT_5PF'])
            l1[25] += varSum(row, csvFields, ['CT_6PF'])
            l1[26] += varSum(row, csvFields, ['CT_7MPF'])
            l1[27] += varSum(row, csvFields, ['CT_NONFAM_HH'])
            l1[28] += varSum(row, csvFields, ['CT_2PNF'])
            l1[29] += varSum(row, csvFields, ['CT_3PNF'])
            l1[30] += varSum(row, csvFields, ['CT_4PNF'])
            l1[31] += varSum(row, csvFields, ['CT_5PNF'])
            l1[32] += varSum(row, csvFields, ['CT_6PNF'])
            l1[33] += varSum(row, csvFields, ['CT_7MPNF'])
            l1[34] += varSum(row, csvFields, ['POP_16OV'])
            l1[35] += varSum(row, csvFields, ['IN_LBFRC'])
            l1[36] += varSum(row, csvFields, ['EMP'])
            l1[37] += varSum(row, csvFields, ['UNEMP'])
            l1[38] += varSum(row, csvFields, ['NOT_IN_LBFRC'])
            l1[39] += varSum(row, csvFields, ['WORK_AT_HOME'])
            l1[40] += varSum(row, csvFields, ['TOT_COMM'])
            l1[41] += varSum(row, csvFields, ['DROVE_AL'])
            l1[42] += varSum(row, csvFields, ['CARPOOL'])
            l1[43] += varSum(row, csvFields, ['TRANSIT'])
            l1[44] += varSum(row, csvFields, ['WALK_BIKE'])
            l1[45] += varSum(row, csvFields, ['COMM_OTHER'])
            try:
                l1[46] += varSum2(row, csvFields, ['AGG_TT'])
            except ValueError:
                l1[46] = 'N/A'
            except TypeError:
                l1[46] = 'N/A'
            l1[47] += varSum(row, csvFields, ['NO_VEH'])
            l1[48] += varSum(row, csvFields, ['ONE_VEH'])
            l1[49] += varSum(row, csvFields, ['TWO_VEH'])
            l1[50] += varSum(row, csvFields, ['THREEOM_VEH'])
            l1[51] += varSum(row, csvFields, ['POP_25OV'])
            l1[52] += varSum(row, csvFields, ['LT_HS'])
            l1[53] += varSum(row, csvFields, ['HS'])
            l1[54] += varSum(row, csvFields, ['SOME_COLL'])
            l1[55] += varSum(row, csvFields, ['ASSOC'])
            l1[56] += varSum(row, csvFields, ['BACH'])
            l1[57] += varSum(row, csvFields, ['GRAD_PROF'])
            l1[58] += varSum(row, csvFields, ['INC_LT_25K'])
            l1[59] += varSum(row, csvFields, ['INC_25_50K'])
            l1[60] += varSum(row, csvFields, ['INC_50_75K'])
            l1[61] += varSum(row, csvFields, ['INC_75_100K'])
            l1[62] += varSum(row, csvFields, ['INC_100_150K'])
            l1[63] += varSum(row, csvFields, ['INC_GT_150'])
            l1[64] += varSum(row, csvFields, ['INC_LT_45K'])
            l1[65] += varSum(row, csvFields, ['TOT_HH'])
            l1[66] += varSum(row, csvFields, ['OWN_OCC_HU'])
            l1[67] += varSum(row, csvFields, ['RENT_OCC_HU'])
            l1[68] += varSum(row, csvFields, ['VAC_HU'])
            l1[69] += varSum(row, csvFields, ['VAC_IMP'])
            l1[70] += varSum(row, csvFields, ['VAC_NOT_IMP'])
            l1[71] += varSum(row, csvFields, ['VAC_FOR_RENT'])
            l1[72] += varSum(row, csvFields, ['VAC_FOR_SALE'])
            l1[73] += varSum(row, csvFields, ['VAC_OTHER'])
            l1[74] += varSum(row, csvFields, ['OWN_1_PERS_HH'])
            l1[75] += varSum(row, csvFields, ['OWN_2_PERS_HH'])
            l1[76] += varSum(row, csvFields, ['OWN_3_PERS_HH'])
            l1[77] += varSum(row, csvFields, ['OWN_4_PERS_HH'])
            l1[78] += varSum(row, csvFields, ['OWN_5_PERS_HH'])
            l1[79] += varSum(row, csvFields, ['OWN_6_PERS_HH'])
            l1[80] += varSum(row, csvFields, ['OWN_7_MORE_HH'])
            l1[81] += varSum(row, csvFields, ['RENT_1_PERS_HH'])
            l1[82] += varSum(row, csvFields, ['RENT_2_PERS_HH'])
            l1[83] += varSum(row, csvFields, ['RENT_3_PERS_HH'])
            l1[84] += varSum(row, csvFields, ['RENT_4_PERS_HH'])
            l1[85] += varSum(row, csvFields, ['RENT_5_PERS_HH'])
            l1[86] += varSum(row, csvFields, ['RENT_6_PERS_HH'])
            l1[87] += varSum(row, csvFields, ['RENT_7_MORE_HH'])
            l1[88] += varSum(row, csvFields, ['HU_TOT'])
            l1[89] += varSum(row, csvFields, ['HU_SNG_DET'])
            l1[90] += varSum(row, csvFields, ['HU_SNG_ATT'])
            l1[91] += varSum(row, csvFields, ['HU_2UN'])
            l1[92] += varSum(row, csvFields, ['HU_3_4UN'])
            l1[93] += varSum(row, csvFields, ['HU_GT_5UN'])
            l1[94] += varSum(row, csvFields, ['HU_OWN_1DET'])
            l1[95] += varSum(row, csvFields, ['HU_OWN_1ATT'])
            l1[96] += varSum(row, csvFields, ['HU_OWN_2'])
            l1[97] += varSum(row, csvFields, ['HU_OWN_3_4'])
            l1[98] += varSum(row, csvFields, ['HU_OWN_5_9'])
            l1[99] += varSum(row, csvFields, ['HU_OWN_10_19'])
            l1[100] += varSum(row, csvFields, ['HU_OWN_20_49'])
            l1[101] += varSum(row, csvFields, ['HU_OWN_50OV'])
            l1[102] += varSum(row, csvFields, ['HU_OWN_MOB_HOME'])
            l1[103] += varSum(row, csvFields, ['HU_OWN_OTHER_MOB'])
            l1[104] += varSum(row, csvFields, ['HU_RENT_1DET'])
            l1[105] += varSum(row, csvFields, ['HU_RENT_1ATT'])
            l1[106] += varSum(row, csvFields, ['HU_RENT_2'])
            l1[107] += varSum(row, csvFields, ['HU_RENT_3_4'])
            l1[108] += varSum(row, csvFields, ['HU_RENT_5_9'])
            l1[109] += varSum(row, csvFields, ['HU_RENT_10_19'])
            l1[110] += varSum(row, csvFields, ['HU_RENT_20_49'])
            l1[111] += varSum(row, csvFields, ['HU_RENT_50OV'])
            l1[112] += varSum(row, csvFields, ['HU_RENT_MOB_HOME'])
            l1[113] += varSum(row, csvFields, ['HU_RENT_OTHER_MOB'])
            l1[114] += varSum(row, csvFields, ['HA_AFT2000'])
            l1[115] += varSum(row, csvFields, ['HA_80_00'])
            l1[116] += varSum(row, csvFields, ['HA_70_00'])
            l1[117] += varSum(row, csvFields, ['HA_60_80'])
            l1[118] += varSum(row, csvFields, ['HA_40_70'])
            l1[119] += varSum(row, csvFields, ['HA_40_60'])
            l1[120] += varSum(row, csvFields, ['HA_BEF1940'])
            l1[121] += varSum(row, csvFields, ['BR_0_1'])
            l1[122] += varSum(row, csvFields, ['BR_2'])
            l1[123] += varSum(row, csvFields, ['BR_3'])
            l1[124] += varSum(row, csvFields, ['BR_4'])
            l1[125] += varSum(row, csvFields, ['BR_5'])
            l1[126] += varSum(row, csvFields, ['AGG_VEH_AVAIL'])
            l1[127] += varSum(row, csvFields, ['HV_LT_150K'])
            l1[128] += varSum(row, csvFields, ['HV_150_300K'])
            l1[129] += varSum(row, csvFields, ['HV_300_500K'])
            l1[130] += varSum(row, csvFields, ['HV_GT_500K'])
            l1[131] += varSum(row, csvFields, ['OWNCST_OV30PCT'])
            l1[132] += varSum(row, csvFields, ['HU_OWN_INC_LT5K'])
            l1[133] += varSum(row, csvFields, ['HU_OWN_INC_5K_10K'])
            l1[134] += varSum(row, csvFields, ['HU_OWN_INC_10K_15K'])
            l1[135] += varSum(row, csvFields, ['HU_OWN_INC_15K_20K'])
            l1[136] += varSum(row, csvFields, ['HU_OWN_INC_20K_25K'])
            l1[137] += varSum(row, csvFields, ['HU_OWN_INC_25K_35K'])
            l1[138] += varSum(row, csvFields, ['HU_OWN_INC_35K_50K'])
            l1[139] += varSum(row, csvFields, ['HU_OWN_INC_50K_75K'])
            l1[140] += varSum(row, csvFields, ['HU_OWN_INC_75K_100K'])
            l1[141] += varSum(row, csvFields, ['HU_OWN_INC_100K_150K'])
            l1[142] += varSum(row, csvFields, ['HU_OWN_INC_150KOV'])
            l1[143] += varSum(row, csvFields, ['HU_RENT_INC_LT5K'])
            l1[144] += varSum(row, csvFields, ['HU_RENT_INC_5K_10K'])
            l1[145] += varSum(row, csvFields, ['HU_RENT_INC_10K_15K'])
            l1[146] += varSum(row, csvFields, ['HU_RENT_INC_15K_20K'])
            l1[147] += varSum(row, csvFields, ['HU_RENT_INC_20K_25K'])
            l1[148] += varSum(row, csvFields, ['HU_RENT_INC_25K_35K'])
            l1[149] += varSum(row, csvFields, ['HU_RENT_INC_35K_50K'])
            l1[150] += varSum(row, csvFields, ['HU_RENT_INC_50K_75K'])
            l1[151] += varSum(row, csvFields, ['HU_RENT_INC_75K_100K'])
            l1[152] += varSum(row, csvFields, ['HU_RENT_INC_100K_150K'])
            l1[153] += varSum(row, csvFields, ['HU_RENT_INC_150KOV'])
            l1[154] += varSum(row, csvFields, ['HCUND20K'])
            l1[155] += varSum(row, csvFields, ['HCUND20K_LT20PCT'])
            l1[156] += varSum(row, csvFields, ['HCUND20K_20_29PCT'])
            l1[157] += varSum(row, csvFields, ['HCUND20K_30MPCT'])
            l1[158] += varSum(row, csvFields, ['HC20Kto49K'])
            l1[159] += varSum(row, csvFields, ['HC20Kto49K_LT20PCT'])
            l1[160] += varSum(row, csvFields, ['HC20Kto49K_20_29PCT'])
            l1[161] += varSum(row, csvFields, ['HC20Kto49K_30MPCT'])
            l1[162] += varSum(row, csvFields, ['HC50Kto75K'])
            l1[163] += varSum(row, csvFields, ['HC50Kto75K_LT20PCT'])
            l1[164] += varSum(row, csvFields, ['HC50Kto75K_20_29PCT'])
            l1[165] += varSum(row, csvFields, ['HC50Kto75K_30MPCT'])
            l1[166] += varSum(row, csvFields, ['HCOV75K'])
            l1[167] += varSum(row, csvFields, ['HCOV75K_LT20PCT'])
            l1[168] += varSum(row, csvFields, ['HCOV75K_20_29PCT'])
            l1[169] += varSum(row, csvFields, ['HCOV75K_30MPCT'])
            l1[170] += varSum(row, csvFields, ['RNTCST_OV30PCT'])
            l1[171] += varSum(row, csvFields, ['ENGLISH'])
            l1[172] += varSum(row, csvFields, ['SPANISH'])
            l1[173] += varSum(row, csvFields, ['SLAVIC'])
            l1[174] += varSum(row, csvFields, ['CHINESE'])
            l1[175] += varSum(row, csvFields, ['TAGALOG'])
            l1[176] += varSum(row, csvFields, ['ARABIC'])
            l1[177] += varSum(row, csvFields, ['KOREAN'])
            l1[178] += varSum(row, csvFields, ['OTHER_ASIAN'])
            l1[179] += varSum(row, csvFields, ['OTHER_EURO'])
            l1[180] += varSum(row, csvFields, ['OTHER_UNSPEC'])
            l1[181] += varSum(row, csvFields, ['NATIVE'])
            l1[182] += varSum(row, csvFields, ['FOR_BORN'])
            l1[183] += varSum(row, csvFields, ['POP_OV5'])
            l1[184] += varSum(row, csvFields, ['ONLY_ENGLISH'])
            l1[185] += varSum(row, csvFields, ['NOT_ENGLISH'])
            l1[186] += varSum(row, csvFields, ['LING_ISO'])
            l1[187] += varSum(row, csvFields, ['POV_SURV'])
            l1[188] += varSum(row, csvFields, ['POV_POP'])
            l1[189] += varSum(row, csvFields, ['TOT_FAMILIES'])
            l1[190] += varSum(row, csvFields, ['POV_FAM'])
            l1[191] += varSum(row, csvFields, ['HH_PUB_ASSIST_OR_FOOD_STAMPS'])
            l1[192] += varSum(row, csvFields, ['FAM_INC_UND45K'])
            l1[193] += varSum(row, csvFields, ['POP_CIV_NONINST'])
            l1[194] += varSum(row, csvFields, ['DISABLED'])
            l1[195] += varSum(row, csvFields, ['POP_NO_HINS'])

        # Return to start of input csv
        rfile.seek(0)

        # Rounds to whole number, writes to out csv
        for i in range(1, len(l1)):
            try:
                l1[i] = round(l1[i], 0)
            except TypeError:
                l1[i] = 'N/A'
        csvOut.writerow(l1)

# Open summarized csvs for use in SQL join
# Creates the database.
connection = sqlite3.connect(':memory:')
cursor = connection.cursor()

with open('ACS{}_regional_medians.csv'.format(year), 'rb') as rMed:
    sqlCsvMed = csv.reader(rMed)
    csvSqlPrep(sqlCsvMed, 'sqlMed')

with open('ACS{}_regional_summary.csv'.format(year), 'rb') as rAll:
    sqlCsvAll = csv.reader(rAll)
    csvSqlPrep(sqlCsvAll, 'sqlAll')

# Creates output csv file
with open(r'S:\Projects\CDS\input_data\ACS\{0}\ACS{0}_selVariablesRegion.csv'.format(year), 'wb') as w_Reg:
    ccaReg_jn = csv.writer(w_Reg)
    ccaReg_jn.writerow(('GEOG', 'TOT_POP', 'UND19', 'A20_34', 'A35_49', 'A50_64', 'A65_74', 'A75_84', 'OV85', 'MED_AGE', 'WHITE', 'HISP', 'BLACK', 'ASIAN', 'OTHER', 'POP_HH', 'CT_SP_WCHILD', 'CT_1PHH', 'CT_2PHH', 'CT_3PHH', 'CT_4MPHH', 'CT_FAM_HH', 'CT_2PF', 'CT_3PF', 'CT_4PF', 'CT_5PF', 'CT_6PF', 'CT_7MPF', 'CT_NONFAM_HH', 'CT_2PNF', 'CT_3PNF', 'CT_4PNF', 'CT_5PNF', 'CT_6PNF', 'CT_7MPNF', 'POP_16OV', 'IN_LBFRC', 'EMP', 'UNEMP', 'NOT_IN_LBFRC', 'WORK_AT_HOME', 'TOT_COMM', 'DROVE_AL', 'CARPOOL', 'TRANSIT', 'WALK_BIKE', 'COMM_OTHER', 'AGG_TT', 'NO_VEH', 'ONE_VEH', 'TWO_VEH', 'THREEOM_VEH', 'POP_25OV', 'LT_HS', 'HS', 'SOME_COLL', 'ASSOC', 'BACH', 'GRAD_PROF', 'INC_LT_25K', 'INC_25_50K', 'INC_50_75K', 'INC_75_100K', 'INC_100_150K', 'INC_GT_150', 'MEDINC', 'INC_LT_45K', 'TOT_HH', 'OWN_OCC_HU', 'RENT_OCC_HU', 'VAC_HU', 'VAC_IMP', 'VAC_NOT_IMP', 'VAC_FOR_RENT', 'VAC_FOR_SALE', 'VAC_OTHER', 'OWN_1_PERS_HH', 'OWN_2_PERS_HH', 'OWN_3_PERS_HH', 'OWN_4_PERS_HH', 'OWN_5_PERS_HH', 'OWN_6_PERS_HH', 'OWN_7_MORE_HH', 'RENT_1_PERS_HH', 'RENT_2_PERS_HH', 'RENT_3_PERS_HH', 'RENT_4_PERS_HH', 'RENT_5_PERS_HH', 'RENT_6_PERS_HH', 'RENT_7_MORE_HH', 'HU_TOT', 'HU_SNG_DET', 'HU_SNG_ATT', 'HU_2UN', 'HU_3_4UN', 'HU_GT_5UN', 'MED_ROOMS', 'HU_OWN_1DET', 'HU_OWN_1ATT', 'HU_OWN_2', 'HU_OWN_3_4', 'HU_OWN_5_9', 'HU_OWN_10_19', 'HU_OWN_20_49', 'HU_OWN_50OV', 'HU_OWN_MOB_HOME', 'HU_OWN_OTHER_MOB', 'HU_RENT_1DET', 'HU_RENT_1ATT', 'HU_RENT_2', 'HU_RENT_3_4', 'HU_RENT_5_9', 'HU_RENT_10_19', 'HU_RENT_20_49', 'HU_RENT_50OV', 'HU_RENT_MOB_HOME', 'HU_RENT_OTHER_MOB', 'HA_AFT2000', 'HA_80_00', 'HA_70_00', 'HA_60_80', 'HA_40_70', 'HA_40_60', 'HA_BEF1940', 'MED_HA', 'BR_0_1', 'BR_2', 'BR_3', 'BR_4', 'BR_5', 'AGG_VEH_AVAIL', 'HV_LT_150K', 'HV_150_300K', 'HV_300_500K', 'HV_GT_500K', 'MED_HV', 'OWNCST_OV30PCT', 'HU_OWN_INC_LT5K', 'HU_OWN_INC_5K_10K', 'HU_OWN_INC_10K_15K', 'HU_OWN_INC_15K_20K', 'HU_OWN_INC_20K_25K', 'HU_OWN_INC_25K_35K', 'HU_OWN_INC_35K_50K', 'HU_OWN_INC_50K_75K', 'HU_OWN_INC_75K_100K', 'HU_OWN_INC_100K_150K', 'HU_OWN_INC_150KOV', 'HU_RENT_INC_LT5K', 'HU_RENT_INC_5K_10K', 'HU_RENT_INC_10K_15K', 'HU_RENT_INC_15K_20K', 'HU_RENT_INC_20K_25K', 'HU_RENT_INC_25K_35K', 'HU_RENT_INC_35K_50K', 'HU_RENT_INC_50K_75K', 'HU_RENT_INC_75K_100K', 'HU_RENT_INC_100K_150K', 'HU_RENT_INC_150KOV',    'HCUND20K', 'HCUND20K_LT20PCT', 'HCUND20K_20_29PCT', 'HCUND20K_30MPCT', 'HC20Kto49K', 'HC20Kto49K_LT20PCT', 'HC20Kto49K_20_29PCT', 'HC20Kto49K_30MPCT', 'HC50Kto75K', 'HC50Kto75K_LT20PCT', 'HC50Kto75K_20_29PCT', 'HC50Kto75K_30MPCT', 'HCOV75K', 'HCOV75K_LT20PCT', 'HCOV75K_20_29PCT', 'HCOV75K_30MPCT', 'RNTCST_OV30PCT', 'ENGLISH', 'SPANISH', 'SLAVIC', 'CHINESE', 'TAGALOG', 'ARABIC', 'KOREAN', 'OTHER_ASIAN', 'OTHER_EURO', 'OTHER_UNSPEC', 'NATIVE', 'FOR_BORN', 'POP_OV5', 'ONLY_ENGLISH', 'NOT_ENGLISH', 'LING_ISO', 'POV_SURV', 'POV_POP', 'TOT_FAMILIES', 'POV_FAM', 'HH_PUB_ASSIST_OR_FOOD_STAMPS', 'FAM_INC_UND45K', 'POP_CIV_NONINST', 'DISABLED', 'POP_NO_HINS'))

    # Join tables based on geoid
    cursor.execute('SELECT sqlAll.GEOG,sqlAll.TOT_POP,sqlAll.UND19,sqlAll.A20_34,sqlAll.A35_49,sqlAll.A50_64,sqlAll.A65_74,sqlAll.A75_84,sqlAll.OV85,sqlMed.MED_AGE,sqlAll.WHITE,sqlAll.HISP,sqlAll.BLACK,sqlAll.ASIAN,sqlAll.OTHER,sqlAll.POP_HH,sqlAll.CT_SP_WCHILD,sqlAll.CT_1PHH,sqlAll.CT_2PHH,sqlAll.CT_3PHH,sqlAll.CT_4MPHH,sqlAll.CT_FAM_HH,sqlAll.CT_2PF,sqlAll.CT_3PF,sqlAll.CT_4PF,sqlAll.CT_5PF,sqlAll.CT_6PF,sqlAll.CT_7MPF,sqlAll.CT_NONFAM_HH,sqlAll.CT_2PNF,sqlAll.CT_3PNF,sqlAll.CT_4PNF,sqlAll.CT_5PNF,sqlAll.CT_6PNF,sqlAll.CT_7MPNF,sqlAll.POP_16OV,sqlAll.IN_LBFRC,sqlAll.EMP,sqlAll.UNEMP,sqlAll.NOT_IN_LBFRC,sqlAll.WORK_AT_HOME,sqlAll.TOT_COMM,sqlAll.DROVE_AL,sqlAll.CARPOOL,sqlAll.TRANSIT,sqlAll.WALK_BIKE,sqlAll.COMM_OTHER,sqlAll.AGG_TT,sqlAll.NO_VEH,sqlAll.ONE_VEH,sqlAll.TWO_VEH,sqlAll.THREEOM_VEH,sqlAll.POP_25OV,sqlAll.LT_HS,sqlAll.HS,sqlAll.SOME_COLL,sqlAll.ASSOC,sqlAll.BACH,sqlAll.GRAD_PROF,sqlAll.INC_LT_25K,sqlAll.INC_25_50K,sqlAll.INC_50_75K,sqlAll.INC_75_100K,sqlAll.INC_100_150K,sqlAll.INC_GT_150,sqlMed.MEDINC,sqlAll.INC_LT_45K,sqlAll.TOT_HH,sqlAll.OWN_OCC_HU,sqlAll.RENT_OCC_HU,sqlAll.VAC_HU,sqlAll.VAC_IMP,sqlAll.VAC_NOT_IMP,sqlAll.VAC_FOR_RENT,sqlAll.VAC_FOR_SALE,sqlAll.VAC_OTHER,sqlAll.OWN_1_PERS_HH,sqlAll.OWN_2_PERS_HH,sqlAll.OWN_3_PERS_HH,sqlAll.OWN_4_PERS_HH,sqlAll.OWN_5_PERS_HH,sqlAll.OWN_6_PERS_HH,sqlAll.OWN_7_MORE_HH,sqlAll.RENT_1_PERS_HH,sqlAll.RENT_2_PERS_HH,sqlAll.RENT_3_PERS_HH,sqlAll.RENT_4_PERS_HH,sqlAll.RENT_5_PERS_HH,sqlAll.RENT_6_PERS_HH,sqlAll.RENT_7_MORE_HH,sqlAll.HU_TOT,sqlAll.HU_SNG_DET,sqlAll.HU_SNG_ATT,sqlAll.HU_2UN,sqlAll.HU_3_4UN,sqlAll.HU_GT_5UN,sqlMed.MED_ROOMS,sqlAll.HU_OWN_1DET,sqlAll.HU_OWN_1ATT,sqlAll.HU_OWN_2,sqlAll.HU_OWN_3_4,sqlAll.HU_OWN_5_9,sqlAll.HU_OWN_10_19,sqlAll.HU_OWN_20_49,sqlAll.HU_OWN_50OV,sqlAll.HU_OWN_MOB_HOME,sqlAll.HU_OWN_OTHER_MOB,sqlAll.HU_RENT_1DET,sqlAll.HU_RENT_1ATT,sqlAll.HU_RENT_2,sqlAll.HU_RENT_3_4,sqlAll.HU_RENT_5_9,sqlAll.HU_RENT_10_19,sqlAll.HU_RENT_20_49,sqlAll.HU_RENT_50OV,sqlAll.HU_RENT_MOB_HOME,sqlAll.HU_RENT_OTHER_MOB,sqlAll.HA_AFT2000,sqlAll.HA_80_00,sqlAll.HA_70_00,sqlAll.HA_60_80,sqlAll.HA_40_70,sqlAll.HA_40_60,sqlAll.HA_BEF1940,sqlMed.MED_HA,sqlAll.BR_0_1,sqlAll.BR_2,sqlAll.BR_3,sqlAll.BR_4,sqlAll.BR_5,sqlAll.AGG_VEH_AVAIL,sqlAll.HV_LT_150K,sqlAll.HV_150_300K,sqlAll.HV_300_500K,sqlAll.HV_GT_500K,sqlMed.MED_HV,sqlAll.OWNCST_OV30PCT,sqlAll.HU_OWN_INC_LT5K,sqlAll.HU_OWN_INC_5K_10K,sqlAll.HU_OWN_INC_10K_15K,sqlAll.HU_OWN_INC_15K_20K,sqlAll.HU_OWN_INC_20K_25K,sqlAll.HU_OWN_INC_25K_35K,sqlAll.HU_OWN_INC_35K_50K,sqlAll.HU_OWN_INC_50K_75K,sqlAll.HU_OWN_INC_75K_100K,sqlAll.HU_OWN_INC_100K_150K,sqlAll.HU_OWN_INC_150KOV,sqlAll.HU_RENT_INC_LT5K,sqlAll.HU_RENT_INC_5K_10K,sqlAll.HU_RENT_INC_10K_15K,sqlAll.HU_RENT_INC_15K_20K,sqlAll.HU_RENT_INC_20K_25K,sqlAll.HU_RENT_INC_25K_35K,sqlAll.HU_RENT_INC_35K_50K,sqlAll.HU_RENT_INC_50K_75K,sqlAll.HU_RENT_INC_75K_100K,sqlAll.HU_RENT_INC_100K_150K,sqlAll.HU_RENT_INC_150KOV,sqlAll.HCUND20K,sqlAll.HCUND20K_LT20PCT,sqlAll.HCUND20K_20_29PCT,sqlAll.HCUND20K_30MPCT,sqlAll.HC20Kto49K,sqlAll.HC20Kto49K_LT20PCT,sqlAll.HC20Kto49K_20_29PCT,sqlAll.HC20Kto49K_30MPCT,sqlAll.HC50Kto75K,sqlAll.HC50Kto75K_LT20PCT,sqlAll.HC50Kto75K_20_29PCT,sqlAll.HC50Kto75K_30MPCT,sqlAll.HCOV75K,sqlAll.HCOV75K_LT20PCT,sqlAll.HCOV75K_20_29PCT,sqlAll.HCOV75K_30MPCT,sqlAll.RNTCST_OV30PCT,sqlAll.ENGLISH,sqlAll.SPANISH,sqlAll.SLAVIC,sqlAll.CHINESE,sqlAll.TAGALOG,sqlAll.ARABIC,sqlAll.KOREAN,sqlAll.OTHER_ASIAN,sqlAll.OTHER_EURO,sqlAll.OTHER_UNSPEC,sqlAll.NATIVE,sqlAll.FOR_BORN,sqlAll.POP_OV5,sqlAll.ONLY_ENGLISH,sqlAll.NOT_ENGLISH,sqlAll.LING_ISO,sqlAll.POV_SURV,sqlAll.POV_POP,sqlAll.TOT_FAMILIES,sqlAll.POV_FAM,sqlAll.HH_PUB_ASSIST_OR_FOOD_STAMPS,sqlAll.FAM_INC_UND45K,sqlAll.POP_CIV_NONINST,sqlAll.DISABLED,sqlAll.POP_NO_HINS FROM sqlAll INNER JOIN sqlMed ON (sqlAll.GEOG = sqlMed.GEOG)')
    for i in cursor:
        i = list(i)
        ccaReg_jn.writerow(i)

# Deletes intermediate csvs
csv_list = ['ACS{}_regional_medians.csv'.format(year), 'ACS{}_regional_summary.csv'.format(year)]
for csv_file in csv_list:
    try:
        os.remove(csv_file)
    except:
        pass

print('region complete.')
