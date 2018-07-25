# File Names
betaItemConversionsFileName = 'betaItemConversions.csv'
countryAbilityToRespondFileName = 'countryAbilityToRespond.csv'
depotInventoryFileName = 'depotInventoryData.csv'
depotLatLongFileName = 'depotLatLong.csv'
depotWhichToUseReadInvFileName = 'depotsWhichToInclude.csv'
disasterCountryWhichToUseReadInFileName = 'disasterCountryWhichToInclude.csv'
depotWhichToMapToFileName = 'depotsWhichToMapTo.csv'
disasterLatLongFileName = 'disasterLatLong.csv'
disasterTotAffectedFileName = 'disasterAffectedData.csv'
disasterWhichTypeToUseFileName = 'disasterTypeWhichToUse.csv'
drivingDistanceMatrixFileName = 'drivingDistanceMatrix.csv'
gglCountryContinentLkupFileName = 'gglCountryContinentLkup.csv'
transporationParametersFileName = 'transporationParameters.csv'
itemAttributesFileName = 'itemAttributes.csv'
carrierListFileName = 'fakeCarrierDataJames.csv'
itemCarrierConversionFileName = 'fakeCarrierItemConversionRates.csv'


# Are all scenario probabilities set to 1/n?  (Possible values are 0 or 1)
setScenarioProbabilitiesTo1OverN_Flag = 1


# Are the initial supplies variable.  If so, the program will rearrange them
#     optimally.  If not, the input supplies will be use.  Legal values are 0 or 1.
#areInitialSuppliesVariables_Flag = 0



# What to write out
# myFileNames = ['DemandAssignments.csv', 'SummaryScenario.csv', 'SummaryOverall.csv', 'InitialSupplies.csv', 'InitialSuppliesFlat.csv']
#mySetOfFilesToWrite = [0, 2, 3, 4]




minDisasterYear = 1900
maxDisasterYear = 2017

#minDisasterYear = 2009
#maxDisasterYear = 2009



truckDistanceMethod = 'google' #'google' 'crowScale'
maxDrivingTimeCutAbove_Hrs = 100



# When the optimization routine sets up the dummy supply node, how much should that cost?
bigMCostDummy = 10000
bigInventoryDummy = 1000000

# In the original files, we set the time and cost to be 1e6 if it is infeasible (i.e., for the road link from
#    Canada to Australia)  This parameter is necessary so that the optimization routine can identify infeasible
#    arcs and delete them.
bigMCostElim = 1e6

dummyNodeName = 'XDummy'




# If an item can serve above this number of people, then it can sserven infinite people, and the demand for that region/item will be set to zero.
# Also, automatically, if the persons per item is zero, this is interpreted as zero demand for the item.
betaConversion_zeroDemandThreshold = 1000000