ensure_dir(inputPathPickle_Cost)
ensure_dir(inputPathPickle_Beta)
indent = '        '
#-------------------------------------------------------------------------------
print str(datetime.now()) + ' -- Reading in Files'
print str(datetime.now()) + indent + '  Getting Disaster Data'
# DISASASTER TOT AFFECTED
# Read in the disasterType data
print(inputPath)
[disasterWhichTypeHeaderRow, disasterWhichTypeRead] = f_myReadCsv(inputPath + disasterWhichTypeToUseFileName)
disasterTypeNames = columnByName(disasterWhichTypeRead, disasterWhichTypeHeaderRow, 'disasterType')
disasterTypeUseID = columnByName(disasterWhichTypeRead, disasterWhichTypeHeaderRow, 'include')
disasterWhichToUseSubset = [disasterTypeNames[i] for i in range(len(disasterTypeNames)) if disasterTypeUseID[i] == '1']



[disasterWhichCountryHeaderRow, disasterWhichCountryRead] = f_myReadCsv(inputPath + disasterCountryWhichToUseReadInFileName)
disasterCountryNames = columnByName(disasterWhichCountryRead, disasterWhichCountryHeaderRow, 'gglCountry')
disasterCountryUseID = columnByName(disasterWhichCountryRead, disasterWhichCountryHeaderRow, 'UseMe')
disasterWhichCountrySubset = [disasterCountryNames[i] for i in range(len(disasterCountryNames)) if disasterCountryUseID[i] == '1']



if 1 == 1:
  # Read in the demand data
  [disasterTotAffHeaderRow, disasterTotAffRead] = f_myReadCsv(inputPath + disasterTotAffectedFileName)
  #Filter out those disasters not wanted and years before minYear
  disasterTotAffSubRead1 = createSubMatrixByColAndVectLkup(disasterTotAffRead, disasterTotAffHeaderRow, 'Type', disasterWhichToUseSubset)
  disasterTotAffSubRead = createSubMatrixByColAndVectLkup(disasterTotAffSubRead1, disasterTotAffHeaderRow, 'gglCountry', disasterWhichCountrySubset)
  yearsToIncludeAsString = range(minDisasterYear, maxDisasterYear + 1)
  yearsToIncludeAsString = deepcopy([str(i) for i in yearsToIncludeAsString])
  disasterTotAffSubRead = deepcopy(createSubMatrixByColAndVectLkup(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Year', yearsToIncludeAsString ))

if 1 == 1:
  #Filter out results with null tot affected
  subTotAffAll = columnByName(disasterTotAffSubRead,disasterTotAffHeaderRow, 'TotAffected')
  subTotAffNotNull = []
  for i in range(len(subTotAffAll)):
    try:
      int(subTotAffAll[i])
      subTotAffNotNull.append(i)
    except ValueError:
      pass    
  disasterTotAffSubRead = deepcopy([disasterTotAffSubRead[i] for i in subTotAffNotNull])
  #Change Tot Affected to int
  disasterTotAffSubRead = deepcopy(changeColType(disasterTotAffSubRead, disasterTotAffHeaderRow, 'TotAffected', 'int'))
  # Change dates to int's
  disasterTotAffSubRead = deepcopy(changeColType(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Day', 'int'))
  disasterTotAffSubRead = deepcopy(changeColType(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Month', 'int'))
  disasterTotAffSubRead = deepcopy(changeColType(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Year', 'int'))


"""
  The way the file reads in data is faulty.

  Specifically, this line:

  disasterTotAffectedD = dict(zip(zip(disasterIDVect, disasterIDVect_SubLoc), columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'TotAffected')))

  On the 1980+ data, disasterIDVect has 7359 entries, while the dict has only 6923.  THis is because there are duplicate disaster IDs for disasters that occurred in multiple countries.  (5.9%).  I hadn't realized this, and ignored it.  Thus, when the file gets "dict"'d, it chooses one disatser ID and one value.  It tends to choose the value that comes latest in the list order which is not null (because null values are already filtered out).

  So that the 7359 values include disasters from 1980+, which are in the set of disasters to be included, which are not null.  

  Within this subset, there may be duplicate disaster IDs.  In this case, the software will eliminate the first entry(s) of a disaster ID when it turns the list into a dict.  

  The excel file 
  "C:\Users\jaa26\Dropbox\Academic\Papers\HumIndex\Jason\Data\GettingRawDataPython\WorkWithEmDatData\Em-Dat numDisasters.xlsx"

  has the analysis dulpicating this.


"""

disasterLocationsDisaster = list(set(columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglAddress')))
countriesOfDisastersDisaster = list(set(columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglCountry')))

#disasterIDVect = [ 'DisasterID_{0:05}'.format(i) for i in range(len(disasterTotAffSubRead))]
disasterIDVect = columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'DisasterID')
disasterIDVect_SubLoc = []
kCount = 0
for i in range(len(disasterIDVect)):
  tmpDisastIDNew = deepcopy(disasterIDVect[i])
  if i == 0:
    disasterIDVect_SubLoc.append('SubLoc_{0:05}'.format(kCount))
  else:
    if tmpDisastIDOld == tmpDisastIDNew:
      kCount += 1
    else:
      kCount = 0
    disasterIDVect_SubLoc.append('SubLoc_{0:05}'.format(kCount))
  tmpDisastIDOld = deepcopy(tmpDisastIDNew)



    
#totAffectedNamesD = zip(disasterIDVect, columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglAddress'))
#totAffectedD = dict(zip(totAffectedNamesD, columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'TotAffected')))


disasterTotAffectedD = dict(zip(zip(disasterIDVect, disasterIDVect_SubLoc), columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'TotAffected')))
disasterGglAddressD = dict(zip(zip(disasterIDVect, disasterIDVect_SubLoc), columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglAddress')))
disasterGglCountryD = dict(zip(zip(disasterIDVect, disasterIDVect_SubLoc), columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglCountry')))
disasterDistTypeD = dict(zip(disasterIDVect, columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Type')))
disasterMonthD = dict(zip(disasterIDVect, columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Month')))
disasterYearD = dict(zip(disasterIDVect, columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'Year')))
disasterProbD = dict(zip(disasterIDVect, [1. / len(disasterIDVect)] * len(disasterIDVect)))



#------------------------------------------------------------------------------
# Create a disaster/country/continent lookup table for future use:
[countryContLkupHeaderRow, countryContLkupData] = f_myReadCsv(inputPath + gglCountryContinentLkupFileName)
myDistasterCountriesTup = list(set(zip(columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglAddress'), columnByName(disasterTotAffSubRead, disasterTotAffHeaderRow, 'gglCountry'))))
countryCont_CountryCol = columnByName(countryContLkupData, countryContLkupHeaderRow, 'gglCountry')
countryCont_ContinCol = columnByName(countryContLkupData, countryContLkupHeaderRow, 'Continent')

#countryToContinentD = {}
disasterLocToCountryD = {}
disasterLocToContinentD = {}

for i_dist in range(len(myDistasterCountriesTup)): 
  myDisasterLoc = myDistasterCountriesTup[i_dist][0]
  myCountry = myDistasterCountriesTup[i_dist][1]
  myContinent = countryCont_ContinCol[[i for i in range(len(countryCont_ContinCol)) if myCountry == countryCont_CountryCol[i]][0]]
  #countryToContinentD.update({myCountry: myContinent})
  disasterLocToCountryD.update({myDisasterLoc: myCountry})
  disasterLocToContinentD.update({myDisasterLoc: myContinent})

 
#-------------------------------------------------------------------------------
# Calculate the minimum inventory required per country
if 1 == 1:
  MIN_DISASTERS_CTRY_HOLD_INV = 2
  MIN_DISASTERS_CTRY_PCNTL = 60
  minInventoryPerCountryD = {}
  for i_country in countriesOfDisastersDisaster:
    disasterIdsHere = [i for i in disasterGglCountryD.keys() if disasterGglCountryD[i] == i_country]
    totAffectedHereVect = [disasterTotAffectedD[i] for i in disasterIdsHere]
    if len(disasterIdsHere) > MIN_DISASTERS_CTRY_HOLD_INV:
      minInventoryPerCountryD.update({i_country: int(round(numpy.percentile(totAffectedHereVect, MIN_DISASTERS_CTRY_PCNTL), 0))})
    else:
      minInventoryPerCountryD.update({i_country: int(0)})

#AXR: changed the next line
#minInventoryPerCountryD.update({'Samoa':5000})

for i_c in countriesOfDisastersDisaster:
    print i_c + "," + str(minInventoryPerCountryD[i_c])
 
 
#------------------------------------------------------------------------------
# INVENTORY DATA 
print str(datetime.now()) + indent + '  Getting Inventory Data'
# Read in the depot "which to use" data
[depotWhichToUseHeaderRow, depotWhichToUseRead] = f_myReadCsv(inputPath + depotWhichToUseReadInvFileName)

##################################JAMESSTART##########################
[contractorHead, contractorData] = f_myReadCsv(inputPath + "fakeContractorDataJames.csv")

contractor_depotWhichToUseHeaderRow = []
contractor_depotWhichToUseRead = []

contractor_depotWhichToUseHeaderRow = deepcopy(depotWhichToUseHeaderRow)
contractor_depotWhichToUseHeaderRow.append(contractorHead[0]) #Alter city names


for original_row in depotWhichToUseRead:
  no_contractor_row = deepcopy(original_row)
  no_contractor_row.append("None")
  contractor_depotWhichToUseRead.append(no_contractor_row)


  for contractor_row in contractorData:
    contractorCity = contractor_row[5]
    originalCity = original_row[1].split(",")[0]


    if contractorCity == originalCity:
      new_row = deepcopy(original_row)
      new_row.append(contractor_row[0]) 
      contractor_depotWhichToUseRead.append(new_row)


depotWhichToUseHeaderRow = contractor_depotWhichToUseHeaderRow #Remap original data to altered data
depotWhichToUseRead = contractor_depotWhichToUseRead












print(contractor_depotWhichToUseHeaderRow)
for row in contractor_depotWhichToUseRead:
  print(row)
#sys.exit()

#Notes

##################################JAMESEND##########################























depotWhichToUseNames = columnByName(depotWhichToUseRead, depotWhichToUseHeaderRow, 'gglAddressAscii')
depotWhichToUseID = columnByName(depotWhichToUseRead, depotWhichToUseHeaderRow, 'include')
depotWhichToUseSubset = [depotWhichToUseNames[i] for i in range(len(depotWhichToUseNames)) if depotWhichToUseID[i] == '1']

depotWhichFixedID = columnByName(depotWhichToUseRead, depotWhichToUseHeaderRow, 'FixedInventory')
depotWhichFixedSubset = [depotWhichToUseNames[i] for i in range(len(depotWhichToUseNames)) if depotWhichFixedID[i] == '1']



[depotWhichToMapToHeaderRow, depotWhichToMapToRead] = f_myReadCsv(inputPath + depotWhichToMapToFileName)
depotMapFromNames = columnByName(depotWhichToMapToRead, depotWhichToMapToHeaderRow, 'gglAddressAsciiMapFrom')
depotMapToNames = columnByName(depotWhichToMapToRead, depotWhichToMapToHeaderRow, 'gglAddressAsciiMapTo')

#depotNamesMapTo = list(set(depotMapToNames))
depotNamesMapTo = list(set(depotMapToNames).intersection(set(depotWhichToUseSubset)))
#raise NameError('Is this really correct? 2015-07-15')

[inventoryHeaderRow, inventoryDataReadRaw] = f_myReadCsv(inputPath + depotInventoryFileName)
depotNamesInventoryRawNotUnique = columnByName(inventoryDataReadRaw, inventoryHeaderRow, 'gglAddress')
inventoryDataRead = []
# Exclude observations not in the "include" cities
for i in range(len(depotNamesInventoryRawNotUnique)):
  if depotNamesInventoryRawNotUnique[i] in depotWhichToUseSubset:
    ix_cntryInHeader = [j for j in range(len(inventoryHeaderRow)) if inventoryHeaderRow[j] == 'gglAddress'][0]
    tmpRow = deepcopy(inventoryDataReadRaw[i])
    rowNumInMapDepots = [j for j in range(len(depotMapFromNames)) if depotMapFromNames[j] == depotNamesInventoryRawNotUnique[i]][0]
    tmpRow[ix_cntryInHeader] = depotMapToNames[rowNumInMapDepots]
    inventoryDataRead.append(deepcopy(tmpRow))
depotNamesInventory = list(set(columnByName(inventoryDataRead, inventoryHeaderRow, 'gglAddress')))    
itemNamesInventory = list(set(columnByName(inventoryDataRead, inventoryHeaderRow, 'ItemName')))
inventoryDataRead = deepcopy(changeColType(inventoryDataRead, inventoryHeaderRow, 'Total', 'int'))



inventoryByDepotItemD = {}
for in_depot in depotNamesMapTo:
  for nn_item in itemNamesInventory:
    itemColNum = [i for i in range(len(inventoryHeaderRow)) if inventoryHeaderRow[i] == 'ItemName'][0]
    depotColNum = [i for i in range(len(inventoryHeaderRow)) if inventoryHeaderRow[i] == 'gglAddress'][0]
    tmpSubset = [i for i in range(len(inventoryDataRead)) if in_depot == inventoryDataRead[i][depotColNum] and nn_item == inventoryDataRead[i][itemColNum]]
    sumItems = sum([columnByName(inventoryDataRead, inventoryHeaderRow, 'Total')[i] for i in tmpSubset])
    inventoryByDepotItemD.update({(in_depot, nn_item) : sumItems})
    
depotInWhichCountry = {}
for in_depot in depotNamesMapTo:
    #itemColNum = [i for i in range(len(inventoryHeaderRow)) if inventoryHeaderRow[i] == 'ItemName'][0]
    depotColNum = [i for i in range(len(inventoryHeaderRow)) if inventoryHeaderRow[i] == 'gglAddress'][0]
    myCountry_ix = [i for i in range(len(inventoryHeaderRow)) if inventoryHeaderRow[i] == 'gglCountry'][0]
    tmpSubset = [i for i in range(len(inventoryDataRead)) if in_depot == inventoryDataRead[i][depotColNum]][0]
    #sumItems = sum([columnByName(inventoryDataRead, inventoryHeaderRow, 'Total')[i] for i in tmpSubset])
    depotInWhichCountry.update({(in_depot) : inventoryDataRead[tmpSubset][myCountry_ix]})
    
#raise NameError('Stop for depot subset')    

#------------------------------------------------------------------------------
# Item Weight Data
if 1 == 1:
  [itemAttributesHeaderRow, itemAttributesDataRead] = f_myReadCsv(inputPath + itemAttributesFileName)
  # THIS OPERATION COMPLETELY CHANGES THE ORDER.  FIX!!!!
  # AND CHECK OTHER INSTANCES
  itemNamesAttribute = columnByName(itemAttributesDataRead, itemAttributesHeaderRow, 'ItemName')
  if len(itemNamesAttribute) != len(list(set(itemNamesAttribute))):
    raise NameError('You have duplicate items in your item attributes')
  itemAttributesDataRead = deepcopy(changeColType(itemAttributesDataRead, itemAttributesHeaderRow, 'WeightMetricTon', 'float'))
  itemAttributesDataRead = deepcopy(changeColType(itemAttributesDataRead, itemAttributesHeaderRow, 'CubicMeters', 'float'))
  itemWeightsD = dict(zip(itemNamesAttribute, columnByName(itemAttributesDataRead, itemAttributesHeaderRow, 'WeightMetricTon')))
  itemVolumesD = dict(zip(itemNamesAttribute, columnByName(itemAttributesDataRead, itemAttributesHeaderRow, 'CubicMeters')))
 
 
 

#------------------------------------------------------------------------------
# TIMES TO GET THERE AND COSTS
if createLargeDictionariesFromScratch_Cost:
  indent = '        '
  print str(datetime.now()) + indent + indent + '  CreatingCostMatrix'
  # Read in the files
  [gglDistancesHeaderRow, gglDistancesDataRead] = f_myReadCsv(inputPath + drivingDistanceMatrixFileName)


##################################JAMESSTART##########################
  [contractorHead, contractorData] = f_myReadCsv(inputPath + "fakeContractorDataJames.csv")
  mapOriginalToCopies = {}
  
  contractor_gglDistancesHeaderRow = [] #Alter distanceDrivingmatrix data
  contractor_gglDistancesDataRead = []

  contractor_gglDistancesHeaderRow = deepcopy(gglDistancesHeaderRow)
  #contractor_gglDistancesHeaderRow.append("Contractor")  # Add Contractor Row
  contractor_gglDistancesHeaderRow[1] = contractor_gglDistancesHeaderRow[1] + "_" + contractorHead[0] #Alter city names

  contractor_depotWhichToUseHeaderRow = []
  contractor_depotWhichToUseRead = []
  [depotWhichToUseHeaderRow, depotWhichToUseRead]


  for original_row in gglDistancesDataRead:
    no_contractor_row = deepcopy(original_row)
    no_contractor_row.append("None")
    contractor_gglDistancesDataRead.append(no_contractor_row)


    for contractor_row in contractorData:
      contractorCity = contractor_row[5]
      

      if contractorCity == original_row[1]:
        new_row = deepcopy(original_row)
        new_row[12] += contractor_row[2]
        new_row[1] += "_" + contractor_row[0] #Alter city names
        #new_row.append(contractor_row[0]) # Add Contractor Row
        contractor_gglDistancesDataRead.append(new_row)


  gglDistancesHeaderRow = contractor_gglDistancesHeaderRow #Remap original data to altered data
  gglDistancesDataRead = contractor_gglDistancesDataRead












  print(contractor_gglDistancesHeaderRow)
  for row in contractor_gglDistancesDataRead:
    print(row)
  #sys.exit()

#Notes

#Altering distance driving matrix does not seem to effect output








# Base node for noncontractor transportation? Or assign internal transportation as its own contractor?

##################################JAMESEND##########################



  depotNamesDistances = list(set(columnByName(gglDistancesDataRead, gglDistancesHeaderRow, 'depotGglAddressAscii')))
  disasterLocationsDistances = list(set(columnByName(gglDistancesDataRead, gglDistancesHeaderRow, 'disasterGglAddressAscii')))
  [transParamsHeaderRow, transParamsDataRead] = f_myReadCsv(inputPath + transporationParametersFileName)
  transModesTransParams = list(set(columnByName(transParamsDataRead, transParamsHeaderRow, 'Mode')))
  [latLongDepotsHeaderRow, latLongDepotsRead] = f_myReadCsv(inputPath + depotLatLongFileName)
  






##################################JAMESSTART##########################
  [contractorHead, contractorData] = f_myReadCsv(inputPath + "fakeContractorDataJames.csv")
  mapOriginalToCopies = {}
  
  contractor_gglDistancesHeaderRow = [] #Alter distanceDrivingmatrix data
  contractor_gglDistancesDataRead = []

  contractor_gglDistancesHeaderRow = deepcopy(gglDistancesHeaderRow)
  #contractor_gglDistancesHeaderRow.append("Contractor")  # Add Contractor Row
  contractor_gglDistancesHeaderRow[1] = contractor_gglDistancesHeaderRow[1] + "_" + contractorHead[0] #Alter city names

  contractor_depotWhichToUseHeaderRow = []
  contractor_depotWhichToUseRead = []
  [depotWhichToUseHeaderRow, depotWhichToUseRead]


  for original_row in gglDistancesDataRead:
    no_contractor_row = deepcopy(original_row)
    no_contractor_row.append("None")
    contractor_gglDistancesDataRead.append(no_contractor_row)


    for contractor_row in contractorData:
      contractorCity = contractor_row[5]
      

      if contractorCity == original_row[1]:
        new_row = deepcopy(original_row)
        new_row[12] += contractor_row[2]
        new_row[1] += "_" + contractor_row[0] #Alter city names
        #new_row.append(contractor_row[0]) # Add Contractor Row
        contractor_gglDistancesDataRead.append(new_row)


  gglDistancesHeaderRow = contractor_gglDistancesHeaderRow #Remap original data to altered data
  gglDistancesDataRead = contractor_gglDistancesDataRead











  contractor_latLongDepotsHeaderRow = []
  contractor_latLongDepotsRead = []


  contractor_latLongDepotsHeaderRow = deepcopy(latLongDepotsHeaderRow)
  contractor_latLongDepotsHeaderRow[1] = latLongDepotsHeaderRow[1] + "_" + contractorHead[0] #Alter city names


  for original_row in contractor_latLongDepotsRead:
    no_contractor_row = deepcopy(original_row)
    no_contractor_row[1] += "None"
    contractor_latLongDepotsRead.append(no_contractor_row)


    for contractor_row in contractorData:
      contractorCity = contractor_row[5]
      

      if contractorCity == original_row[1]:
        new_row = deepcopy(original_row)
        new_row[1] += "_" + contractor_row[0] #Alter city names
        contractor_latLongDepotsRead.append(new_row)






  for row in contractor_latLongDepotsRead:
    print(row)
  #sys.exit()

#Notes

#Altering distance driving matrix does not seem to effect output








# Base node for noncontractor transportation? Or assign internal transportation as its own contractor?

##################################JAMESEND##########################

































  [latLongDisastersHeaderRow, latLongDisastersRead] = f_myReadCsv(inputPath + disasterLatLongFileName)









  # This converts many of the columns to actual numbers
  indent = '        '

  print str(datetime.now()) + indent + indent + '  CreatingCostMatrix - part 2'
  transParamsDataRead = deepcopy(changeColType(transParamsDataRead, transParamsHeaderRow, 'Number', 'float'))
  latLongDepotsRead = deepcopy(changeColType(latLongDepotsRead, latLongDepotsHeaderRow, 'gglLat', 'float'))
  latLongDepotsRead = deepcopy(changeColType(latLongDepotsRead, latLongDepotsHeaderRow, 'gglLong', 'float'))
  latLongDisastersRead = deepcopy(changeColType(latLongDisastersRead, latLongDisastersHeaderRow, 'gglLong', 'float'))
  latLongDisastersRead = deepcopy(changeColType(latLongDisastersRead, latLongDisastersHeaderRow, 'gglLat', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'disasterGglLat', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'disasterGglLong', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'depotGglLat', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'depotGglLong', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'drivingTime_hrs', 'float'))
  gglDistancesDataRead = deepcopy(changeColType(gglDistancesDataRead, gglDistancesHeaderRow, 'distance_km', 'float'))

if 1 == 1:  
  print str(datetime.now()) + indent + indent + '  CreatingCostMatrix - part 3'
  # Check to make sure that all the disasters and depots are actually in the distance matrix and lat longs
  if len(set(depotNamesInventory) - set(depotNamesDistances)) > 0:
    print set(depotNamesInventory) - set(depotNamesDistances)
    raise NameError('Youve read in costs and initial supplies, but youve read in depots with supplies that are not in cost matrix (see last printed objects for discrepency)')
  if len(set(disasterLocationsDisaster) - set(disasterLocationsDistances)) > 0:
    print set(disasterLocationsDisaster) - set(disasterLocationsDistances)
    raise NameError('Youve read in costs and initial supplies, but youve read in disaters with demands that are not in cost matrix (see last printed objects for discrepency)')
  if len(set(depotNamesInventory) - set(columnByName(latLongDepotsRead, latLongDepotsHeaderRow, 'gglAddressAscii'))) > 0:
    raise NameError('You\'re missing some lat longs in your depots')
  if len(set(disasterLocationsDisaster) - set(columnByName(latLongDisastersRead, latLongDisastersHeaderRow, 'gglAddressAscii'))) > 0:
    raise NameError('You\'re missing some lat longs in your disasters')
    
  if len(set(itemNamesInventory) - set(itemNamesAttribute)) > 0:
    print set(itemNamesInventory) - set(itemNamesAttribute)
    raise NameError('Youve read in item inventory and item attributes, but you have inventory that you dont have attributes for (see last printed objects for discrepency)')



  print str(datetime.now()) + indent + indent + '  CreatingCostMatrix - part 4'  
  myPairs = []
  for i in range(len(depotNamesInventory)):
    for j in range(len(disasterLocationsDisaster)):  
      myPairs.append((depotNamesInventory[i], disasterLocationsDisaster[j]))    

  costPairs = []
  for i in range(len(depotNamesDistances)):
    for j in range(len(disasterLocationsDistances)):  
      costPairs.append((depotNamesDistances[i], disasterLocationsDistances[j]))    
     
         
  if len(set(myPairs) - set(costPairs)) > 0:
    print set(myPairs) - set(costPairs)
    raise NameError('Youve read in costs and demands, but youve read in initial supplies and demand scenario PAIRS that are not in cost matrix (see last printed objects for discrepency)')


  # Actually calculate the values
  # We cycle through the depots, the demands, and the modes, and create a time and cost for each one
  transTimeHrs = {}
  transCostPerTon = {}
  transDistKm = {}
  print str(datetime.now()) + indent + indent + '  CreatingCostMatrix - part 5'
  for i_depot in range(len(depotNamesDistances)):
    rowInLatLong = [i for i in range(len(latLongDepotsRead)) if columnByName(latLongDepotsRead, latLongDepotsHeaderRow, 'gglAddressAscii')[i] == depotNamesDistances[i_depot]][0]
    latCol = [i for i in range(len(latLongDepotsHeaderRow)) if latLongDepotsHeaderRow[i] == 'gglLat'][0]
    longCol = [i for i in range(len(latLongDepotsHeaderRow)) if latLongDepotsHeaderRow[i] == 'gglLong'][0]
    i_latLong = deepcopy([latLongDepotsRead[rowInLatLong][latCol], latLongDepotsRead[rowInLatLong][longCol]])
    # Here, we create a small dictionary that has just the depot, but all of the demands, to make looking up distances and times faster
    gglDistancesDataReadTmp = createSubMatrixByColAndVectLkup(gglDistancesDataRead, gglDistancesHeaderRow, 'depotGglAddressAscii', [depotNamesDistances[i_depot]])
    ODNamesTmp = zip([depotNamesDistances[i_depot]] * len(gglDistancesDataReadTmp), columnByName(gglDistancesDataReadTmp, gglDistancesHeaderRow, 'disasterGglAddressAscii'))  
    gglDistancesDictTmp_Hrs = dict(zip(ODNamesTmp, columnByName(gglDistancesDataReadTmp, gglDistancesHeaderRow, 'drivingTime_hrs')))
    gglDistancesDictTmp_Km = dict(zip(ODNamesTmp, columnByName(gglDistancesDataReadTmp, gglDistancesHeaderRow, 'distance_km')))
    for j_dist in range(len(disasterLocationsDisaster)):
      rowInLatLong = [i for i in range(len(latLongDisastersRead)) if columnByName(latLongDisastersRead, latLongDisastersHeaderRow, 'gglAddressAscii')[i] == disasterLocationsDisaster[j_dist]][0]
      latCol = [i for i in range(len(latLongDisastersHeaderRow)) if latLongDisastersHeaderRow[i] == 'gglLat'][0]
      longCol = [i for i in range(len(latLongDisastersHeaderRow)) if latLongDisastersHeaderRow[i] == 'gglLong'][0]
      j_latLong = [latLongDisastersRead[rowInLatLong][latCol], latLongDisastersRead[rowInLatLong][longCol]]
      i_j_dist = convertLatLongsToKm(i_latLong[0], i_latLong[1], j_latLong[0], j_latLong[1])
      for v_mode in range(len(transModesTransParams)):
        myDictKey = [depotNamesDistances[i_depot], disasterLocationsDisaster[j_dist], transModesTransParams[v_mode]]
        myFixedTime = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['FixedAddlTime_Hrs'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )
        myStretchTime = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['StretchTimeFactor'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )                
        myStretchDistance = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['StretchDistanceFactor'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )                                         
        myFixedCost = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['FixedAddlCost_USD'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )         

        myVarCostPerKm = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['VarCost_USD_ton_km'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )         
                                  
                                  
        if transModesTransParams[v_mode] == 'Truck':
          myDictKeyLkup = tuple([depotNamesDistances[i_depot], disasterLocationsDisaster[j_dist]])
          myTravelTimeGgl = gglDistancesDictTmp_Hrs[myDictKeyLkup]      
          if truckDistanceMethod == 'google': 
            myTime = myFixedTime + myTravelTimeGgl * myStretchTime
            myTravelDist = gglDistancesDictTmp_Km[myDictKeyLkup]
            myCostPerTon = myTravelDist * myStretchDistance * myVarCostPerKm + myFixedCost
          elif truckDistanceMethod == 'crowScale':
            if myTravelTimeGgl >= maxDrivingTimeCutAbove_Hrs: 
              myTime = bigMCostElim
              myCostPerTon = bigMCostElim      
            else:
              myTruckRoadKmPerCrowKm = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['TruckRoadKm_per_CrowKm'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )              
              myTruckSpeed = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['TruckKmPerHrOnRoad'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )              
            
              myTime = myFixedTime + i_j_dist * myTruckRoadKmPerCrowKm / myTruckSpeed * myStretchTime
              myCostPerTon = myFixedCost + i_j_dist * myTruckRoadKmPerCrowKm * myStretchDistance * myVarCostPerKm
          else:
            raise NameError('You don\'t have a proper truck mode.')
          if myTravelTimeGgl >= maxDrivingTimeCutAbove_Hrs: 
            myTime = bigMCostElim
            myCostPerTon = bigMCostElim
        elif transModesTransParams[v_mode] == 'Air':
          myAirSpeed = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['AirSpeed_km_hr'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )  
          myTime = myFixedTime + i_j_dist / myAirSpeed * myStretchTime
          # print ''
          # print 'myFixedTime =', myFixedTime
          # print 'i_j_dist =', i_j_dist
          # print 'myAirSpeed = ', myAirSpeed
          # print 'myStretchTime =', myStretchTime
          # print 'myTime =', myTime
          # assert False
          
          myCostPerTon = myFixedCost + i_j_dist *  myStretchDistance * myVarCostPerKm
          
        elif transModesTransParams[v_mode] == 'Sea':
          myAirSpeed = returnValuePossibleDefaults(
                                  masterList = myDictKey
                                  , lkupMat = createSubMatrixByColAndVectLkup(transParamsDataRead, transParamsHeaderRow, 'Attribute', ['BoatSpeed_km_hr'])
                                  , lkupHeader = transParamsHeaderRow
                                  , matchVectMasterToLkupTxt = ['gglAddress', None, 'Mode']
                                  , ix_defaultsInMasterTxt = ['gglAddress']
                                  , ix_finalNumTxt = 'Number'
                                  )  
          myTime = myFixedTime + i_j_dist / myAirSpeed * myStretchTime
          # print ''
          # print 'myFixedTime =', myFixedTime
          # print 'i_j_dist =', i_j_dist
          # print 'myAirSpeed = ', myAirSpeed
          # print 'myStretchTime =', myStretchTime
          # print 'myTime =', myTime
          # assert False
          
          myCostPerTon = myFixedCost + i_j_dist *  myStretchDistance * myVarCostPerKm          
          
          
        else:
          raise NameError('No Valid Mode of Transport in calcualting distances and times')
        transTimeHrs.update({tuple(myDictKey):myTime})
        transCostPerTon.update({tuple(myDictKey):myCostPerTon})
        transDistKm.update({tuple(myDictKey): i_j_dist})

  f_saveObj(transTimeHrs, 'transTimeHrs_pickleDict', inputPathPickle_Cost )
  f_saveObj(transCostPerTon, 'transCostPerTon_pickleDict', inputPathPickle_Cost )
  f_saveObj(transDistKm,  'transDistKm_pickleDict' , inputPathPickle_Cost)
  f_saveObj(transModesTransParams,  'transModesTransParams' , inputPathPickle_Cost)

  # [gglDistancesHeaderRow, gglDistancesDataRead] = f_myReadCsv(inputPath + drivingDistanceMatrixFileName)
  # depotNamesDistances = list(set(columnByName(gglDistancesDataRead, gglDistancesHeaderRow, 'depotGglAddressAscii')))
  # disasterLocationsDistances = list(set(columnByName(gglDistancesDataRead, gglDistancesHeaderRow, 'disasterGglAddressAscii')))
  # [transParamsHeaderRow, transParamsDataRead] = f_myReadCsv(inputPath + transporationParametersFileName)
  # transModesTransParams = list(set(columnByName(transParamsDataRead, transParamsHeaderRow, 'Mode')))
  # [latLongDepotsHeaderRow, latLongDepotsRead] = f_myReadCsv(inputPath + depotLatLongFileName)
  # [latLongDisastersHeaderRow, latLongDisastersRead] = f_myReadCsv(inputPath + disasterLatLongFileName)

   
else:
  print str(datetime.now()) + indent + '  Reading in trans costs files'
  transTimeHrs = f_loadObj('transTimeHrs_pickleDict', inputPathPickle_Cost )
  transCostPerTon = f_loadObj('transCostPerTon_pickleDict', inputPathPickle_Cost )
  transDistKm = f_loadObj('transDistKm_pickleDict' , inputPathPickle_Cost)
  transModesTransParams = f_loadObj('transModesTransParams' , inputPathPickle_Cost)



#------------------------------------------------------------------------------
# Calculating true demand for each item
print str(datetime.now()) + indent + '  Country\'s ability to respond'
[abilityToRespondHeaderRow, abilityToRespondData] = f_myReadCsv(inputPath + countryAbilityToRespondFileName)
abilityToRespondData = deepcopy(changeColType(abilityToRespondData, abilityToRespondHeaderRow, 'capacityToRespond', 'float'))
disasterCntryItemDomesticCapacityInPplD = {}
for i_dist in range(len(countriesOfDisastersDisaster)):
  myDistCount = countriesOfDisastersDisaster[i_dist]
  for n_item in range(len(itemNamesInventory)):
    myItem = itemNamesInventory[n_item]
    myCapacityPpl = returnValuePossibleDefaults(
                                masterList = [myDistCount, myItem]
                                , lkupMat = createSubMatrixByColAndVectLkup(abilityToRespondData, abilityToRespondHeaderRow, 'gglCountry', [myDistCount])
                                , lkupHeader = abilityToRespondHeaderRow
                                , matchVectMasterToLkupTxt = ['gglCountry', 'item']
                                , ix_defaultsInMasterTxt = ['item']
                                , ix_finalNumTxt = 'capacityToRespond'
                                )
    disasterCntryItemDomesticCapacityInPplD.update({(myDistCount, myItem):myCapacityPpl})
    

    
[betaConversionsHeaderRow, betaConversionsData] = f_myReadCsv(inputPath + betaItemConversionsFileName)
betaConversionsData = deepcopy(changeColType(betaConversionsData, betaConversionsHeaderRow, 'PersonsPerItem', 'float'))


ki_junk = 0
if createLargeDictionariesFromScratch_Beta:    
  print str(datetime.now()) + indent + '  Beta Conversion Factors'    


  """
  betaConversionsCntryMnthDistypeItemD = {}
  k = 0
  for t_month in [-1] + range(1, 13):
    myMonth = t_month
    for j_cntry in range(len(countriesOfDisastersDisaster)):  
      myCntry = countriesOfDisastersDisaster[j_cntry]
      for m_dist in range(len(disasterWhichToUseSubset)):
        myDistType = disasterWhichToUseSubset[m_dist]
        for n_item in range(len(itemNamesInventory)):
          myItem = itemNamesInventory[n_item]
          myConversionFactor = returnValuePossibleDefaults(
                                  masterList = [myMonth, myCntry, myDistType]
                                  , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [myItem])
                                  , lkupHeader = betaConversionsHeaderRow
                                  , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                                  , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                                  , ix_finalNumTxt = 'PersonsPerItem'
                                  )
          
          betaConversionsCntryMnthDistypeItemD.update({(myCntry, myMonth, myDistType, myItem): myConversionFactor})
  #                                , ix_defaultsInMasterTxt = ['gglCountry', 'Month', 'Disaster Type']    
          #if k % 1000 == 0:
          #  print '--' + str(datetime.now()) + ' ---- k = ' + str(k) + ' of ' + str(len(countriesOfDisastersDisaster) * 14 * len(disasterWhichToUseSubset) * len(itemNamesInventory))
          k += 1
  """    
  #print str(datetime.now()) + indent + '  Beta Conversion Factors finished'
  #raise NameError('Stop sep 5')
  
  print str(datetime.now()) + indent + '  Disasters\' true demand per item all months (i.e., ignoring month)'
  demandPerDisasterperItem_NoMonth = {}


  for nn_item in itemNamesInventory:
    kCount = 0
    for kn_dist in disasterIDVect:
      kn_subLoc = disasterIDVect_SubLoc[kCount]
      myCountry = disasterLocToCountryD[disasterGglAddressD[(kn_dist, kn_subLoc)]]
      myPplAffected = max(disasterTotAffectedD[(kn_dist, kn_subLoc)] - disasterCntryItemDomesticCapacityInPplD[(myCountry, nn_item)], 0)
      betaTemp = returnValuePossibleDefaults(
                                  masterList = [-1, myCountry, disasterDistTypeD[kn_dist]]
                                  , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [nn_item])
                                  , lkupHeader = betaConversionsHeaderRow
                                  , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                                  , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                                  , ix_finalNumTxt = 'PersonsPerItem'
                                  )
      #betaTemp =  deepcopy(betaConversionsCntryMnthDistypeItemD[(myCountry, -1, disasterDistTypeD[kn_dist], nn_item)])
      if  betaTemp == 0 or betaTemp > betaConversion_zeroDemandThreshold:
        itemsNeeded = 0
      else:
        itemsNeeded = myPplAffected / betaTemp
      if itemsNeeded > 1e-1:
        demandPerDisasterperItem_NoMonth.update(deepcopy({(kn_dist, kn_subLoc, nn_item) : itemsNeeded}))
      else:
        ki_junk += 1
        
      if kn_dist == 'ID:9841':
        print kn_dist
        print kCount
        print itemsNeeded
        print kn_subLoc
        print myCountry
        print  myPplAffected
        print  betaTemp
        
      kCount += 1  
      
        

      
      
      
  #raise NameError('wwwww')
  print 'You had', ki_junk, 'sublocations with zero emand'

  print str(datetime.now()) + indent + '  Disasters\' true demand per item all months (i.e, month by month)'
  demandPerDisasterperItem_MonthByMonthWithDefaultD = {}
  disasterItemTotAffectedNetNonZeroD = {}

  for nn_item in itemNamesInventory:
    kCount = 0
    for kn_dist in disasterIDVect:
      kn_subLoc = disasterIDVect_SubLoc[kCount]
      if disasterMonthD[kn_dist] in range(1,13):
        tmpMonth = disasterMonthD[kn_dist]
      else:
        tmpMonth = -1
      myCountry = disasterLocToCountryD[disasterGglAddressD[(kn_dist, kn_subLoc)]]
      myPplAffected = max(disasterTotAffectedD[(kn_dist, kn_subLoc)] - disasterCntryItemDomesticCapacityInPplD[(myCountry, nn_item)], 0)
      betaTemp = returnValuePossibleDefaults(
                                  masterList = [tmpMonth, myCountry, disasterDistTypeD[kn_dist]]
                                  , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [nn_item])
                                  , lkupHeader = betaConversionsHeaderRow
                                  , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                                  , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                                  , ix_finalNumTxt = 'PersonsPerItem'
                                  )    
      if  betaTemp == 0 or betaTemp > betaConversion_zeroDemandThreshold:
        itemsNeeded = 0
      else:
        itemsNeeded = myPplAffected / betaTemp
      if itemsNeeded > 1e-3:
        demandPerDisasterperItem_MonthByMonthWithDefaultD.update(deepcopy({(kn_dist, kn_subLoc, nn_item) : itemsNeeded}))
        disasterItemTotAffectedNetNonZeroD.update({(kn_dist, kn_subLoc, nn_item): myPplAffected})
      kCount += 1
      
      
      
      
  f_saveObj(demandPerDisasterperItem_MonthByMonthWithDefaultD, 'demandPerDisasterperItem_MonthByMonthWithDefaultD', inputPathPickle_Beta )
  f_saveObj(disasterItemTotAffectedNetNonZeroD, 'disasterItemTotAffectedNetNonZeroD', inputPathPickle_Beta )
  f_saveObj(demandPerDisasterperItem_NoMonth,  'demandPerDisasterperItem_NoMonth' , inputPathPickle_Beta)



   
else:
  print str(datetime.now()) + indent + '  Reading in demand per disaster'
  demandPerDisasterperItem_MonthByMonthWithDefaultD = f_loadObj('demandPerDisasterperItem_MonthByMonthWithDefaultD', inputPathPickle_Beta )
  disasterItemTotAffectedNetNonZeroD = f_loadObj('disasterItemTotAffectedNetNonZeroD', inputPathPickle_Beta )
  demandPerDisasterperItem_NoMonth = f_loadObj('demandPerDisasterperItem_NoMonth' , inputPathPickle_Beta)    
       
if createLargeDictionariesFromScratch_Beta:
  raise NameError('You just created large Beta files.  Rerun again with "createLargeDictionariesFromScratch_Beta" set to False')      

print('Doing min items pr country')

minInventoryPerCountry_ItemD = {} 
for nn_item in itemNamesInventory:
    kCount = 0
    for kn_country in minInventoryPerCountryD.keys():
      kn_subLoc = minInventoryPerCountryD.keys()[kCount]
      myCountry = kn_subLoc
      #myPplAffected = minInventoryPerCountryD[myCountry]
      myPplAffected = max(minInventoryPerCountryD[myCountry] - disasterCntryItemDomesticCapacityInPplD[(myCountry, nn_item)], 0)
      betaTemp = returnValuePossibleDefaults(
                                  masterList = [-1, myCountry, 'JunkDisasterType']
                                  , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [nn_item])
                                  , lkupHeader = betaConversionsHeaderRow
                                  , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                                  , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                                  , ix_finalNumTxt = 'PersonsPerItem'
                                  )
      #betaTemp =  deepcopy(betaConversionsCntryMnthDistypeItemD[(myCountry, -1, disasterDistTypeD[kn_dist], nn_item)])
      if  betaTemp == 0 or betaTemp > betaConversion_zeroDemandThreshold:
        itemsNeeded = 0
      else:
        itemsNeeded = myPplAffected / betaTemp
      if itemsNeeded > 1e-1:
        minInventoryPerCountry_ItemD.update(deepcopy({(myCountry, nn_item) : itemsNeeded}))
      else:
        minInventoryPerCountry_ItemD.update(deepcopy({(myCountry, nn_item) : 0.}))
      kCount += 1
#raise NameError('Stop99')      

# a = {}
# for k in disasterItemTotAffectedNetNonZeroD.keys():
  # if k[2] == 'JerryCanGen':
    # a.update({k: disasterItemTotAffectedNetNonZeroD[k]})  
  
# b = {}
# for k in disasterItemTotAffectedNetNonZeroD.keys():
  # if k[2] == 'JerryCanGen':
    # a.update({k: disasterItemTotAffectedNetNonZeroD[k]})  

  
# assert False
  
#raise NameError('S S S Stop')      
#    if itemsNeeded > 1e-3:    
#      demandPerDisasterperItem_MonthByMonthWithDefaultD.update({(kn_dist, nn_item): itemsNeeded})
#      disasterItemTotAffectedNetNonZeroD.update({(kn_dist, nn_item): myPplAffected})

"""
#------------------------------------------------------------------------------
# Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
for nn_item in itemNamesInventory:
  miniDict = f_extractSubDict(demandPerDisasterperItem_NoMonth, [1], [nn_item])
  maxDemandThisItem = miniDict[f_keyWithMaxVal(miniDict)]
  inventoryByDepotItemD.update({(dummyNodeName, nn_item): maxDemandThisItem + 1000})

maxCost = transCostPerTon[f_keyWithMaxVal(transCostPerTon)] * 100
maxTime = transTimeHrs[f_keyWithMaxVal(transTimeHrs)] * 100
for jn_disaster in disasterLocationsDisaster:
  for vn_mode in transModesTransParams:
    transTimeHrs.update({(dummyNodeName, jn_disaster, vn_mode): maxTime })
    transCostPerTon.update({(dummyNodeName, jn_disaster, vn_mode): maxCost})
myKeysInfeasibleDriving = [k for k in transTimeHrs.keys() if transTimeHrs[k] == 1000000]
for k in myKeysInfeasibleDriving:
  transTimeHrs.update({k: maxTime })
  transCostPerTon.update({k: maxCost})  
"""