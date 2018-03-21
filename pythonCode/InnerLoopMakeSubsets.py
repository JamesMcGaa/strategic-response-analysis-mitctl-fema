indent = '        '

print ''
print str(datetime.now()) + ' -- Starting inner loop for '
print str(datetime.now()) + indent * 2 + ' n_itemIter = ' + str(n_itemIter)
print str(datetime.now()) + indent * 2 + ' initialInventoryToTest = ' + str(initialInventoryToTest)
print str(datetime.now()) + indent * 2 + ' t_month_Disaster = ' + str(t_month_Disaster)
print str(datetime.now()) + indent * 2 + ' minYearSubset = ' + str(minYearSubset)
print str(datetime.now()) + indent * 2 + ' maxYearSubset = ' + str(maxYearSubset)
#------------------------------------------------------------------------------
# Here, we take the parameters and create some temporary files to be fed into
#    the optimization routine
inventory_tmpD_tmp = f_extractSubDict(inventoryByDepotItemD, [1], [n_itemIter])
currentWarehouses = list(zip(*inventory_tmpD_tmp.keys())[0])
if expandWhichWarehousesCarryItem_01 == 1:
  missingWarehouses = [i for i in depotNamesDistances if i not in currentWarehouses]
  for i_depot in missingWarehouses:
    inventory_tmpD_tmp.update({(i_depot, n_itemIter): 0})
elif expandWhichWarehousesCarryItem_01 != 0:
  raise NameError('You do not have a valid value for expandWhichWarehousesCarryItem_01')

  

  
 
if careAboutMonthDemand_Beta_01 == 1:
  demand_tmpD_tmp = f_extractSubDict(demandPerDisasterperItem_MonthByMonthWithDefaultD, [2], [n_itemIter])
elif careAboutMonthDemand_Beta_01 == 0:
  demand_tmpD_tmp = f_extractSubDict(demandPerDisasterperItem_NoMonth, [2], [n_itemIter])
else:
  raise NameError('You don\'t have a valid careAboutMonthDemand_Beta_01')

minInvItem_tmp2 = f_extractSubDict(minInventoryPerCountry_ItemD, [1], [n_itemIter])
cnt_min_list = [x[0] for x in minInvItem_tmp2.keys()]
minInvItem_tmp = {}
for i_cnt in cnt_min_list:
  minInvItem_tmp.update({i_cnt: minInvItem_tmp2[(i_cnt, n_itemIter)]})

  
  
inventoryNames = column(inventory_tmpD_tmp.keys(), 0)
#inventoryNamesNoDummy = [i for i in inventoryNames if i != dummyNodeName]
disasterIDsUnq = list(set(column(demand_tmpD_tmp.keys(), 0)))
disasterIDsWithSubLocUnq = list(set(zip(column(demand_tmpD_tmp.keys(), 0), column(demand_tmpD_tmp.keys(), 1)) ))


demandAddressesUnq = list(set([disasterGglAddressD[i] for i in disasterIDsWithSubLocUnq]))


costPerItem_tmpD = {}
timePerItem_tmpD = {}
for in_depot in inventoryNames:
  for jn_demandAddress in demandAddressesUnq:
    for vn_mode in transModesTransParams:
      myDictKey = (in_depot, jn_demandAddress, vn_mode)
      # Added this IF on 9/20/2014
      if transTimeHrs[myDictKey] <= min(minTimeRequiredToRespond, bigMCostElim):
        costPerItem_tmpD.update({myDictKey: transCostPerTon[myDictKey] * itemWeightsD[n_itemIter]})
        timePerItem_tmpD.update({myDictKey: transTimeHrs[myDictKey]})
      else:
        costPerItem_tmpD.update({myDictKey: bigMCostElim + 1})
        timePerItem_tmpD.update({myDictKey: bigMCostElim + 1})        



# Takes as input a number and spits back a dummy vector of starting inventories
inventory_tmpD = {}

if 'Actual' in myLPInitialSuppliesVariables_Flag_param:
  initialInventorySum = sum(inventory_tmpD_tmp.values())
  for in_depot in inventoryNames:
    inventory_tmpD.update({in_depot: inventory_tmpD_tmp[(in_depot, n_itemIter)]})  
else:
  initialInventorySum = deepcopy(initialInventoryToTest)
  for i in range(len(inventory_tmpD_tmp) - 1):
    inventory_tmpD.update({inventoryNames[i]: 0.})
  inventory_tmpD.update({inventoryNames[-1]: initialInventorySum})

# Demand subset
if t_month_Disaster == -1:
  disasterIDsUnq_tmp = deepcopy(disasterIDsUnq)
elif t_month_Disaster >=1 and t_month_Disaster <= 12:
  if careAboutMonthDemand_Beta_01 == 0:
    raise NameError('You don\'t care about the month, but you are testing the month with t_month_Disaster')
  t_monthsSet = range(t_month_Disaster, t_month_Disaster + 1 + numMonthsToAvg)
  t_monthsSet = deepcopy([(m - 1) % 12  + 1 for m in t_monthsSet])
  disasterIDsUnq_tmp = [i for i in disasterIDsUnq if disasterMonthD[i] in t_monthsSet]
else:
  raise NameError('You dont have a valid month t_month_Disaster')

disasterIDsUnq_tmp = [i for i in disasterIDsUnq_tmp if disasterYearD[i] in range(minYearSubset, maxYearSubset + 1)]  
disasterIDsWithSubLocUnq_tmp = [i for i in disasterIDsWithSubLocUnq if i[0] in disasterIDsUnq_tmp]



demand_tmpD = dict([[i, demand_tmpD_tmp[tuple(list(i) + [n_itemIter])]] for i in disasterIDsWithSubLocUnq_tmp])
demandAddress_tmpD =  dict([[i, disasterGglAddressD[i]] for i in disasterIDsWithSubLocUnq_tmp])
tmpTotalProb = sum([disasterProbD[i] for i in disasterIDsUnq_tmp])
probs_tmpD =  dict([[i, disasterProbD[i] * 1. / tmpTotalProb] for i in disasterIDsUnq_tmp])

# print ''
# print ''
# print ''
# print 'test here'
# if 1 == 1:
  # d = ('EmDat:2013-0098', 'SubLoc_00000')
  # print 'd = ', d
  # print 'demand_tmpD[d] =', demand_tmpD[d]
  # print 'demandAddress_tmpD[d] = ', demandAddress_tmpD[d]
  # print 'tmpTotalProb =', tmpTotalProb
  # print 'probs_tmpD[d] =', probs_tmpD[d[0]]


# assert False
# ------------------------------------------------------------------------------
# Final parameter definitions
myCostsToIterateDMaster = {'Cost': costPerItem_tmpD, 'Time': timePerItem_tmpD}
myCostsToCompareDMaster = {'Cost': costPerItem_tmpD, 'Time': timePerItem_tmpD, 'pureKM': transDistKm}
myLPInitialSuppliesVariables_FlagDMaster = {'Optimal': 1, 'Actual': 0, 'Worst': 3}

myCostsToIterateD = {}
for k in myCostsToIterate_param:
  myCostsToIterateD.update({k: myCostsToIterateDMaster[k]})

myCostsToCompareD = {}
for k in myCostsToCompare_param:
  myCostsToCompareD.update({k: myCostsToCompareDMaster[k]})

myLPInitialSuppliesVariables_FlagD = {}
for k in myLPInitialSuppliesVariables_Flag_param:
  myLPInitialSuppliesVariables_FlagD.update({k: myLPInitialSuppliesVariables_FlagDMaster[k]})  
  
# Added 12/1/2014 
myLPInitialSuppliesVariablesNoWorst_FlagD = {}
for k in myLPInitialSuppliesVariables_Flag_param:
  if k != 'Worst':
    myLPInitialSuppliesVariablesNoWorst_FlagD.update({k: myLPInitialSuppliesVariables_FlagDMaster[k]})  
  

# ------------------------------------------------------------------------------
# Execute the LP

#raise NameError('Stop44')
print str(datetime.now()) + ' -- Starting LPs'

myLPSuperDict = {}
for i_costType in myCostsToIterateD.keys():
  for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():
    myLPDictTmp = f_solveStochLPDisasterGurobiSubLoc3(demand_tmpD = demand_tmpD
                                              , demandAddress_tmpD = demandAddress_tmpD
                                              , probs_tmpD = probs_tmpD
                                              , disasterIDsUnq_tmp = disasterIDsUnq_tmp
                                              , disasterIDsWithSubLocUnq_tmp = disasterIDsWithSubLocUnq_tmp
                                              , inventory_tmpD = inventory_tmpD
                                              , transModesTransParams = transModesTransParams
                                              , bigMCostElim = bigMCostElim
                                              , bigMCostDummy = bigMCostDummy
                                              , costD = myCostsToIterateD[i_costType]
                                              , dummyNodeName = dummyNodeName
                                              , areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD[i_initSupVar]
                                              , depotWhichFixedSubset = depotWhichFixedSubset
                                              , minInvItemD = minInvItem_tmp
                                              , depotInWhichCountry = depotInWhichCountry
                                              )
    myLPSuperDict.update({(i_costType, i_initSupVar): myLPDictTmp}) 
    
    print str(datetime.now()) + indent + ' Finished LP cost: ' + i_costType + '  InitSuplyFlag: ' +  i_initSupVar

print str(datetime.now()) + ' -- calculating summary stats'

#raise NameError('^^STOP%%')
# This is just the number of units by each mode, not counting the miles/km
if 1 == 1:
  transDistKmD = {}
  print str(datetime.now()) + indent + '  Calculating units shipped by trans mode'
  totShippedWeightedByMode = {}
  totModeKmWeighted = {}
  for v in transModesTransParams:
    for i_costType in myCostsToIterateD.keys():
      for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():
        #print str(datetime.now()) + indent + '  Calculating units shipped by trans mode inside ' + str(v) + ' ' + str(i_costType) + ' ' + str(i_initSupVar)
        #print str(datetime.now()) + 2 * indent + '  Calculating units shipped by trans mode inside step 1'
        tmpTotShipSubDict = deepcopy(f_extractSubDict(myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum']
                                        , [3]
                                        , [v]
                                        ))
        weightedShipped = 0
        #print str(datetime.now()) + 2 * indent + '  Calculating units shipped by trans mode inside step 2'
        # for k in disasterIDsUnq_tmp:
          # weightedShipped +=  probs_tmpD[k] * sum(f_extractSubDict(tmpTotShipSubDict
                                        # , [0]
                                        # , [k]
                                        # ).values())    
        # print 'old weighted = ',  weightedShipped                                       
        weightedShipped = sum([tmpTotShipSubDict[(k, i, j, vTmp)] * probs_tmpD[k] 
                              for (k, i, j, vTmp) in tmpTotShipSubDict.keys() ])     
                            

        totShippedWeightedByMode.update({(i_costType, i_initSupVar, v): weightedShipped})
        
        modeKmTmp = 0
        #print str(datetime.now()) + 2 * indent + '  Calculating units shipped by trans mode inside step 3'
        #for (k, i, j, vTmp) in tmpTotShipSubDict.keys():
        #  modeKmTmp += round(tmpTotShipSubDict[(k, i, j, vTmp)] * probs_tmpD[k] * transDistKm[(i, j, vTmp)], 2)
        modeKmTmp = sum([tmpTotShipSubDict[(k, i, j, vTmp)] * probs_tmpD[k] * transDistKm[(i, j, vTmp)] 
                              for (k, i, j, vTmp) in tmpTotShipSubDict.keys() ])
        totModeKmWeighted.update({(i_costType, i_initSupVar, v): modeKmTmp})  
        #print str(datetime.now()) + 2 * indent + '  Calculating units shipped by trans mode inside END'
        
        
print str(datetime.now()) + indent + '  Calculating myBalMetricD'        
if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys() and 'Optimal' in myLPInitialSuppliesVariables_FlagD.keys():
  myBalMetricD = {}
  for i_costType in myCostsToIterateD.keys(): 
    myBalMetricD.update({i_costType: myLPSuperDict[(i_costType, 'Actual')]['myObjNoDum'] / (myLPSuperDict[(i_costType, 'Optimal')]['myObjNoDum'] + 1e-7)  })

    
    
    
    
    
##------------------------
# Giving me trouble on 9/7 when I just do optimal allocation
# Deleted on 9/7/2014
#if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys():
if 1 == 2:
  for i_costType in [myCostsToIterateD.keys()[0]]: 
    for i_initSupVar in [myLPInitialSuppliesVariables_FlagD.keys()[0]]:  
      myFracServed = myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemandMetNoDum'] / (myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemand'] + 1e-7)
      myFractionOfDisastersUsingDummy = myLPSuperDict[(i_costType, i_initSupVar)]['myFractionOfDisastersUsingDummy']
      myItemDemandMetWeighted = myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemandMetNoDum']
      myWeightedDemand = myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemand']

      
      
      
if 1 == 1:
  print str(datetime.now()) + indent + '  Calculating myFracServedD'     
  myFracServedD = {}
  myFractionOfDisastersUsingDummyD = {}
  myItemDemandMetWeightedD = {}
  myWeightedDemandD = {}
  
  for i_costType in myCostsToIterateD.keys(): 
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():  
      myFracServedD.update({(i_costType, i_initSupVar): myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemandMetNoDum'] / (myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemand'] + 1e-7) })
      myFractionOfDisastersUsingDummyD.update({(i_costType, i_initSupVar): myLPSuperDict[(i_costType, i_initSupVar)]['myFractionOfDisastersUsingDummy'] })
      myItemDemandMetWeightedD.update({(i_costType, i_initSupVar): myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemandMetNoDum'] })
      myWeightedDemandD.update({(i_costType, i_initSupVar): myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemand'] })
      
      
      
print str(datetime.now()) + indent + '  Calculating myDualsPerDepotAct'         
# added if on 9/7/2014   
if 'Actual' in myLPInitialSuppliesVariables_FlagD.keys():
  myDualsPerDepotAct = {}
  for i_costType in myCostsToIterateD.keys(): 
    myDualsPerDepotAct.update({i_costType:  myLPSuperDict[(i_costType, 'Actual')]['dualsInvNoDum_PlusDummyCost']})
    
# Added if 1==1 and took away "actual" on 9/7/2014  
print str(datetime.now()) + indent + '  Calculating myGenericCostPerUnitShipped'    
if 1 == 1:    
  myGenericCostPerUnitShipped = {}
  for i_costType in myCostsToIterateD.keys(): 
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():    
      myGenericCostPerUnitShipped.update({(i_costType, i_initSupVar): myLPSuperDict[(i_costType, i_initSupVar)]['myObjNoDum'] / (myLPSuperDict[(i_costType, i_initSupVar)]['myWeightedDemandMetNoDum'] + 1e-7)})

##------------------------






print str(datetime.now()) + indent +  ' Calculating summary stats 1'



#myTotDisastersDummyFlowTo = sum([myLPDictMinTimeAct['myFlow'][(k, i, j, v)] for (k, i, j, v) in myLPDictMinTimeAct['myFlow'].keys() if i == 'XDummy'])


impactOfCostOnOtherCosts = {}
for i_costType in myCostsToIterateD.keys(): 
  for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys(): 
    for i_costCompare in myCostsToCompareD.keys():
      myVal = sum(myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'][(k, i, j, v)] * 
                                                    myCostsToCompareD[i_costCompare][(i, j, v)] * 
                                                    probs_tmpD[k]
                                         for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'].keys())
      impactOfCostOnOtherCosts.update({(i_costType, i_initSupVar, i_costCompare): myVal})


  #Calculate Capita Demand and Capita Served
if 1 == 2:  
  print str(datetime.now()) +  ' -- Calculating summary stats capita inv'
  myPeopleServedPerDisaster = {}
  myPeopleDemandedPerDisaster = {}
  # n_itemIter
  # disasterItemTotAffectedNetNonZeroD
  for kn_dist in disasterIDs_tmp:
    for i_costType in [myCostsToIterateD.keys()[0]]: 
      for i_initSupVar in [myLPInitialSuppliesVariables_FlagD.keys()[0]]:
        if careAboutMonthDemand_Beta_01 == 1:
          if disasterMonthD[kn_dist] in range(1,13):
            tmpMonth = disasterMonthD[kn_dist]
          else:
            tmpMonth = -1
        else:
          tmpMonth = -1
          
        myCountry = disasterLocToCountryD[disasterGglAddressD[kn_dist]]
        betaTemp = returnValuePossibleDefaults(
                                masterList = [tmpMonth, myCountry, disasterDistTypeD[kn_dist]]
                                , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [n_itemIter])
                                , lkupHeader = betaConversionsHeaderRow
                                , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                                , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                                , ix_finalNumTxt = 'PersonsPerItem'
                                )
        myPplServed = betaTemp * sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'][(k, i, j, v)]
                                            for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'].keys()
                                              if k == kn_dist
                                                and j == disasterGglAddressD[kn_dist]
                                                ])
                                                                                                
        myPplDemanded = betaTemp *  sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'][(k, i, j, v)]
                                            for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'].keys()
                                              if k == kn_dist
                                                and j == disasterGglAddressD[kn_dist]
                                                ])                                                                                            
        myPeopleServedPerDisaster.update({kn_dist: myPplServed})      
        myPeopleDemandedPerDisaster.update({kn_dist: myPplDemanded})      
    

    
  myPeopleServedPerItemShipped = sum([myPeopleServedPerDisaster[k] * probs_tmpD[k] for k in disasterIDs_tmp] ) / (myItemDemandMetWeighted + 1e-7)
  myPeopleServedPerItemAll = sum([myPeopleDemandedPerDisaster[k] * probs_tmpD[k] for k in disasterIDs_tmp] ) / (myWeightedDemand + 1e-7)
    
    
    
    
#  START HERE 3/30/2015 ^^^^^^^^^^^^^^&&&&&&&&&&&&&&&&
# Change disasterIDs_tmp to    disasterIDsUnq_tmp
# Change efficient frontier (after testing) 
    
    
  #Calculate Capita Demand and Capita Served
  
  
  
  
  
print str(datetime.now()) + indent +  ' Calculating summary stats 1 -- myPeopleServedPerItemShippedD'

betaTmpDict = {}
for kn_dist in disasterIDsUnq_tmp:
  if careAboutMonthDemand_Beta_01 == 1:
    if disasterMonthD[kn_dist] in range(1,13):
      tmpMonth = disasterMonthD[kn_dist]
    else:
      tmpMonth = -1
  else:
    tmpMonth = -1
  disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == kn_dist])
  for kn_distSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
    myCountry = disasterLocToCountryD[disasterGglAddressD[kn_distSubLoc]]
    betaTmpDict.update({(kn_dist, kn_distSubLoc) :returnValuePossibleDefaults(
                            masterList = [tmpMonth, myCountry, disasterDistTypeD[kn_dist]]
                            , lkupMat = createSubMatrixByColAndVectLkup(betaConversionsData, betaConversionsHeaderRow, 'Item', [n_itemIter])
                            , lkupHeader = betaConversionsHeaderRow
                            , matchVectMasterToLkupTxt = ['Month', 'gglCountry', 'Disaster Type']
                            , ix_defaultsInMasterTxt = ['Disaster Type', 'Month', 'gglCountry']
                            , ix_finalNumTxt = 'PersonsPerItem'
                            )
                          }
                        )
print str(datetime.now()) + indent +  ' Just created beta dict'                            


if 1 == 1:  
  myPeopleServedPerItemShippedD = {}
  myPeopleServedPerItemAllD = {}
  print str(datetime.now()) + indent +  ' Calculating summary stats capita inv'
  myPeopleServedPerDisaster = {}
  myPeopleDemandedPerDisaster = {}
  # n_itemIter
  # disasterItemTotAffectedNetNonZeroD
  for i_costType in myCostsToIterateD.keys(): 
    for i_initSupVar in myLPInitialSuppliesVariables_FlagD.keys():  
      # print str(datetime.now()) + indent +  ' -- Inside'

      tuplesOfArcs = {}
      for kn_dist in disasterIDsUnq_tmp:  
        tuplesOfArcs.update({kn_dist: [(k, i, j, v) for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'].keys() if k == kn_dist] })
        
        
        
      
      for kn_dist in disasterIDsUnq_tmp:
        # print str(datetime.now()) + 2 * indent +  ' -- Inside step 1'
        myPplServedWholeDisaster = 0
        myPplDemandedWholeDisaster = 0
        if careAboutMonthDemand_Beta_01 == 1:
          if disasterMonthD[kn_dist] in range(1,13):
            tmpMonth = disasterMonthD[kn_dist]
          else:
            tmpMonth = -1
        else:
          tmpMonth = -1
        disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == kn_dist])
        # print str(datetime.now()) + 2 * indent +  ' -- Inside step 2'
        #tmpTupleList = [(k, i, j, v) for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'].keys() if k == kn_dist]
        #tmpTupleList = [(k, i, j, v) for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'].keys() if k == kn_dist]
        for kn_distSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
          myCountry = disasterLocToCountryD[disasterGglAddressD[kn_distSubLoc]]
          # print str(datetime.now()) + 3 * indent +  ' -- Inside step A'
          betaTemp = deepcopy(betaTmpDict[(kn_dist, kn_distSubLoc)])
          # print str(datetime.now()) + 3 * indent +  ' -- Inside step B'
          # myPplServed = betaTemp * sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'][(k, i, j, v)]
                                              # for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'].keys()
                                                # if k == kn_dist
                                                  # and j == disasterGglAddressD[kn_distSubLoc]
                                                  # ])
                                                  
                                         

          myPplServed = betaTemp * sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlowNoDum'][(k, i, j, v)]
                                              for (k, i, j, v) in tuplesOfArcs[kn_dist]
                                                if j == disasterGglAddressD[kn_distSubLoc]
                                                  and i != dummyNodeName
                                                  ])                                         
                                         
          # print str(datetime.now()) + 3 * indent +  ' -- Inside step C'                                                                                        
          # myPplDemanded = betaTemp *  sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'][(k, i, j, v)]
                                              # for (k, i, j, v) in myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'].keys()
                                                # if k == kn_dist
                                                  # and j == disasterGglAddressD[kn_distSubLoc]
                                                  # ])      


          myPplDemanded = betaTemp * sum([myLPSuperDict[(i_costType, i_initSupVar)]['myFlow'][(k, i, j, v)]
                                              for (k, i, j, v) in tuplesOfArcs[kn_dist]
                                                if j == disasterGglAddressD[kn_distSubLoc]
                                                  ])                                             

          myPplServedWholeDisaster += myPplServed
          myPplDemandedWholeDisaster += myPplDemanded
        # print str(datetime.now()) + 2 * indent +  ' -- Inside step 3'          
        myPeopleServedPerDisaster.update({kn_dist: myPplServedWholeDisaster})      
        myPeopleDemandedPerDisaster.update({kn_dist: myPplDemandedWholeDisaster})   
        # print str(datetime.now()) + 2 * indent +  ' -- Inside step 4'
        # assert False        
    

    
      myPeopleServedPerItemShippedD.update({(i_costType, i_initSupVar): sum([myPeopleServedPerDisaster[k] * probs_tmpD[k] for k in disasterIDsUnq_tmp] ) / (myItemDemandMetWeightedD[(i_costType, i_initSupVar)] + 1e-7) })
      myPeopleServedPerItemAllD.update({(i_costType, i_initSupVar): sum([myPeopleDemandedPerDisaster[k] * probs_tmpD[k] for k in disasterIDsUnq_tmp] ) / (myWeightedDemandD[(i_costType, i_initSupVar)] + 1e-7) })
      #assert False

# Change disasterIDs_tmp to    disasterIDsUnq_tmp  
if plotEffFront_01 == 1:    
  # Get the efficient frontier
  # Specifically, between time and cost
  # Here, the optimizer is the thing you want to optimize.  That is, if you said "Minmize time subject to cost
  #    being $500k or less", then "time" is your optimizer and "cost" is your constraint.  To find the efficient 
  #    frontier, it keeps optimizing the optimizer while moving the constraint between the lower and upper
  #    bounds at given steps.
  #
  #    Note that the optmization routine might or might not vary the initial placement of supplies, but it
  #    definitely optimizes the assignment of inventory to disasters (i.e., if there are 100 units in accra,
  #    and a single disaster in Kenya, the time model might fly it all, the cost model might truck it all, and
  #    the efficient frontier might fly some and truck some, even though it doesn't change where the 100 units are.


  #optimizeCostsD = timePerItem_tmpD
  #constraintCostsD = costPerItem_tmpD
  print str(datetime.now()) +  ' -- Calculating eff frontier'
  # Parameters

  
  
  optimizeCostsD = myCostsToIterateD[optimizeTag]
  constraintCostsD = myCostsToIterateD[constrainerTag]
  


  # The work  
  ef_tmpSuperDict = {}
  miniDict = {'opt': optimizeCostsD, 'con': constraintCostsD}
  for i_costType in miniDict.keys():
    for i_initSupVar in myLPInitialSuppliesVariablesNoWorst_FlagD.keys():
      ef_tmpSuperDict.update({(i_costType, i_initSupVar): f_solveStochLPDisasterGurobiCostConstraintSubLoc(demand_tmpD = demand_tmpD
                                            , demandAddress_tmpD = demandAddress_tmpD
                                            , probs_tmpD = probs_tmpD
                                            , disasterIDsUnq_tmp = disasterIDsUnq_tmp
                                            , disasterIDsWithSubLocUnq_tmp = disasterIDsWithSubLocUnq_tmp
                                            , inventory_tmpD = inventory_tmpD
                                            , transModesTransParams = transModesTransParams
                                            , bigMCostElim = bigMCostElim
                                            , bigMCostDummy = bigMCostDummy
                                            , costD = miniDict[i_costType]
                                            , costConstraintsD = constraintCostsD
                                            , constraintNumberUpperLimit = 1e100
                                            , dummyNodeName = dummyNodeName
                                            , areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariablesNoWorst_FlagD[i_initSupVar]
                                            )
                               })


  ef_myConObj_UB = sum(ef_tmpSuperDict[('opt', initiSupplyVar_TempFlag)]['myFlowNoDum'][(k, i, j, v)] * 
                                                        constraintCostsD[(i, j, v)] * 
                                                        probs_tmpD[k]
                                             for (k, i, j, v) in ef_tmpSuperDict[('opt', initiSupplyVar_TempFlag)]['myFlowNoDum'].keys())
  ef_myConObj_LB = ef_tmpSuperDict[('con', initiSupplyVar_TempFlag)]['myObjNoDum'] 

  
  myStepTmp = (ef_myConObj_UB - ef_myConObj_LB) / (myNumEffFrontPoints - 1)
  ef_constraintNumbersUpperLimitList = [ef_myConObj_LB + i * myStepTmp for i in range(myNumEffFrontPoints)]

  ef_constrPointD = dict(zip(['constraintPoint_{:03d}'.format(i) for i in range(len(ef_constraintNumbersUpperLimitList))], ef_constraintNumbersUpperLimitList))
  
  
  ef_finalSuperDict = {}
  for i_constraintNumID in ef_constrPointD.keys():
    print str(datetime.now()) + indent +  ' -- Calculating ' + i_constraintNumID
    ef_finalSuperDict.update({i_constraintNumID: f_solveStochLPDisasterGurobiCostConstraintSubLoc(demand_tmpD = demand_tmpD
                                            , demandAddress_tmpD = demandAddress_tmpD
                                            , probs_tmpD = probs_tmpD
                                            , disasterIDsUnq_tmp = disasterIDsUnq_tmp
                                            , disasterIDsWithSubLocUnq_tmp = disasterIDsWithSubLocUnq_tmp
                                            , inventory_tmpD = inventory_tmpD
                                            , transModesTransParams = transModesTransParams
                                            , bigMCostElim = bigMCostElim
                                            , bigMCostDummy = bigMCostDummy
                                            , costD = optimizeCostsD
                                            , costConstraintsD = constraintCostsD
                                            , constraintNumberUpperLimit = ef_constrPointD[i_constraintNumID]
                                            , dummyNodeName = dummyNodeName
                                            , areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariablesNoWorst_FlagD[initiSupplyVar_TempFlag]
                                            )
                               })
                               
  ef_optimatlObjVal = {}                               
  for  i_constraintNumID in ef_constrPointD.keys():                             
    ef_optimatlObjVal.update({i_constraintNumID: ef_finalSuperDict[i_constraintNumID]['myObjNoDum']}) 
        

 
  print str(datetime.now()) + indent + '  Calculating units shipped by trans mode for efficient frontier'
  ef_totShippedWeightedByMode = {}
  ef_totModeKmWeighted = {}
  for v in transModesTransParams:
    for i_efKey in ef_finalSuperDict.keys():
      tmpTotShipSubDict = deepcopy(f_extractSubDict(ef_finalSuperDict[i_efKey]['myFlowNoDum']
                                      , [3]
                                      , [v]
                                      ))
      weightedShipped = 0
      for k in disasterIDsUnq_tmp:
        weightedShipped +=  probs_tmpD[k] * sum(f_extractSubDict(tmpTotShipSubDict
                                      , [0]
                                      , [k]
                                      ).values())    
      ef_totShippedWeightedByMode.update({(i_efKey, v): weightedShipped})
      
      modeKmTmp = 0
      for (k, i, j, vTmp) in tmpTotShipSubDict.keys():
        modeKmTmp += round(tmpTotShipSubDict[(k, i, j, vTmp)] * probs_tmpD[k] * transDistKm[(i, j, v)], 2)
      ef_totModeKmWeighted.update({(i_efKey, v): modeKmTmp})      
    
    

if 1 == 2:
  print str(datetime.now()) + indent + '  plotting efficient frontier'
  keysSorted = ef_constrPointD.keys()
  keysSorted.sort()
  myX = [ef_constrPointD[k] for k in keysSorted]
  myY = [ef_optimatlObjVal[k] for k in keysSorted]
  plt.plot(myX, myY)  
  plt.plot(ef_tmpSuperDict[('con', 'Actual')]['myObjNoDum'], ef_tmpSuperDict[('opt', 'Actual')]['myObjNoDum'], 'bo')  
  plt.show()



