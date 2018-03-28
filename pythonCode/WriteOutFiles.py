# Here is a list of all the dictionaries and variables I think I need to think this through

# DICTIONARIES
# demandPerDisasterperItem_MonthByMonthWithDefaultD (distID, item): demand
# demandPerDisasterperItem_NoMonth
# transCostPerTon (i, j, mode): cost
# transTimeHrs  (i, j, mode): time
# inventoryByDepotItemD (i, item) : numItems
# disasterTotAffectedD (distID): TotAff
# disasterGglAddressD (distID): Address
# disasterGglCountryD (distID): Country
# disasterDistTypeD (distID): DistType
# disasterMonthD (distID): Month
# disasterProbD (distID): Prob

# PARAMETERS
# depotNamesInventory
# disasterLocationsDisaster
# transModesTransParams
# itemNamesInventory
# dummyNodeName
# Change disasterIDs_tmp to    disasterIDsUnq_tmp

#------------------------------------------------------------------------------
print str(datetime.now()) + ' -- Writing out files'

#myDescription = 'initialTest'
#myDescription = myParamSuffix_output
myDescription = myPBSBatch_runDescription

myMacroHeader = ['myDescription'
                  , 'careAboutMonthDemand_Beta_01'
                  , 't_month_Disaster'
                  , 'numMonthsToAvg'
                  , 'setScenarioProbabilitiesTo1OverN_Flag'
                  , 'minDisasterYear'
                  , 'maxDisasterYear'
                  , 'minYearSubset'
                  , 'maxYearSubset'
                  , 'truckDistanceMethod'
                  , 'expandWhichWarehousesCarryItem_01'
                  , 'maxDrivingTimeCutAbove_Hrs'
                  , 'minTimeRequiredToRespond'
                  , 'numDisasters'
                  ]
                 

myMacroData = [myDescription
                  , careAboutMonthDemand_Beta_01
                  , t_month_Disaster
                  , numMonthsToAvg
                  , setScenarioProbabilitiesTo1OverN_Flag
                  , minDisasterYear
                  , maxDisasterYear
                  , minYearSubset
                  , maxYearSubset
                  , truckDistanceMethod
                  , expandWhichWarehousesCarryItem_01
                  , maxDrivingTimeCutAbove_Hrs
                  , minTimeRequiredToRespond
                  , str(len(disasterIDsUnq_tmp))
                  ]                  




# Write out the actual assignments of inventory to demands
if writeOutFlowFile:
  print str(datetime.now()) + indent + '  Writing out flow file'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'
                 , 'disasterID'
                 , 'warehouseID'
                 , 'disasterLocation'
                 , 'transMode'
                 , 'numUnitsMoved'
                 , 'timeHours'
                 , 'costPerTon'
                 , 'distKm' ]

  myFileToWrite = deepcopy([headerTmp])               
                 
  for i_costType in myCostsToIterateD.keys():
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():
      for (k, i, j, v) in  myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'].keys():
        myVal = deepcopy(myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'][(k, i, j, v)])
        #Added 9/16/2014
        if i == dummyNodeName:
          myTimeTmp = bigMCostDummy
          myCostTmp = bigMCostDummy
          myKmTmp = bigMCostDummy
        else:
          myTimeTmp = transTimeHrs[(i, j, v)]
          myCostTmp = transCostPerTon[(i, j, v)]
          myKmTmp = transDistKm[(i, j, v)]        
        myRow = deepcopy(myMacroData + \
                           [n_itemIter
                            , initialInventorySum] + \
                           [i_costType, i_initSupVar] + \
                           [k, i, j, v] + \
                           [myVal] + \
                           [myTimeTmp, myCostTmp, myKmTmp] \
                           )  
        if myVal != 0:
          myFileToWrite.append(myRow)
           
  f_appendOrWriteCsv(os.path.join(outputPath,'allDemandFlows.csv'), myFileToWrite, writeOverOrAppendFiles)                  
  print str(datetime.now()) + indent + '  Finished writing out flow file'                
                  
                  
 
if 1 == 1:
  print str(datetime.now()) + indent + '  Writing out trans mode summary file'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                 , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'
                 , 'transMode'] + \
                 ['numberOfUnits'] + \
                 ['numberOfUnit-KMs']
               
                 
  myFileToWrite = deepcopy([headerTmp])               
  
  for i_costType in myCostsToIterateD.keys():
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():
      for v in transModesTransParams:
        myRow = deepcopy(myMacroData + \
                           [n_itemIter
                           , initialInventorySum] + \
                           [i_costType, i_initSupVar] + \
                           [v] + \
                           [totShippedWeightedByMode[(i_costType, i_initSupVar, v)]] + \
                           [totModeKmWeighted[(i_costType, i_initSupVar, v)]] \
                           )    
        myFileToWrite.append(myRow)
           
  f_appendOrWriteCsv(os.path.join(outputPath,'sumShippingInfoByMode.csv'), myFileToWrite, writeOverOrAppendFiles) 


if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys() and 'Optimal' in myLPInitialSuppliesVariables_FlagD.keys() and 'Worst' in myLPInitialSuppliesVariables_FlagD.keys():
  print str(datetime.now()) + indent + '  Writing out balance metric file worst'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'] + \
                 ['actualObjVal'
                  , 'optimalObjVal'
                  , 'worstObjVal'
                  , 'Balance Metric']
  
  myFileToWrite = deepcopy([headerTmp])
  
  for i_costType in myCostsToIterateD.keys():
    myRow = deepcopy(myMacroData + \
                           [n_itemIter
                            , initialInventorySum] + \
                           [i_costType] + \
                           [myLPSuperDict[(i_costType, 'Actual')]['myObjNoDum']
                            , myLPSuperDict[(i_costType, 'Optimal')]['myObjNoDum']
                            , myLPSuperDict[(i_costType, 'Worst')]['myObjNoDum']
                            , myBalMetricD[i_costType]])
    myFileToWrite.append(myRow)
  f_appendOrWriteCsv(os.path.join(outputPath, 'sumBalanceMetric.csv'), myFileToWrite, writeOverOrAppendFiles)
      
elif 'Actual' in myLPInitialSuppliesVariables_FlagD.keys() and 'Optimal' in myLPInitialSuppliesVariables_FlagD.keys():
  print str(datetime.now()) + indent + '  Writing out balance metric file'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'] + \
                 ['actualObjVal'
                  , 'optimalObjVal'
                  , 'worstObjVal'
                  , 'Balance Metric']
  
  myFileToWrite = deepcopy([headerTmp])
  
  for i_costType in myCostsToIterateD.keys():
    myRow = deepcopy(myMacroData + \
                           [n_itemIter
                            , initialInventorySum] + \
                           [i_costType] + \
                           [myLPSuperDict[(i_costType, 'Actual')]['myObjNoDum']
                            , myLPSuperDict[(i_costType, 'Optimal')]['myObjNoDum']
                            , -1
                            , myBalMetricD[i_costType]])
    myFileToWrite.append(myRow)
  f_appendOrWriteCsv(os.path.join(outputPath, 'sumBalanceMetric.csv'), myFileToWrite, writeOverOrAppendFiles)      

if 1 == 2:
  print str(datetime.now()) + indent + '  Writing out summary stats file about fraction of demand met'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['myFracServed'
                  , 'myFractionOfDisastersUsingDummy'
                  , 'myItemDemandMetWeighted'
                  , 'myWeightedDemand'
                  , 'myPeopleServedPerItemShipped'
                  , 'myPeopleServedPerItemAllJUNKWITHSCALING']
                  
  
  myFileToWrite = deepcopy([headerTmp])
  myFileToWrite.append(myMacroData + \
                          [n_itemIter
                            , initialInventorySum] + \
                          [myFracServed
                            , myFractionOfDisastersUsingDummy
                            , myItemDemandMetWeighted
                            , myWeightedDemand
                            , myPeopleServedPerItemShipped
                            , myPeopleServedPerItemAll]
                            )       
  f_appendOrWriteCsv(os.path.join(outputPath, 'sumDemandMetAndPerCapita.csv'), myFileToWrite, writeOverOrAppendFiles) 




if 1 == 1:
  print str(datetime.now()) + indent + '  Writing out overall summary stats file'
  myTmpKeys = myCostsToCompareD.keys()
  myTmpKeys.sort()
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'] + \
                ['myFracServed'
                  , 'myFractionOfDisastersUsingDummy'
                  , 'myItemDemandMetWeighted'
                  , 'myWeightedDemand'
                  , 'myPeopleServedPerItemShipped'
                  , 'myPeopleServedPerItemAll'
                  , 'bigMCostDummy'] + \
                  ['objVal'
                    , 'objValPerUnitShipped'
                    , 'dualTotInv'
                    , 'dualTotInvAdj'] + \
                  ['compareObjVal_' + k for k in myTmpKeys]
                  
                  

  myFileToWrite = deepcopy([headerTmp])
  for i_costType in myCostsToIterateD.keys(): 
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():  
      myTempDual =   myLPSuperDict[(i_costType, i_initSupVar)]['dualTotInv']
      if myTempDual == None:
        myTempDualAdj = None
      else:
        myTempDualAdj = deepcopy(myTempDual + myFractionOfDisastersUsingDummyD[(i_costType, i_initSupVar)] * bigMCostDummy)
      myFileToWrite.append(myMacroData + \
                          [n_itemIter
                            , initialInventorySum] + \
                          [i_costType
                            , i_initSupVar] + \
                          [myFracServedD[(i_costType, i_initSupVar)]
                            , myFractionOfDisastersUsingDummyD[(i_costType, i_initSupVar)]
                            , myItemDemandMetWeightedD[(i_costType, i_initSupVar)]
                            , myWeightedDemandD[(i_costType, i_initSupVar)]
                            , myPeopleServedPerItemShippedD[(i_costType, i_initSupVar)]
                            , myPeopleServedPerItemAllD[(i_costType, i_initSupVar)]
                            , bigMCostDummy] + \
                          [  myLPSuperDict[(i_costType, i_initSupVar)]['myObjNoDum'] 
                            , myGenericCostPerUnitShipped[(i_costType, i_initSupVar)] 
                            , myTempDual
                            , myTempDualAdj \
                          ] + \
                          [impactOfCostOnOtherCosts[(i_costType, i_initSupVar, k)] 
                                    for k in myTmpKeys] 
                            )       
  f_appendOrWriteCsv(os.path.join(outputPath, 'summaryAll.csv'), myFileToWrite, writeOverOrAppendFiles) 


if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys():
  print str(datetime.now()) + indent + '  Writing out dual summaries by warehouse'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'] + \
                ['warehouseID'] + \
                ['myFractionOfDisastersUsingDummy'
                  , 'bigMCostDummy' ] + \
                ['rawDual'
                  , 'adjustedDual']
                  
  
  myFileToWrite = deepcopy([headerTmp])
  for i_costType in myCostsToIterateD.keys(): 
    for i_warehouse in myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_PlusDummyCost'].keys(): 
          
      myFileToWrite.append(myMacroData + \
                          [n_itemIter
                            , initialInventorySum] + \
                          [i_costType
                            , 'Actual'] + \
                          [i_warehouse] + \
                          [myFractionOfDisastersUsingDummyD[(i_costType, 'Actual')]
                             , bigMCostDummy ] + \
                          [myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_UnAdj'][i_warehouse]
                              , myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_PlusDummyCost'][i_warehouse] \
                          ]
                            )       
  f_appendOrWriteCsv(os.path.join(outputPath, 'dualsByWarehouse.csv'), myFileToWrite, writeOverOrAppendFiles) 


if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys() and writeOutDualsByWarehouseAndDisaster:
  print str(datetime.now()) + indent + '  Writing out dual details by warehouse disaster location'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'] + \
                ['warehouseID'] + \
                ['disasterID'] + \
                ['myFractionOfDisastersUsingDummy'
                  , 'bigMCostDummy' ] + \
                ['rawDual']
                  
  
  myFileToWrite = deepcopy([headerTmp])
  for i_costType in myCostsToIterateD.keys(): 
    for (k, i) in myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_All'].keys(): 
      myVal = deepcopy(myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_All'][(k, i)] )
      if myVal != 0:
        myFileToWrite.append(myMacroData + \
                                [n_itemIter
                                  , initialInventorySum] + \
                                [i_costType
                                  , 'Actual'] + \
                                [i] + \
                                [k] + \
                                [myFractionOfDisastersUsingDummyD[(i_costType, 'Actual')]
                                   , bigMCostDummy ] + \
                                [myVal] \
                                 )        
  f_appendOrWriteCsv(os.path.join(outputPath, 'dualsByWarehouseAndDisaster.csv'), myFileToWrite, writeOverOrAppendFiles) 

if 1 == 1:
  print str(datetime.now()) + indent + '  Writing out optimal inventory location by warehouse'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['objCostType'
                 , 'initialSuppliesVarFlag'] + \
                ['warehouseID'] + \
                ['startingInventory'
                  , 'optimalInventory' ]
                  
  
  myFileToWrite = deepcopy([headerTmp])
  for i_costType in myCostsToIterateD.keys(): 
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():
      for i_warehouse in myLPSuperDict[(i_costType, i_initSupVar)]['myOptInvNoDum'].keys(): 
            
        myFileToWrite.append(myMacroData + \
                            [n_itemIter
                              , initialInventorySum] + \
                            [i_costType
                              , i_initSupVar] + \
                            [i_warehouse] + \
                            [inventory_tmpD[i_warehouse]
                                , myLPSuperDict[(i_costType, i_initSupVar)]['myOptInvNoDum'][i_warehouse] \
                            ]
                              )       
  f_appendOrWriteCsv(os.path.join(outputPath, 'optimalInventoryByWarehouse.csv'), myFileToWrite, writeOverOrAppendFiles) 
  


if plotEffFront_01 == 1:
  print str(datetime.now()) + indent + '  Writing out Efficient Frontier Data and Plot'
  headerTmp = myMacroHeader   + \
                ['n_itemIter'
                  , 'initialInventorySum'] + \
                ['optimizeTag'
                 , 'constrainerTag'
                 , 'initialSuppliesVarFlag'] + \
                ['ef_pointID'] + \
                ['ef_constraintPoint'
                  , 'ef_optimizerObjVal'] + \
                ['ef_actualConstrainerPoint'
                  , 'ef_actualOptimizerPoint']                  
  
  myFileToWrite = deepcopy([headerTmp])
  keysSorted = ef_constrPointD.keys()
  keysSorted.sort()
  for i_key in keysSorted: 
    if 'Actual' in myLPInitialSuppliesVariablesNoWorst_FlagD.keys():
      myTmpX = ef_tmpSuperDict[('con', 'Actual')]['myObjNoDum']
      myTmpY = ef_tmpSuperDict[('opt', 'Actual')]['myObjNoDum']
    else:
      myTmpX = 'DidntCalcActual'
      myTmpY = 'DidntCalcActual'
    
    myFileToWrite.append(myMacroData + \
                            [n_itemIter
                              , initialInventorySum] + \
                            [optimizeTag
                              , constrainerTag
                              , initiSupplyVar_TempFlag] + \
                            [i_key] + \
                            [ef_constrPointD[i_key]
                              , ef_optimatlObjVal[i_key]] + \
                            [myTmpX
                               , myTmpY] \
                             )        
  f_appendOrWriteCsv(os.path.join(outputPath, 'ef_frontierData.csv'), myFileToWrite, writeOverOrAppendFiles) 

print 'Samoa min required is manual'
print 'Palau and other countries with no disasters are manually removed in the StochLP function itself'