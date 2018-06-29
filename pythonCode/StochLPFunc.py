# On 2/26, changed line 541 and 573: these are the 2 last day constraints, where now I changed it to have ending inventory AT LEAST 
#    be the  goals, not equal

"""
import os
import sys
import random
import math
import numpy
import subprocess
from pylab import *
from statlib import stats
from pulp import *
import csv
import shutil
import fnmatch
from copy import deepcopy
from scipy.stats import norm
import time
from scipy.stats import truncnorm
from datetime import *
from gurobipy import *

def column(matrix, i):
    return [row[i] for row in matrix]




# This function calculates for each FC the lamnda, i.e., load factors
# If a demand region is equal to 2 FC's, it chooses the FC with the smallest index
def f_getLoadFactors(f_dailyDemandVect, f_costMatrix):
    whichFCNearest = [0] * len(f_dailyDemandVect)
    for i in range(len(f_dailyDemandVect)):
        whichFCNearest[i] = numpy.nonzero(array(f_costMatrix[i]) == min(array(f_costMatrix[i])))[0][0]

    sumDemandFC = [0] * len(f_costMatrix[0])
    for i in range(len(sumDemandFC)):
        a = numpy.nonzero(array(whichFCNearest) == array(i))[0]
        sumDemandFC[i] = sum(f_dailyDemandVect[a[j]] for j in range(len(a)))
    return([round(sumDemandFC[i]* 1. / sum(sumDemandFC), 4) for i in range(len(sumDemandFC))])



# This function takes the lead times and review period, and returns the horizon
def f_getTransLPHorizon(f_leadTime, f_reviewPeriod):
    return(int(math.ceil(max(f_leadTime) * 1.0 / f_reviewPeriod)*f_reviewPeriod))

"""


#*******************************************************************************

"""
# ---------------------------------------------------------------------------
# This tries to fix the issue with the long lead times
def f_solveStochLPDisasterGurobi(demandNames \
                                   , scenarioNames \
                                   , timeNames \
                                   , demand \
                                   , probs
                                   , costs \
                                   , depotNames \
                                   , supply \
                                   , costsMeasure \
                                   , supplyTotalConstraint \
                                   , supplyTotalDepotNames \
                                   , areInitialSuppliesVariables_Flag \
                                   , macroTotSupply \
                                   , macroMonth \
                                   , macroNumMonthsAvg \
                                   , macroScenarioDesc \
                                   ):
"""
    # f_solveStochLPDisasterGurobi(demandNamesScenario \
                                   # , scenarioNamesScenario \
                                   # , timeNamesScenario \
                                   # , demandD \
                                   # , scenarioProbabiltiesD \
                                   # , costsD \
                                   # , depotNamesSupply \
                                   # , initialSuppliesD \
                                   # , costsD \
                                   # , sum([initialSuppliesD[i] for i in depotNamesSupplyNoDummyUnique]) \
                                   # , depotNamesSupplyNoDummyUnique \
                                   # , 0 \
                                   #):                                   
                                 
    # demandNames = demandNamesScenario
    # scenarioNames = scenarioNamesScenario
    # timeNames = timeNamesScenario
    # demand = demandD
    # probs = scenarioProbabilitiesD
    # costs = costsD
    # depotNames = depotNamesSupply
    # supply = initialSuppliesD
    # costsMeasure = costsD
    # supplyTotalDepotNames = depotNamesSupplyNoDummyUnique
    # supplyTotalConstraint = sum([initialSuppliesD[supplyTotalDepotNames[i]] for i in range(len(supplyTotalDepotNames))]) 
    # areInitialSuppliesVariables_Flag = 1
def f_solveStochLPDisasterGurobi(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDs_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):

  #costD = myCostsToIterateD[i_costType]
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD[i_initSupVar]
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000


  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  #inventory_tmpD['Accra, Ghana'] += 1
  # myMaxKeyLength = 40
  # for i in inventory_tmpD.keys():
    # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # #> myMaxKeyLength:
      # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
  # for i in costD.keys():
    # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # costD[('Moffett', i[1], i[2])] = costD.pop(i)
  
  
  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
 
  
  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  
  
  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpD.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))

  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpD.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO
  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDs_tmp:
    #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
    pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == demand_tmpD[k], name = 'EnsureDemandSat_%s' %(k))

    #print 'wrong'
    #print inventory_tmpD.keys()
    
    for i in inventory_tmpD.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpD[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            print 'test'
            print str(i) + ' - ' + str(inventory_tmpD[i])
            print k
            print 'length'
            print len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim])
            print [costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]
            print ''
            #print x_satDemand
            #print myArcs_SatDemand
            print inventory_tmpD        
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpD[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpD[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')
      
      
  if areInitialSuppliesVariables_Flag == 1:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpD.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
      
  # Added 9/19
    
      
  m.update()
    
  print str(datetime.now()) +  '  About to Solve'
  m.optimize()
  print str(datetime.now()) +  '  Just Solved'
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  
  #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDs_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDs_tmp)

  
  #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpD.values())]) * 1. / len(disasterIDs_tmp)
  
  dualsInvNoDum_PlusDummyCost = {}
  for i in inventory_tmpD.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


  dualsInvNoDum_UnAdj = {}
  for i in inventory_tmpD.keys():
    myTmpDual = 0
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))

  dualsInvNoDum_All = {}
  for i in inventory_tmpD.keys():
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))

    

    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
    
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
  
  myOptInvNoDum = {}
  for i in inventory_tmpD.keys():
    if areInitialSuppliesVariables_Flag == 1:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
    
  myOutDict = {'myObj': myObj
                , 'myObjNoDum': myObjNoDum
                , 'myWeightedDemand': myWeightedDemand
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
              }

  
  return myOutDict
"""  
def f_solveStochLPDisasterGurobiAlsoMax(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDs_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):

  #costD = myCostsToIterateD[i_costType]
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD[i_initSupVar]
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000


  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  #inventory_tmpD['Accra, Ghana'] += 1
  # myMaxKeyLength = 40
  # for i in inventory_tmpD.keys():
    # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # #> myMaxKeyLength:
      # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
  # for i in costD.keys():
    # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # costD[('Moffett', i[1], i[2])] = costD.pop(i)
  
  
  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  inventory_tmpDTmp = deepcopy(inventory_tmpD)
  inventory_tmpDBad = deepcopy(inventory_tmpD)
 
  
  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  
  
  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDTmp.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))

  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpDTmp.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO
  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDs_tmp:
    #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
    pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == demand_tmpD[k], name = 'EnsureDemandSat_%s' %(k))

    #print 'wrong'
    #print inventory_tmpDTmp.keys()
    
    for i in inventory_tmpDTmp.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        elif areInitialSuppliesVariables_Flag == 3:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')
      
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
      
  # Added 9/19
    
      
  m.update()  

  
  
  if areInitialSuppliesVariables_Flag == 2:
    m.ModelSense = -1
  elif areInitialSuppliesVariables_Flag == 3:
    print str(datetime.now()) +  '  About to Solve worst depot'
    tmpWorstObj = -1
    tmpWorstDepot = None
    for i in inventory_tmpDBad.keys():
      #print str(datetime.now()) +  ' -- Testing depot' + str(i)
      for j in inventory_tmpDBad.keys():
        inventory_tmpDBad[j] = 0
      inventory_tmpDBad[i] = supplyTotalConstraint
      #print 'inventory vect'
      #print inventory_tmpDBad
      for k in disasterIDs_tmp:
        for i2 in inventory_tmpDTmp.keys():
          if len([costDDum[(i2, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i2, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
            m.remove(pi_inventoryBalance[(k, i2)])
            pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
      m.update()
      m.optimize()
      if m.status != GRB.status.OPTIMAL:
        print m.status
        raise NameError('Non-optimal LP')
      tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))
      #print 'tmpTmpObj = ' + str(tmpTmpObj)
      #print 'tmpWOrst  = ' + str(tmpWorstObj)
      #print 'old worst depot = ' + str(tmpWorstDepot)
      #print 'i = ' + str(i)
      if tmpTmpObj > tmpWorstObj:
        #print 'found new bad depot'
        tmpWorstObj = deepcopy(tmpTmpObj)
        tmpWorstDepot = deepcopy(i)
        #print 'newWorstObj = ' + str(tmpWorstObj)
        #print 'newWOrstDepot = ' + str(tmpWorstDepot)
    #print 'old Inv vect'
    #print inventory_tmpDTmp    
    for i2 in inventory_tmpDTmp.keys():
      inventory_tmpDTmp[i2] = 0
    inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
    for k in disasterIDs_tmp:
      for i2 in inventory_tmpDTmp.keys():
        if len([costDDum[(i2, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i2, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
          m.remove(pi_inventoryBalance[(k, i2)])
          pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      
    #print 'new Inv vect'
    #print inventory_tmpDTmp   
    print str(datetime.now()) +  '  Just Solved worst depot'  
  print str(datetime.now()) +  '  About to Solve'    
  m.update()
  m.optimize()
  print str(datetime.now()) +  '  Just Solved'
  #print 'sum from accra'
  #print quicksum(x_satDemand[k, 'Accra, Ghana', j, v].x for (k, i2, j, v) in myArcs_SatDemand.select(k, 'Accra, Ghana', '*', '*'))
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  #print myObj
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  #print myObjNoDum
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  
  #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDs_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDs_tmp)
  #print myFractionOfDisastersUsingDummy
  #print myWeightedDemandMetNoDum
  #print myWeightedDemand
  
  #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpDTmp.values())]) * 1. / len(disasterIDs_tmp)
  
  dualsInvNoDum_PlusDummyCost = {}
  for i in inventory_tmpDTmp.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


  dualsInvNoDum_UnAdj = {}
  for i in inventory_tmpDTmp.keys():
    myTmpDual = 0
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))

  dualsInvNoDum_All = {}
  for i in inventory_tmpDTmp.keys():
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))

    

    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
    
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
  
  myOptInvNoDum = {}
  for i in inventory_tmpDTmp.keys():
    if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    elif areInitialSuppliesVariables_Flag == 3:
      myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
    
  myOutDict = {'myObj': myObj
                , 'myObjNoDum': myObjNoDum
                , 'myWeightedDemand': myWeightedDemand
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
              }

  
  return myOutDict
"""


def f_solveStochLPDisasterGurobiSubLoc(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):

  #costD = myCostsToIterateD['Cost']
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD['Optimal']
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000

  indent = '        '
  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  #inventory_tmpD['Accra, Ghana'] += 1
  # myMaxKeyLength = 40
  # for i in inventory_tmpD.keys():
    # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # #> myMaxKeyLength:
      # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
  # for i in costD.keys():
    # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # costD[('Moffett', i[1], i[2])] = costD.pop(i)
  

  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  inventory_tmpDTmp = deepcopy(inventory_tmpD)
  inventory_tmpDBad = deepcopy(inventory_tmpD)
 

  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  

  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDTmp.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))
 
  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpDTmp.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO

  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
    for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
      #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
      pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD[kSubLoc], name = 'EnsureDemandSat_%s' %(k))
      #print 'wrong'
      #print inventory_tmpDTmp.keys()
      
    for i in inventory_tmpDTmp.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        elif areInitialSuppliesVariables_Flag == 3:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')
        
  
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
      
  # Added 9/19
    
      
  m.update()  

  
  
  if areInitialSuppliesVariables_Flag == 2:
    m.ModelSense = -1
  elif areInitialSuppliesVariables_Flag == 3:
    print str(datetime.now()) + indent * 2 +  '  About to Solve worst depot'
    tmpWorstObj = -1
    tmpWorstDepot = None
    for i in inventory_tmpDBad.keys():
      #print str(datetime.now()) + indent +  ' -- Testing depot' + str(i)
      for j in inventory_tmpDBad.keys():
        inventory_tmpDBad[j] = 0
      inventory_tmpDBad[i] = supplyTotalConstraint
      #print 'inventory vect'
      #print inventory_tmpDBad
      for k in disasterIDsUnq_tmp:
        disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
        for i2 in inventory_tmpDTmp.keys():
          if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
            m.remove(pi_inventoryBalance[(k, i2)])
            pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
      m.update()
      m.optimize()
      if m.status != GRB.status.OPTIMAL:
        print m.status
        raise NameError('Non-optimal LP')
      tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))
      #print 'tmpTmpObj = ' + str(tmpTmpObj)
      #print 'tmpWOrst  = ' + str(tmpWorstObj)
      #print 'old worst depot = ' + str(tmpWorstDepot)
      #print 'i = ' + str(i)
      if tmpTmpObj > tmpWorstObj:
        #print 'found new bad depot'
        tmpWorstObj = deepcopy(tmpTmpObj)
        tmpWorstDepot = deepcopy(i)
        #print 'newWorstObj = ' + str(tmpWorstObj)
        #print 'newWOrstDepot = ' + str(tmpWorstDepot)
    #print 'old Inv vect'
    #print inventory_tmpDTmp    
    for i2 in inventory_tmpDTmp.keys():
      inventory_tmpDTmp[i2] = 0
    inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      for i2 in inventory_tmpDTmp.keys():
        if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
          m.remove(pi_inventoryBalance[(k, i2)])
          pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      
    #print 'new Inv vect'
    #print inventory_tmpDTmp   
    print str(datetime.now()) + indent * 2 +  '  Just Solved worst depot'  
    
      
  print str(datetime.now()) + indent * 2 +  '  About to Solve'    
  m.update()
  m.optimize()
  print str(datetime.now()) + indent * 2 +  '  Just Solved'
  #print 'sum from accra'
  #print quicksum(x_satDemand[k, 'Accra, Ghana', j, v].x for (k, i2, j, v) in myArcs_SatDemand.select(k, 'Accra, Ghana', '*', '*'))
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

    
  #print str(datetime.now()) + indent +  '  Doing Test'    
  #for   (k, i, j, v) in myArcs_SatDemand.select('ID:9841', '*', '*', '*'):
  #  print 'k = ' + str(k) + ';i = ' + str(i) + ';j = ' + str(j) + ';v = ' + str(v) + ';flow = ' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('vvv')  
    
    
    
  #print str(datetime.now()) + indent +  '  part 1'  
  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  #print myObj
  #print str(datetime.now()) + indent +  '  part 2'  
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  #print myObjNoDum
  #print str(datetime.now()) + indent +  '  part 3'  
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  #print str(datetime.now()) + indent +  '  part 4'  
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  #print str(datetime.now()) + indent +  '  part 5'  
  # This is pre multiple locs per disastser #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  #myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand.select(k1, dummyNodeName, '*', '*')]).getConstant() > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 faster'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k1, dummyNodeName, j, v)].x for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 fastest 1'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if x_satDemand[(k1, dummyNodeName, j, v)].x > 0 for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  
  #print str(datetime.now()) + indent +  '  part 5 ended'  
  #print myFractionOfDisastersUsingDummy
  #print myWeightedDemandMetNoDum
  #print myWeightedDemand
  
  
  
  #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpDTmp.values())]) * 1. / len(disasterIDs_tmp)
  print str(datetime.now()) + indent * 2 +  '  Doing duals'  
  disasterIDsWithSubLocUnq_tmpD = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmpD.update({k: [ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k]})  
  
  #print str(datetime.now()) + indent +  '  Just made dict'  
  
  
  # dualsInvNoDum_PlusDummyCost = {}
  # kCount = 0
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
        # kCount += 1
    # dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


  dualsInvNoDum_PlusDummyCost = {}
  #kCount = 0
  for i in inventory_tmpDTmp.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
        #kCount += 1
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))



    
  # print str(datetime.now()) + indent +  '  kCount = ' + str(kCount)  
  
  # print str(datetime.now()) + indent +  '  Doing duals part 2'  
  # dualsInvNoDum_UnAdj = {}
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = 0
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
    # dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))
  # print ''
  # print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)  
  # print ''
  # print ''  
  
  dualsInvNoDum_UnAdj = deepcopy(dualsInvNoDum_PlusDummyCost)
  for i in dualsInvNoDum_PlusDummyCost.keys():
    dualsInvNoDum_UnAdj.update({i: dualsInvNoDum_PlusDummyCost[i] - myFractionOfDisastersUsingDummy * bigMCostDummy})
  #print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)    
  #print str(datetime.now()) + indent +  '  Doing duals part 3'    
  # dualsInvNoDum_All = {}
  # for i in inventory_tmpDTmp.keys():
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))
        
  dualsInvNoDum_All = {}
  for i in inventory_tmpDTmp.keys():
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))


  #print str(datetime.now()) + indent +  '  Doing duals done'      
  #assert False

  print str(datetime.now()) + indent * 2 +  '  Doing myFlow'    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  #for   (k, i, j, v) in myArcs_SatDemand:
  #  print str(k) + ';' + str(i) + ';' + str(j) + ';' + str(v) + ';' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('UUU')

  print str(datetime.now()) + indent * 2 +  '  Doing myFlowNoDum'  
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  print str(datetime.now()) + indent * 2 +  '  Doing myOptInvNoDum'  
  myOptInvNoDum = {}
  for i in inventory_tmpDTmp.keys():
    if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    elif areInitialSuppliesVariables_Flag == 3:
      myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
  #assert False  
  #print ''
  #print 'myObjNoDum = ', myObjNoDum
  #m.update()
  #print 'myObjNoDum = ', myObjNoDum
  #print 'myObjNoDum.const = ', myObjNoDum.getConstant()
  #print ''
  #assert False
  myOutDict = {'myObj': myObj.getConstant()
                , 'myObjNoDum': myObjNoDum.getConstant()
                , 'myWeightedDemand': myWeightedDemand.getConstant()
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant()
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
              }

  
  return myOutDict
      

def f_solveStochLPDisasterGurobiSubLoc2(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  ):

  #costD = myCostsToIterateD['Cost']
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD['Optimal']
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000

  indent = '        '
  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  #inventory_tmpD['Accra, Ghana'] += 1
  # myMaxKeyLength = 40
  # for i in inventory_tmpD.keys():
    # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # #> myMaxKeyLength:
      # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
  # for i in costD.keys():
    # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # costD[('Moffett', i[1], i[2])] = costD.pop(i)
  

  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  inventory_tmpDTmp = deepcopy(inventory_tmpD)
  inventory_tmpDBad = deepcopy(inventory_tmpD)
 

  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  

  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDTmp.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))
 
  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpDTmp.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO

  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
    for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
      #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
      pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD[kSubLoc], name = 'EnsureDemandSat_%s' %(k))
      #print 'wrong'
      #print inventory_tmpDTmp.keys()
      
    for i in inventory_tmpDTmp.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        elif areInitialSuppliesVariables_Flag == 3:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')
        
  
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
    
    for i in depotWhichFixedSubset:
        pi_fixed_inv = m.addConstr(x_howToAllocateInitialInventory[i] == inventory_tmpDTmp[i])
     
  # Added 9/19
    
      
  m.update()  

  
  
  if areInitialSuppliesVariables_Flag == 2:
    m.ModelSense = -1
  elif areInitialSuppliesVariables_Flag == 3:
    print str(datetime.now()) + indent * 2 +  '  About to Solve worst depot'
    tmpWorstObj = -1
    tmpWorstDepot = None
    for i in inventory_tmpDBad.keys():
      #print str(datetime.now()) + indent +  ' -- Testing depot' + str(i)
      for j in inventory_tmpDBad.keys():
        inventory_tmpDBad[j] = 0
      inventory_tmpDBad[i] = supplyTotalConstraint
      #print 'inventory vect'
      #print inventory_tmpDBad
      for k in disasterIDsUnq_tmp:
        disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
        for i2 in inventory_tmpDTmp.keys():
          if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
            m.remove(pi_inventoryBalance[(k, i2)])
            pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
      m.update()
      m.optimize()
      if m.status != GRB.status.OPTIMAL:
        print m.status
        raise NameError('Non-optimal LP')
      tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))
      #print 'tmpTmpObj = ' + str(tmpTmpObj)
      #print 'tmpWOrst  = ' + str(tmpWorstObj)
      #print 'old worst depot = ' + str(tmpWorstDepot)
      #print 'i = ' + str(i)
      if tmpTmpObj > tmpWorstObj:
        #print 'found new bad depot'
        tmpWorstObj = deepcopy(tmpTmpObj)
        tmpWorstDepot = deepcopy(i)
        #print 'newWorstObj = ' + str(tmpWorstObj)
        #print 'newWOrstDepot = ' + str(tmpWorstDepot)
    #print 'old Inv vect'
    #print inventory_tmpDTmp    
    for i2 in inventory_tmpDTmp.keys():
      inventory_tmpDTmp[i2] = 0
    inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      for i2 in inventory_tmpDTmp.keys():
        if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
          m.remove(pi_inventoryBalance[(k, i2)])
          pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      
    #print 'new Inv vect'
    #print inventory_tmpDTmp   
    print str(datetime.now()) + indent * 2 +  '  Just Solved worst depot'  
    
      
  print str(datetime.now()) + indent * 2 +  '  About to Solve'    
  m.update()
  m.optimize()
  print str(datetime.now()) + indent * 2 +  '  Just Solved'
  #print 'sum from accra'
  #print quicksum(x_satDemand[k, 'Accra, Ghana', j, v].x for (k, i2, j, v) in myArcs_SatDemand.select(k, 'Accra, Ghana', '*', '*'))
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

    
  #print str(datetime.now()) + indent +  '  Doing Test'    
  #for   (k, i, j, v) in myArcs_SatDemand.select('ID:9841', '*', '*', '*'):
  #  print 'k = ' + str(k) + ';i = ' + str(i) + ';j = ' + str(j) + ';v = ' + str(v) + ';flow = ' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('vvv')  
    
    
    
  #print str(datetime.now()) + indent +  '  part 1'  
  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  #print myObj
  #print str(datetime.now()) + indent +  '  part 2'  
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  #print myObjNoDum
  #print str(datetime.now()) + indent +  '  part 3'  
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  #print str(datetime.now()) + indent +  '  part 4'  
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  #print str(datetime.now()) + indent +  '  part 5'  
  # This is pre multiple locs per disastser #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  #myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand.select(k1, dummyNodeName, '*', '*')]).getConstant() > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 faster'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k1, dummyNodeName, j, v)].x for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 fastest 1'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if x_satDemand[(k1, dummyNodeName, j, v)].x > 0 for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  
  #print str(datetime.now()) + indent +  '  part 5 ended'  
  #print myFractionOfDisastersUsingDummy
  #print myWeightedDemandMetNoDum
  #print myWeightedDemand
  
  
  
  #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpDTmp.values())]) * 1. / len(disasterIDs_tmp)
  print str(datetime.now()) + indent * 2 +  '  Doing duals'  
  disasterIDsWithSubLocUnq_tmpD = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmpD.update({k: [ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k]})  
  
  #print str(datetime.now()) + indent +  '  Just made dict'  
  
  
  # dualsInvNoDum_PlusDummyCost = {}
  # kCount = 0
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
        # kCount += 1
    # dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


  dualsInvNoDum_PlusDummyCost = {}
  #kCount = 0
  for i in inventory_tmpDTmp.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
        #kCount += 1
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))



    
  # print str(datetime.now()) + indent +  '  kCount = ' + str(kCount)  
  
  # print str(datetime.now()) + indent +  '  Doing duals part 2'  
  # dualsInvNoDum_UnAdj = {}
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = 0
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
    # dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))
  # print ''
  # print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)  
  # print ''
  # print ''  
  
  dualsInvNoDum_UnAdj = deepcopy(dualsInvNoDum_PlusDummyCost)
  for i in dualsInvNoDum_PlusDummyCost.keys():
    dualsInvNoDum_UnAdj.update({i: dualsInvNoDum_PlusDummyCost[i] - myFractionOfDisastersUsingDummy * bigMCostDummy})
  #print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)    
  #print str(datetime.now()) + indent +  '  Doing duals part 3'    
  # dualsInvNoDum_All = {}
  # for i in inventory_tmpDTmp.keys():
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))
        
  dualsInvNoDum_All = {}
  for i in inventory_tmpDTmp.keys():
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))


  #print str(datetime.now()) + indent +  '  Doing duals done'      
  #assert False

  print str(datetime.now()) + indent * 2 +  '  Doing myFlow'    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  #for   (k, i, j, v) in myArcs_SatDemand:
  #  print str(k) + ';' + str(i) + ';' + str(j) + ';' + str(v) + ';' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('UUU')

  print str(datetime.now()) + indent * 2 +  '  Doing myFlowNoDum'  
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  print str(datetime.now()) + indent * 2 +  '  Doing myOptInvNoDum'  
  myOptInvNoDum = {}
  for i in inventory_tmpDTmp.keys():
    if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    elif areInitialSuppliesVariables_Flag == 3:
      myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
  #assert False  
  #print ''
  #print 'myObjNoDum = ', myObjNoDum
  #m.update()
  #print 'myObjNoDum = ', myObjNoDum
  #print 'myObjNoDum.const = ', myObjNoDum.getConstant()
  #print ''
  #assert False
  myOutDict = {'myObj': myObj.getConstant()
                , 'myObjNoDum': myObjNoDum.getConstant()
                , 'myWeightedDemand': myWeightedDemand.getConstant()
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant()
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
              }

  
  return myOutDict
     

def f_solveStochLPDisasterGurobiSubLoc3_old(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  , minInvItemD
                                  , depotInWhichCountry
                                  ):


  #costD = myCostsToIterateD['Cost']
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD['Optimal']
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000

  indent = '        '
  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  #inventory_tmpD['Accra, Ghana'] += 1
  # myMaxKeyLength = 40
  # for i in inventory_tmpD.keys():
    # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # #> myMaxKeyLength:
      # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
  # for i in costD.keys():
    # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
      # costD[('Moffett', i[1], i[2])] = costD.pop(i)
  print("Function Call!")


  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  inventory_tmpDTmp = deepcopy(inventory_tmpD)
  inventory_tmpDBad = deepcopy(inventory_tmpD)
  
  if sum(minInvItemD.values()) > supplyTotalConstraint:
    minDemandScale = sum(minInvItemD.values()) / supplyTotalConstraint
    minInvItemD_tmp = {}
    for i in minInvItemD.keys():
      minInvItemD_tmp.update({i: int(numpy.floor(minInvItemD[i] / minDemandScale * 0.99))})
  else:  
    minInvItemD_tmp = {}
    for i in minInvItemD.keys():
      minInvItemD_tmp.update({i: int(numpy.floor(minInvItemD[i] ))})

 
  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  

  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDTmp.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))
 
  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpDTmp.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO

  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
    for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
      #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
      pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD[kSubLoc], name = 'EnsureDemandSat_%s' %(k))
      #print 'wrong'
      #print inventory_tmpDTmp.keys()
      
    for i in inventory_tmpDTmp.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        elif areInitialSuppliesVariables_Flag == 3:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')


  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:  
    pi_minInvPerCountry = {}  
    print '***%&%^$&$&$&$&^$ You are excluding Palau manually'
    for i_ctry in list(set(depotInWhichCountry.values())):
      
      if i_ctry not in ['Palau', 'Malaysia', 'Papua New Guinea']:

        #print 'country', i_ctry
        #print 'depots', [i for i in depotInWhichCountry.keys() if depotInWhichCountry[i] == i_ctry]
        pi_minInvPerCountry[i_ctry] = m.addConstr(
                                        sum(
                                            [x_howToAllocateInitialInventory[i] for i in depotInWhichCountry.keys() if depotInWhichCountry[i] == i_ctry]
                                            ) >= minInvItemD_tmp[i_ctry]
                                        , "EnsureMinInvEachCntry"
                                        )
  
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
    
    for i in depotWhichFixedSubset:
        pi_fixed_inv = m.addConstr(x_howToAllocateInitialInventory[i] == inventory_tmpDTmp[i])
     
  # Added 9/19
    
      
  m.update()  

  
  
  if areInitialSuppliesVariables_Flag == 2:
    m.ModelSense = -1
  elif areInitialSuppliesVariables_Flag == 3:
    print str(datetime.now()) + indent * 2 +  '  About to Solve worst depot'
    tmpWorstObj = -1
    tmpWorstDepot = None
    for i in inventory_tmpDBad.keys():
      #print str(datetime.now()) + indent +  ' -- Testing depot' + str(i)
      for j in inventory_tmpDBad.keys():
        inventory_tmpDBad[j] = 0
      inventory_tmpDBad[i] = supplyTotalConstraint
      #print 'inventory vect'
      #print inventory_tmpDBad
      for k in disasterIDsUnq_tmp:
        disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
        for i2 in inventory_tmpDTmp.keys():
          if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
            m.remove(pi_inventoryBalance[(k, i2)])
            pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
      m.update()
      m.optimize()
      if m.status != GRB.status.OPTIMAL:
        print m.status
        raise NameError('Non-optimal LP')
      tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))
      #print 'tmpTmpObj = ' + str(tmpTmpObj)
      #print 'tmpWOrst  = ' + str(tmpWorstObj)
      #print 'old worst depot = ' + str(tmpWorstDepot)
      #print 'i = ' + str(i)
      if tmpTmpObj > tmpWorstObj:
        #print 'found new bad depot'
        tmpWorstObj = deepcopy(tmpTmpObj)
        tmpWorstDepot = deepcopy(i)
        #print 'newWorstObj = ' + str(tmpWorstObj)
        #print 'newWOrstDepot = ' + str(tmpWorstDepot)
    #print 'old Inv vect'
    #print inventory_tmpDTmp    
    for i2 in inventory_tmpDTmp.keys():
      inventory_tmpDTmp[i2] = 0
    inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      for i2 in inventory_tmpDTmp.keys():
        if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
          m.remove(pi_inventoryBalance[(k, i2)])
          pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      
    #print 'new Inv vect'
    #print inventory_tmpDTmp   
    print str(datetime.now()) + indent * 2 +  '  Just Solved worst depot'  
    
      
  print str(datetime.now()) + indent * 2 +  '  About to Solve'    
  m.update()
  m.optimize()
  print str(datetime.now()) + indent * 2 +  '  Just Solved'
  #print 'sum from accra'
  #print quicksum(x_satDemand[k, 'Accra, Ghana', j, v].x for (k, i2, j, v) in myArcs_SatDemand.select(k, 'Accra, Ghana', '*', '*'))
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

    
  #print str(datetime.now()) + indent +  '  Doing Test'    
  #for   (k, i, j, v) in myArcs_SatDemand.select('ID:9841', '*', '*', '*'):
  #  print 'k = ' + str(k) + ';i = ' + str(i) + ';j = ' + str(j) + ';v = ' + str(v) + ';flow = ' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('vvv')  
    
    
    
  #print str(datetime.now()) + indent +  '  part 1'  
  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  #print myObj
  #print str(datetime.now()) + indent +  '  part 2'  
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  #print myObjNoDum
  #print str(datetime.now()) + indent +  '  part 3'  
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  #print str(datetime.now()) + indent +  '  part 4'  
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  #print str(datetime.now()) + indent +  '  part 5'  
  # This is pre multiple locs per disastser #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  #myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand.select(k1, dummyNodeName, '*', '*')]).getConstant() > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 faster'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k1, dummyNodeName, j, v)].x for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  #print str(datetime.now()) + indent +  '  part 5 fastest 1'  
  #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if x_satDemand[(k1, dummyNodeName, j, v)].x > 0 for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) * 1. / len(disasterIDsUnq_tmp)
  #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  
  #print str(datetime.now()) + indent +  '  part 5 ended'  
  #print myFractionOfDisastersUsingDummy
  #print myWeightedDemandMetNoDum
  #print myWeightedDemand
  
  
  
  #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpDTmp.values())]) * 1. / len(disasterIDs_tmp)
  print str(datetime.now()) + indent * 2 +  '  Doing duals'  
  disasterIDsWithSubLocUnq_tmpD = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmpD.update({k: [ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k]})  
  
  #print str(datetime.now()) + indent +  '  Just made dict'  
  
  
  # dualsInvNoDum_PlusDummyCost = {}
  # kCount = 0
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
        # kCount += 1
    # dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


  dualsInvNoDum_PlusDummyCost = {}
  #kCount = 0
  for i in inventory_tmpDTmp.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
        #kCount += 1
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))



    
  # print str(datetime.now()) + indent +  '  kCount = ' + str(kCount)  
  
  # print str(datetime.now()) + indent +  '  Doing duals part 2'  
  # dualsInvNoDum_UnAdj = {}
  # for i in inventory_tmpDTmp.keys():
    # myTmpDual = 0
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # myTmpDual += pi_inventoryBalance[(k, i)].Pi
    # dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))
  # print ''
  # print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)  
  # print ''
  # print ''  
  
  dualsInvNoDum_UnAdj = deepcopy(dualsInvNoDum_PlusDummyCost)
  for i in dualsInvNoDum_PlusDummyCost.keys():
    dualsInvNoDum_UnAdj.update({i: dualsInvNoDum_PlusDummyCost[i] - myFractionOfDisastersUsingDummy * bigMCostDummy})
  #print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)    
  #print str(datetime.now()) + indent +  '  Doing duals part 3'    
  # dualsInvNoDum_All = {}
  # for i in inventory_tmpDTmp.keys():
    # for k in disasterIDsUnq_tmp:
      # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        # dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))
        
  dualsInvNoDum_All = {}
  for i in inventory_tmpDTmp.keys():
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))


  #print str(datetime.now()) + indent +  '  Doing duals done'      
  #assert False

  print str(datetime.now()) + indent * 2 +  '  Doing myFlow'    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  #for   (k, i, j, v) in myArcs_SatDemand:
  #  print str(k) + ';' + str(i) + ';' + str(j) + ';' + str(v) + ';' + str(x_satDemand[(k, i, j, v)].x)
  #raise NameError('UUU')

  print str(datetime.now()) + indent * 2 +  '  Doing myFlowNoDum'  
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  print str(datetime.now()) + indent * 2 +  '  Doing myOptInvNoDum'  
  myOptInvNoDum = {}
  for i in inventory_tmpDTmp.keys():
    if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    elif areInitialSuppliesVariables_Flag == 3:
      myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
  #assert False  
  #print ''
  #print 'myObjNoDum = ', myObjNoDum
  #m.update()
  #print 'myObjNoDum = ', myObjNoDum
  #print 'myObjNoDum.const = ', myObjNoDum.getConstant()
  #print ''
  #assert False

  print("----------------------------------------------------------------")
  print(myFlow)
  print("----------------------------------------------------------------")
  #BOOKMARK
  sys.exit()
  myOutDict = {'myObj': myObj.getConstant() #Objective value with dummy (might be huge)
                , 'myObjNoDum': myObjNoDum.getConstant() #Objective value without dummy 
                , 'myWeightedDemand': myWeightedDemand.getConstant() #Total flow (weighted by probability not cost)
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant() #Total flow without dummy (weighted by probability not cost)
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy #Fraction of disasters that used dummy not (fraction not used) (should be weighted by probabilities)
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost #Dictionary mapping depot names to dual variable sensitivity
                #Double check impact of scaled demand logic
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All #Maps (disasterID, depot) to sensitivity
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow #Maps variables to flow
                , 'myOptInvNoDum': myOptInvNoDum #Optimal inv distribution if moving inventory is allowed
                , 'dualTotInv': dualTotInv
              }

  return myOutDict































#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#JAMESSTART
def f_solveStochLPDisasterGurobiSubLoc3(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  , minInvItemD
                                  , depotInWhichCountry
                                  ):
  print("-------------------------------MAIN------------------------------")
  #Does not output
  #Does not consider fleet capacity
  #Does not consider dual variables
  #Monetary cost support 
  #Slides

  #Test 1
  demand_tmpD = {
  ('0000-0000', 'SubLoc_00000'): 100,
  ('0000-0001', 'SubLoc_00000'): 80,
  ('0000-0002', 'SubLoc_00000'): 50,}
  probs_tmpD = {'0000-0000':.5, '0000-0001':.99, '0000-0002':.1,}
  demandAddress_tmpD = {
  ('0000-0000', 'SubLoc_00000'): "DisasterCity0", 
  ('0000-0001', 'SubLoc_00000'): "DisasterCity1", 
  ('0000-0002', 'SubLoc_00000'): "DisasterCity2",}
  costD = {
  ('San Francisco, California', 'DisasterCity0', 'Truck'):10, 
  ('Dallas, Texas', 'DisasterCity0', 'Truck'):70, 
  ("Philadelphia, Pennsylvania", 'DisasterCity0', 'Truck'):1,
  ('San Francisco, California', 'DisasterCity1', 'Truck'):10, 
  ('Dallas, Texas', 'DisasterCity1', 'Truck'):70, 
  ("Philadelphia, Pennsylvania", 'DisasterCity1', 'Truck'):1,
  ('San Francisco, California', 'DisasterCity2', 'Truck'):20, 
  ('Dallas, Texas', 'DisasterCity2', 'Truck'):70, 
  ("Philadelphia, Pennsylvania", 'DisasterCity2', 'Truck'):1,}
  inventory_tmpD = {
  'Dallas, Texas': 700, 
  'San Francisco, California': 200, 
  'Philadelphia, Pennsylvania': 30}

  #DUMMY TEST  
  # demand_tmpD = {
  # ('0000-0000', 'SubLoc_00000'): 1000,
  # ('0000-0001', 'SubLoc_00000'): 80,
  # ('0000-0002', 'SubLoc_00000'): 50,
  # ('0000-0003', 'SubLoc_00000'): 50}
  # probs_tmpD = {'0000-0000':.5, '0000-0001':.99, '0000-0002':.1,
  # '0000-0003':.5}
  # demandAddress_tmpD = {
  # ('0000-0000', 'SubLoc_00000'): "DisasterCity0", 
  # ('0000-0001', 'SubLoc_00000'): "DisasterCity1", 
  # ('0000-0002', 'SubLoc_00000'): "DisasterCity2",
  # ('0000-0003', 'SubLoc_00000'): "DisasterCity3"}
  # costD = {
  # ('San Francisco, California', 'DisasterCity0', 'Truck'):10, 
  # ('Dallas, Texas', 'DisasterCity0', 'Truck'):70, 
  # ("Philadelphia, Pennsylvania", 'DisasterCity0', 'Truck'):1,
  # ('San Francisco, California', 'DisasterCity1', 'Truck'):10, 
  # ('Dallas, Texas', 'DisasterCity1', 'Truck'):70, 
  # ("Philadelphia, Pennsylvania", 'DisasterCity1', 'Truck'):1,
  # ('San Francisco, California', 'DisasterCity2', 'Truck'):20, 
  # ('Dallas, Texas', 'DisasterCity2', 'Truck'):70, 
  # ("Philadelphia, Pennsylvania", 'DisasterCity2', 'Truck'):1,}
  # inventory_tmpD = {
  # 'Dallas, Texas': 700, 
  # 'San Francisco, California': 200, 
  # 'Philadelphia, Pennsylvania': 30}


  m = Model('StochLP')



  #Generate list of string names
  disasterList = demand_tmpD.keys()
  carrierList = []



  #Create a mapping from depot city names to (contractor, capacity, cost) triplets
  #Populate carrierList
  carrierDict = {}
  carrierParse = f_myReadCsv(inputPath + "fakeCarrierDataJames.csv")
  carrierDataParse = carrierParse[1]
  for row in carrierDataParse:
    if row[5] not in carrierDict:
      carrierDict[row[5]] = []
    carrierDict[row[5]].append((row[0], int(row[1]), int(row[2])))
  


  #Initialize duo variables
  duoVars = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoVars[depot+":"+carrier[0]] = m.addVar(lb=0.0, ub=carrier[1], vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]) 



  #Initialize triplet variables
  triVars = {}
  duoToTris = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoToTris[depot+":"+carrier[0]] = []
      for disaster in disasterList:
        if (depot, demandAddress_tmpD[disaster], 'Truck') in costD:
          var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+disaster[1]) 
          triVars[depot+":"+carrier[0]+":"+disaster[0]+disaster[1]] = var
          duoToTris[depot+":"+carrier[0]].append(var)
  m.update()

  
  #Minimize expected time
  weights = []
  for triVar in [triVars[key] for key in triVars]:
    ID = triVar.VarName.split(":")[2].split("SubLoc")[0]
    ID2 = "SubLoc" + triVar.VarName.split(":")[2].split("SubLoc")[1]
    depotLoc = triVar.VarName.split(":")[0]
    for key in carrierDict: #Identify proper element
      elements = carrierDict[key]
      for element in elements:
        if element[0] == triVar.VarName.split(":")[1]:
          extraCost = element[2]
          break
          break
    if (ID,ID2) in demandAddress_tmpD:
      if (depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck") in costD:
        weights.append(probs_tmpD[ID]*(extraCost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck")])) #Check order preservation?
  expr = LinExpr()
  expr.addTerms(weights, [triVars[key] for key in triVars]) 
  m.setObjective(expr, GRB.MINIMIZE)



  #Satisfy demand
  for disasterTuple in demand_tmpD:
    disasterString = disasterTuple[0]+disasterTuple[1]
    demandQuantity = demand_tmpD[disasterTuple]
    LHS = LinExpr()
    LHS.addConstant(demandQuantity)
    RHS = LinExpr()
    for depot in carrierDict:
      depotCarriers = carrierDict[depot]
      for carrier in depotCarriers:
        if depot+":"+carrier[0]+":"+disasterString in triVars:
          RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterString])
    m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterString+">")



  #Flow constraint
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
          LHS = LinExpr()
          LHS.addTerms(1, duoVars[depot+":"+carrier[0]])
          RHS = LinExpr()
          for tri in duoToTris[depot+":"+carrier[0]]:
            RHS.addTerms(1, tri)
          m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+">")



  #Depot capacity
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    inventoryCapacity = inventory_tmpD[depot]
    LHS = LinExpr()
    LHS.addConstant(inventoryCapacity)
    RHS = LinExpr()
    for carrier in depotCarriers:
      RHS.addTerms(1,duoVars[depot+":"+carrier[0]])


    m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+carrier[0]+">")



  #Carrier capacity
  #Nonnegativity
  #These two are taken care of by bounds placed on respective variables



  m.update()
  m.optimize()
  m.write("jamesmodel.lp")

  def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nTotal Response Time: %g' % m.objVal)
        print('\nDispatch:')
        assignments = m.getAttr('x', [triVars[key] for key in triVars])
        for tri in [triVars[key] for key in triVars]:
            if tri.x > 0.0001:
              print(tri.VarName, tri.x)
    else:
        print('No solution')
  
  printSolution()


  #('2008-0210', 'Dallas, Texas', 'Des Moines, Iowa', 'Truck'): 24.0
  # myFlow = {}
  # for key in triVars:
  #   key_components = key.split(":")
  #   myFlow[(key_components[2], key_components[0], key_components[2], key_components[1])] = triVars[key].X #Need to change

  nonfixedinventoryhelper(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  , minInvItemD
                                  , depotInWhichCountry
                                  )

  dummyhelper(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  , minInvItemD
                                  , depotInWhichCountry
                                  )

  sys.exit()
  #Bookmark
  myOutDict = {'myObj': myObj.getConstant() #Objective value with dummy (might be huge)
                , 'myObjNoDum': myObjNoDum.getConstant() #Objective value without dummy 
                , 'myWeightedDemand': myWeightedDemand.getConstant() #Total flow (weighted by probability not cost)
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant() #Total flow without dummy (weighted by probability not cost)
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy #Fraction of disasters that used dummy not (fraction not used) (should be weighted by probabilities)
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost #Dictionary mapping depot names to dual variable sensitivity
                #Double check impact of scaled demand logic
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All #Maps (disasterID, depot) to sensitivity
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow #Maps variables to flow
                #Optimal inv distribution if moving inventory is  allowed
                , 'myOptInvNoDum': {'Dallas, Texas': 839996.0, 'Atlanta, Georgia': 4400055.2, 'San Francisco, California': 256021.6, 'Philadelphia, Pennsylvania': 24680549.2} 
                , 'dualTotInv': 0.0
              }

  return myOutDict







def nonfixedinventoryhelper(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  , depotWhichFixedSubset
                                  , minInvItemD
                                  , depotInWhichCountry
                                  ):
  print("-------------------------------NONFIXED------------------------------")
  m = Model('StochLPNonfixed')
  #Generate list of string names
  disasterList = demand_tmpD.keys()
  carrierList = []



  #Create a mapping from depot city names to (contractor, capacity, cost) triplets
  #Populate carrierList
  carrierDict = {}
  carrierParse = f_myReadCsv(inputPath + "fakeCarrierDataJames.csv")
  carrierDataParse = carrierParse[1]
  for row in carrierDataParse:
    if row[5] not in carrierDict:
      carrierDict[row[5]] = []
    carrierDict[row[5]].append((row[0], int(row[1]), int(row[2])))
  


  #Initialize duo variables
  duoVars = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoVars[depot+":"+carrier[0]] = m.addVar(lb=0.0, ub=carrier[1], vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]) 



  #Initialize triplet variables
  triVars = {}
  duoToTris = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoToTris[depot+":"+carrier[0]] = []
      for disaster in disasterList:
        if (depot, demandAddress_tmpD[disaster], 'Truck') in costD:
          var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+disaster[1]) 
          triVars[depot+":"+carrier[0]+":"+disaster[0]+disaster[1]] = var
          duoToTris[depot+":"+carrier[0]].append(var)
  m.update()

  
  #Minimize expected time
  weights = []
  for triVar in [triVars[key] for key in triVars]:
    ID = triVar.VarName.split(":")[2].split("SubLoc")[0]
    ID2 = "SubLoc" + triVar.VarName.split(":")[2].split("SubLoc")[1]
    depotLoc = triVar.VarName.split(":")[0]
    for key in carrierDict: #Identify proper element
      elements = carrierDict[key]
      for element in elements:
        if element[0] == triVar.VarName.split(":")[1]:
          extraCost = element[2]
          break
          break
    if (ID,ID2) in demandAddress_tmpD:
      if (depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck") in costD:
        weights.append(probs_tmpD[ID]*(extraCost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck")])) #Check order preservation?
  expr = LinExpr()
  expr.addTerms(weights, [triVars[key] for key in triVars]) 
  m.setObjective(expr, GRB.MINIMIZE)



  #Satisfy demand
  for disasterTuple in demand_tmpD:
    disasterString = disasterTuple[0]+disasterTuple[1]
    demandQuantity = demand_tmpD[disasterTuple]
    LHS = LinExpr()
    LHS.addConstant(demandQuantity)
    RHS = LinExpr()
    for depot in carrierDict:
      depotCarriers = carrierDict[depot]
      for carrier in depotCarriers:
        if depot+":"+carrier[0]+":"+disasterString in triVars:
          RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterString])
    m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterString+">")

  #Flow constraint
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
          LHS = LinExpr()
          LHS.addTerms(1, duoVars[depot+":"+carrier[0]])
          RHS = LinExpr()
          for tri in duoToTris[depot+":"+carrier[0]]:
            RHS.addTerms(1, tri)
          m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+">")


  #THIS IS THE ONLY MODIFIED SECTION
  #Depot capacity
  totalCapacity = 0
  for depotName in inventory_tmpD:
    totalCapacity += inventory_tmpD[depotName]

  depotVars = {}
  for depotName in carrierDict:
    depotVars[depotName] = m.addVar(lb=0.0, ub=totalCapacity, vtype=GRB.CONTINUOUS, name=depotName+":NONFIXEDCAPACITY") 

  LHS = LinExpr()
  for depot in depotVars:
    inventoryCapacity = depotVars[depot]
    LHS.addTerms(1.0, inventoryCapacity)
  RHS = LinExpr()
  RHS.addConstant(totalCapacity)
  m.addConstr(RHS, GRB.EQUAL, LHS, name="TOTALINVENTORY<>") #Can also use GREATER_EQUAL

  for depotName in carrierDict:
    depotCarriers = carrierDict[depotName]
    inventoryCapacity = depotVars[depotName]
    LHS = LinExpr()
    LHS.addTerms(1.0, inventoryCapacity)
    RHS = LinExpr()
    for carrier in depotCarriers:
      RHS.addTerms(1,duoVars[depotName+":"+carrier[0]])

    m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depotName+":"+carrier[0]+">")



  m.update()
  m.optimize()
  m.write("jamesmodelnonfixed.lp")

  def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nTotal Response Time: %g' % m.objVal)
        print('\nDispatch:')
        for tri in [triVars[key] for key in triVars]:
            if tri.x > 0.0001:
              print(tri.VarName, tri.x)
        print('\nCapacity Allocation:')
        for depotV in [depotVars[key] for key in depotVars]:
            if depotV.x > 0.0001:
              print(depotV.VarName, depotV.x)
    else:
        print('No solution')
    
  printSolution()

  myNonfixedFlow = {}
  return myNonfixedFlow







def dummyhelper(demand_tmpD
                                , demandAddress_tmpD
                                , probs_tmpD
                                , disasterIDsUnq_tmp
                                , disasterIDsWithSubLocUnq_tmp
                                , inventory_tmpD
                                , transModesTransParams
                                , bigMCostElim
                                , bigMCostDummy
                                , costD
                                , dummyNodeName
                                , areInitialSuppliesVariables_Flag
                                , depotWhichFixedSubset
                                , minInvItemD
                                , depotInWhichCountry
                                ):
  print("-------------------------------DUMMY------------------------------")

  m = Model('StochLP')

  #Generate list of string names
  disasterList = demand_tmpD.keys()
  carrierList = []

  #Create a mapping from depot city names to (contractor, capacity, cost) triplets
  #Populate carrierList
  carrierDict = {}
  carrierParse = f_myReadCsv(inputPath + "fakeCarrierDataJames.csv")
  carrierDataParse = carrierParse[1]
  for row in carrierDataParse:
    if row[5] not in carrierDict:
      carrierDict[row[5]] = []
    carrierDict[row[5]].append((row[0], int(row[1]), int(row[2])))
  
  #Initialize duo variables
  duoVars = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoVars[depot+":"+carrier[0]] = m.addVar(lb=0.0, ub=carrier[1], vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]) 

  #Initialize triplet variables
  triVars = {}
  duoToTris = {}
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
      duoToTris[depot+":"+carrier[0]] = []
      for disaster in disasterList:
        if (depot, demandAddress_tmpD[disaster], 'Truck') in costD:
          var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+disaster[1]) 
          triVars[depot+":"+carrier[0]+":"+disaster[0]+disaster[1]] = var
          duoToTris[depot+":"+carrier[0]].append(var)
  m.update()





  #Introducing a fake dummy node across all variables
  carrierDict["dummy"] = [("dummycarrier",1000000,0)]
  duoVars["dummy:dummycarrier"] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier") 
  duoToTris["dummy:dummycarrier"] = []
  for disasterName in disasterList:
    var =  m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier:" + disasterName[0]+disasterName[1]) 
    triVars["dummy:dummycarrier:" + disasterName[0]+disasterName[1]] = var
    duoToTris["dummy:dummycarrier"].append(var)
  for disasterID in demandAddress_tmpD:
    costD[('dummy', demandAddress_tmpD[disasterID], 'Truck')] = 10000 #Dummy cost
  inventory_tmpD['dummy'] = 1000
  m.update()





  #Minimize expected time
  weights = []
  for triVar in [triVars[key] for key in triVars]:
    ID = triVar.VarName.split(":")[2].split("SubLoc")[0]
    ID2 = "SubLoc" + triVar.VarName.split(":")[2].split("SubLoc")[1]
    depotLoc = triVar.VarName.split(":")[0]
    for key in carrierDict: #Identify proper element
      elements = carrierDict[key]
      for element in elements:
        if element[0] == triVar.VarName.split(":")[1]:
          extraCost = element[2]
          break
          break
    if (ID,ID2) in demandAddress_tmpD:
      if (depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck") in costD:
        weights.append(probs_tmpD[ID]*(extraCost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck")])) #Check order preservation?
  expr = LinExpr()
  expr.addTerms(weights, [triVars[key] for key in triVars]) 
  m.setObjective(expr, GRB.MINIMIZE)

  #Satisfy demand
  for disasterTuple in demand_tmpD:
    disasterString = disasterTuple[0]+disasterTuple[1]
    demandQuantity = demand_tmpD[disasterTuple]
    LHS = LinExpr()
    LHS.addConstant(demandQuantity)
    RHS = LinExpr()
    for depot in carrierDict:
      depotCarriers = carrierDict[depot]
      for carrier in depotCarriers:
        if depot+":"+carrier[0]+":"+disasterString in triVars:
          RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterString])
    m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterString+">")

  #Flow constraint
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    for carrier in depotCarriers:
          LHS = LinExpr()
          LHS.addTerms(1, duoVars[depot+":"+carrier[0]])
          RHS = LinExpr()
          for tri in duoToTris[depot+":"+carrier[0]]:
            RHS.addTerms(1, tri)
          m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+">")

  #Depot capacity
  for depot in carrierDict:
    depotCarriers = carrierDict[depot]
    inventoryCapacity = inventory_tmpD[depot]
    LHS = LinExpr()
    LHS.addConstant(inventoryCapacity)
    RHS = LinExpr()
    for carrier in depotCarriers:
      RHS.addTerms(1,duoVars[depot+":"+carrier[0]])

    m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+carrier[0]+">")

  #Carrier capacity
  #Nonnegativity
  #These two are taken care of by bounds placed on respective variables
  m.update()
  m.optimize()
  m.write("dummymodel.lp")
  def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nTotal Response Time: %g' % m.objVal)
        print('\nDispatch:')
        assignments = m.getAttr('x', [triVars[key] for key in triVars])
        for tri in [triVars[key] for key in triVars]:
            if tri.x > 0.0001:
              print(tri.VarName, tri.x)
    else:
        print('No solution')
  
  printSolution()

  dummySolution = {}
  return dummySolution
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



























     
     
     
     
     
     
def f_solveStochLPDisasterGurobiSubLocScaleDemand(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):

  #costD = myCostsToIterateD['Cost']
  #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD['Optimal']
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000

  indent = '        '

  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  inventory_tmpDTmp = deepcopy(inventory_tmpD)
  inventory_tmpDBad = deepcopy(inventory_tmpD)
 
  totWeightedDemand_1 = sum([demand_tmpD[i] * probs_tmpD[i[0]] for i in demand_tmpD.keys()])

  demand_tmpD_scaled = {}
  scaleFactorD = {}
  for i_d in disasterIDsUnq_tmp:
    sub_ids = [disasterIDsWithSubLocUnq_tmp[i] for i in range(len(disasterIDsWithSubLocUnq_tmp)) if disasterIDsWithSubLocUnq_tmp[i][0] == i_d]
    tot_demand_all_subs = sum([demand_tmpD[i] for i in sub_ids])
    scaled_factor = min(supplyTotalConstraint * 1. / tot_demand_all_subs, 1.)
    scaleFactorD.update({i_d: scaled_factor})
    for i_s in sub_ids:
      demand_tmpD_scaled.update({i_s: demand_tmpD[i_s] * scaled_factor})
      
  
  #demand_tmpD_scaled = deepcopy([demand_tmpD[i] * 1. / supplyTotalConstraint + 1e-6 for i in demand_tmpD.keys()])

  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  

  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDTmp.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))
 
  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpDTmp.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO

  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
    for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
      #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD_scaled[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
      pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD_scaled[kSubLoc], name = 'EnsureDemandSat_%s' %(k))
      #print 'wrong'
      #print inventory_tmpDTmp.keys()
      
    for i in inventory_tmpDTmp.keys():
      # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          try:
            pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
          except:
            m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
            raise NameError('stop')
          # Went to substring on 9/8/2014 due to gurobi error
          #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
        elif areInitialSuppliesVariables_Flag == 3:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')
        
  
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")
      
  # Added 9/19
    
      
  m.update()  

  
  
  if areInitialSuppliesVariables_Flag == 2:
    m.ModelSense = -1
  elif areInitialSuppliesVariables_Flag == 3:
    print str(datetime.now()) + indent * 2 +  '  About to Solve worst depot'
    tmpWorstObj = -1
    tmpWorstDepot = None
    for i in inventory_tmpDBad.keys():
      #print str(datetime.now()) + indent +  ' -- Testing depot' + str(i)
      for j in inventory_tmpDBad.keys():
        inventory_tmpDBad[j] = 0
      inventory_tmpDBad[i] = supplyTotalConstraint
      #print 'inventory vect'
      #print inventory_tmpDBad
      for k in disasterIDsUnq_tmp:
        disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
        for i2 in inventory_tmpDTmp.keys():
          if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
            m.remove(pi_inventoryBalance[(k, i2)])
            pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
      m.update()
      m.optimize()
      if m.status != GRB.status.OPTIMAL:
        print m.status
        raise NameError('Non-optimal LP')
      tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))

      if tmpTmpObj > tmpWorstObj:
        #print 'found new bad depot'
        tmpWorstObj = deepcopy(tmpTmpObj)
        tmpWorstDepot = deepcopy(i)

    for i2 in inventory_tmpDTmp.keys():
      inventory_tmpDTmp[i2] = 0
    inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      for i2 in inventory_tmpDTmp.keys():
        if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
          m.remove(pi_inventoryBalance[(k, i2)])
          pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      

    print str(datetime.now()) + indent * 2 +  '  Just Solved worst depot'  
      
  print str(datetime.now()) + indent * 2 +  '  About to Solve'    
  m.update()
  m.optimize()
  print str(datetime.now()) + indent * 2 +  '  Just Solved'

  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])

  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])

  myWeightedDemand = totWeightedDemand_1 

  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])

  myFractionOfDisastersUsingDummy = sum([probs_tmpD[k1] for k1 in disasterIDsUnq_tmp if scaleFactorD[k1] < 0.99999 * 1.])

  print str(datetime.now()) + indent * 2 +  '  Doing duals'  
  disasterIDsWithSubLocUnq_tmpD = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmpD.update({k: [ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k]})  
  

  dualsInvNoDum_PlusDummyCost = {}

  for i in inventory_tmpDTmp.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi

    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))
  dualsInvNoDum_UnAdj = deepcopy(dualsInvNoDum_PlusDummyCost)
  for i in dualsInvNoDum_PlusDummyCost.keys():
    dualsInvNoDum_UnAdj.update({i: dualsInvNoDum_PlusDummyCost[i] - myFractionOfDisastersUsingDummy * bigMCostDummy})

  dualsInvNoDum_All = {}
  for i in inventory_tmpDTmp.keys():
    for k in disasterIDsUnq_tmp:
      if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))

  print str(datetime.now()) + indent * 2 +  '  Doing myFlow'    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  print str(datetime.now()) + indent * 2 +  '  Doing myFlowNoDum'  
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  print str(datetime.now()) + indent * 2 +  '  Doing myOptInvNoDum'  
  myOptInvNoDum = {}
  for i in inventory_tmpDTmp.keys():
    if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    elif areInitialSuppliesVariables_Flag == 3:
      myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
  
  myOutDict = {'myObj': myObj.getConstant()
                , 'myObjNoDum': myObjNoDum.getConstant()
                , 'myWeightedDemand': myWeightedDemand
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant()
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All
                , 'myFlowNoDum': myFlowNoDum
                , 'myFlow': myFlow
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
              }

  
  return myOutDict


      




      

def f_solveStochLPDisasterGurobiCostConstraintSubLoc(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDsUnq_tmp
                                  , disasterIDsWithSubLocUnq_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , costConstraintsD
                                  , constraintNumberUpperLimit
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):














  #costD = timePerItem_tmpD
  #costConstraintsD = costPerItem_tmpD
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000
  #areInitialSuppliesVariables_Flag = 0
  #constraintNumberUpperLimit = 1e100
  
  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  
  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  
  
  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpD.keys()
                      for ((k, XJUNK), j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

                      
                      
  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))

  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpD.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  
 
 

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO
  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDsUnq_tmp:
    disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
    for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
      #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
      pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD[kSubLoc], name = 'EnsureDemandSat_%s' %(k))

    for i in inventory_tmpD.keys():
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpD[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')      
          

          
  if areInitialSuppliesVariables_Flag == 1:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpD.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")

          
          
  #Efficient Frontier Constrained Cost 
  pi_constrainedCost = m.addConstr(quicksum(x_satDemand[k, i, j, v] * 
                                                      costConstraintsD[(i, j, v)] * 
                                                      probs_tmpD[k]
                                           for (k, i, j, v) in myArcs_SetDemandNoDummy) <= constraintNumberUpperLimit)
          
          
  m.update()
    
  print str(datetime.now()) +  ' -- About to Solve'
  m.optimize()
  print str(datetime.now()) +  ' -- Just Solved'
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  
  #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDsUnq_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDsUnq_tmp)
  
  dualsInvNoDum_PlusDummyCost = {}
  for i in inventory_tmpD.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))

 
  dualsInvNoDum_UnAdj = {}
  for i in inventory_tmpD.keys():
    myTmpDual = 0
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))

  dualsInvNoDum_All = {}
  for i in inventory_tmpD.keys():
    for k in disasterIDsUnq_tmp:
      disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
      if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))

        
    
    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
  
  myOptInvNoDum = {}
  for i in inventory_tmpD.keys():
    if areInitialSuppliesVariables_Flag == 1:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
    
  myOutDict = {'myObj': myObj
                , 'myObjNoDum': myObjNoDum
                , 'myWeightedDemand': myWeightedDemand
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All                
                , 'myFlow': myFlow
                , 'myFlowNoDum': myFlowNoDum
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
                , 'constrainedNumber': pi_constrainedCost.Pi
              }

  return myOutDict  
  
  
  
  
  
  
  
   
   
   
"""   
def f_solveStochLPDisasterGurobiCostConstraint(demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , disasterIDs_tmp
                                  , inventory_tmpD
                                  , transModesTransParams
                                  , bigMCostElim
                                  , bigMCostDummy
                                  , costD
                                  , costConstraintsD
                                  , constraintNumberUpperLimit
                                  , dummyNodeName
                                  , areInitialSuppliesVariables_Flag
                                  ):

  #costD = timePerItem_tmpD
  #bigMCostElim = 1000000
  #bigMCostDummy = 10000000


  #------------------------------------------------------------------------------
  # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
  supplyTotalConstraint = sum(inventory_tmpD.values())
  maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
  inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
  inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
  
  costDDum = deepcopy(dict(costD.items()))
  for jn_disaster in demandAddress_tmpD.values():
    for vn_mode in transModesTransParams:
      costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  
  
  myArcs_SatDemand = tuplelist([(k, i, j, v)
                      for i in inventory_tmpDDum.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
                      ])
  
  myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
                      for i in inventory_tmpD.keys()
                      for (k, j) in demandAddress_tmpD.items()
                      for v in transModesTransParams
                      if costD[(i, j, v)] < bigMCostElim 
                      ])

  m = Model('StochLP')

  x_satDemand = {}
  for (k, i, j, v) in myArcs_SatDemand:
        x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
                               name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))

  x_howToAllocateInitialInventory = {}
  for i in inventory_tmpD.keys():
    x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

  m.update()

  # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO
  pi_meetDemand = {}
  pi_inventoryBalance = {}
  for k in disasterIDs_tmp:
    #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
    pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == demand_tmpD[k], name = 'EnsureDemandSat_%s' %(k))

    for i in inventory_tmpD.keys():
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        if areInitialSuppliesVariables_Flag == 1:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
        elif areInitialSuppliesVariables_Flag == 0:
          pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpD[i], name = 'EnsureShipLessInv_%s' %(i))
        else:
          raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')      
  if areInitialSuppliesVariables_Flag == 1:        
    pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpD.keys()) == supplyTotalConstraint
          , "EnsureTotalInitialSupplyMatchesTotal")

          
          
  #Efficient Frontier Constrained Cost 
  pi_constrainedCost = m.addConstr(quicksum(x_satDemand[k, i, j, v] * 
                                                      costConstraintsD[(i, j, v)] * 
                                                      probs_tmpD[k]
                                           for (k, i, j, v) in myArcs_SetDemandNoDummy) <= constraintNumberUpperLimit)
          
          
  m.update()
    
  print str(datetime.now()) +  ' -- About to Solve'
  m.optimize()
  print str(datetime.now()) +  ' -- Just Solved'
  #print 'just solved'
  if m.status != GRB.status.OPTIMAL:
    print m.status
    raise NameError('Non-optimal LP')

  myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
  # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
  myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
  
  myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
  
  
  dualsInvNoDum_PlusDummyCost = {}
  for i in inventory_tmpD.keys():
    myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_PlusDummyCost.update({i: myTmpDual})

  dualsInvNoDum_UnAdj = {}
  for i in inventory_tmpD.keys():
    myTmpDual = 0
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        myTmpDual += pi_inventoryBalance[(k, i)].Pi
    dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))

  dualsInvNoDum_All = {}
  for i in inventory_tmpD.keys():
    for k in disasterIDs_tmp:
      if len([costDDum[(i, demandAddress_tmpD[k], v1)] for v1 in transModesTransParams if costDDum[(i, demandAddress_tmpD[k], v1)] < bigMCostElim]) > 0:
        dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))
    
    
    
  myFlow = {}
  for   (k, i, j, v) in myArcs_SatDemand:
    if x_satDemand[(k, i, j, v)].x > 0:
      myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
    
  myFlowNoDum = {}
  for (k, i, j, v) in myArcs_SatDemand:
    if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
      myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})
  
  myOptInvNoDum = {}
  for i in inventory_tmpD.keys():
    if areInitialSuppliesVariables_Flag == 1:
      myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
    else:
      myOptInvNoDum.update({i: None})
      
  if areInitialSuppliesVariables_Flag == 1:
    dualTotInv = pi_totalSystemInventory.Pi
  else:
    dualTotInv = None  
    
  myOutDict = {'myObj': myObj
                , 'myObjNoDum': myObjNoDum
                , 'myWeightedDemand': myWeightedDemand
                , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum
                , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
                , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
                , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
                , 'dualsInvNoDum_All': dualsInvNoDum_All                
                , 'myFlow': myFlow
                , 'myFlowNoDum': myFlowNoDum
                , 'myOptInvNoDum': myOptInvNoDum
                , 'dualTotInv': dualTotInv
                , 'constrainedNumber': pi_constrainedCost.Pi
              }

  
  return myOutDict  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    macroScenarioInfoHeaders = ['StartingInvTotal', 'Month', 'NumMonthsToAvg', 'MacroScenDesc', 'ChangeInitialSupplyFlag', 'setDummyCostHere', 'setScenarioProbabilitiesTo1OverN_Flag']
    macroScenarioData = [macroTotSupply, macroMonth, macroNumMonthsAvg, macroScenarioDesc , areInitialSuppliesVariables_Flag, setDummyCostAndSupplyHere_Flag, setScenarioProbabilitiesTo1OverN_Flag]
    
    
    print str(datetime.now()) +  ' -- About to assign demand'    
    demandAssignmentsHeader = ['Scenario', 'TimeBlock', 'Depot', 'Disaster', 'Flow'] + macroScenarioInfoHeaders    
    demandAssignments = [demandAssignmentsHeader]
    for (s,t, i, j) in myArcs_SatDemand:
        if x_satDemand[s, t, i, j].x > 0:
            demandAssignments.append([s, t, i, j, round(x_satDemand[s, t, i, j].x, 2)] + macroScenarioData)
    
    print str(datetime.now()) +  ' -- About to Scenario Summarize'
    summaryScenarioHeader = ['Scenario', 'Probability', 'ScenarioDemand', 'ScenarioDemandSatisfiedFromDepots', 'LPCost', 'IncurredCost', 'LPCostNoDummy', 'IncurredCostNoDummy'] + macroScenarioInfoHeaders  
    summaryScenario = [summaryScenarioHeader]


    for s in scenarioNamesSet:
        scenarioDemand = quicksum([demand[s1, t, j] for (s1, t, j) in myDemandNamesTup.select(s, '*', '*')])
        scenarioDemandSatisfiedFromDepots = quicksum([x_satDemand[s1, t, i, j].x  for (s1, t, i, j) in myArcs_SetDemandNoDummy.select(s, '*', '*', '*') ])
        lCost = quicksum([x_satDemand[s1, t, i, j].x * costs[i, j] for (s1, t, i, j) in myArcs_SatDemand.select(s, '*', '*', '*')])
        iCost = quicksum([x_satDemand[s1, t, i, j].x * costsMeasure[i, j] for (s1, t, i, j) in myArcs_SatDemand.select(s, '*', '*', '*')])
        lCostNoDumb = quicksum([x_satDemand[s1, t, i, j].x * costs[i, j] for (s1, t, i, j) in myArcs_SetDemandNoDummy.select(s, '*', '*', '*') ])
        iCostNoDumb = quicksum([x_satDemand[s1, t, i, j].x * costsMeasure[i, j] for (s1, t, i, j) in myArcs_SetDemandNoDummy.select(s, '*', '*', '*') ])
        summaryScenario.append([s, probs[s], scenarioDemand, scenarioDemandSatisfiedFromDepots, lCost, iCost, lCostNoDumb,  iCostNoDumb] + macroScenarioData)        
    
        
        
    print str(datetime.now()) +  ' -- About to do some other stuff'    
    summaryHeaderBasic = ['LPWeightedCost', 'IncurredWeightedCost', 'LPWeightedCostNoDummy', 'IncurredWeightedCostNoDummy', 'TotalDemandWeighted', 'TotalDemandSatisfiedFromDepotsWeighted'] 
    summaryHeader = summaryHeaderBasic + macroScenarioInfoHeaders
    summaryOverall = [summaryHeader]        
    lCost2 = sum([x_satDemand[s, t, i, j].x * costs[i, j] * probs[s] for (s, t, i, j) in myArcs_SatDemand])
    iCost2 = sum([x_satDemand[s, t, i, j].x * costsMeasure[i, j] * probs[s] for (s, t, i, j) in myArcs_SatDemand])
    lCostNoDummy2 = sum([x_satDemand[s, t, i, j].x * costs[i, j] * probs[s] for (s, t, i, j) in myArcs_SatDemand if i in depotNamesSetNoDummy])
    iCostNoDummy2 = sum([x_satDemand[s, t, i, j].x * costsMeasure[i, j] * probs[s] for (s, t, i, j) in myArcs_SatDemand if i in depotNamesSetNoDummy])
    scenarioDemand2 = sum([demand[s, t, j] * probs[s] for (s, t, j) in myDemandNamesTup])
    scenarioDemandSatisfiedFromDepots2 = sum([x_satDemand[s, t, i, j].x * probs[s]  for (s, t, i, j) in myArcs_SatDemand if i in depotNamesSetNoDummy] )    
    summaryOverallData = [lCost2, iCost2, lCostNoDummy2, iCostNoDummy2, scenarioDemand2, scenarioDemandSatisfiedFromDepots2 ]   
    summaryOverall.append(summaryOverallData + macroScenarioData)

    
    
    print str(datetime.now()) +  ' -- About to write initial supplies'
    initialSuppliesHeader = ['Depot', 'StartingAmount'] + macroScenarioInfoHeaders
    initialSupplies = [initialSuppliesHeader]
    for i in depotNamesSet:
        initialSupplies.append([i, x_howToAllocateInitialInventory[i].x] + macroScenarioData)

    initialSuppliesHeaderFlat = [i for i in depotNamesSetNoDummy] + summaryHeaderBasic + macroScenarioInfoHeaders
    initialSuppliesFlat = [initialSuppliesHeaderFlat]
    initialSuppliesFlat.append([x_howToAllocateInitialInventory[i].x for i in depotNamesSetNoDummy] + summaryOverallData + macroScenarioData)
        
    #f_printAsCsv(summary)    
    return([demandAssignments, summaryScenario, summaryOverall, initialSupplies, initialSuppliesFlat])    
        
 
"""        
        

# def f_solveStochLPDisasterGurobiSubLoc3(demand_tmpD
#                                   , demandAddress_tmpD
#                                   , probs_tmpD
#                                   , disasterIDsUnq_tmp
#                                   , disasterIDsWithSubLocUnq_tmp
#                                   , inventory_tmpD
#                                   , transModesTransParams
#                                   , bigMCostElim
#                                   , bigMCostDummy
#                                   , costD
#                                   , dummyNodeName
#                                   , areInitialSuppliesVariables_Flag
#                                   , depotWhichFixedSubset
#                                   , minInvItemD
#                                   , depotInWhichCountry
#                                   ):

#   #costD = myCostsToIterateD['Cost']
#   #areInitialSuppliesVariables_Flag = myLPInitialSuppliesVariables_FlagD['Optimal']
#   #bigMCostElim = 1000000
#   #bigMCostDummy = 10000000

#   indent = '        '
#   #------------------------------------------------------------------------------
#   # Adds a dummy node to the inventory dictionary, the cost dictionary, and the time dictionary
#   #inventory_tmpD['Accra, Ghana'] += 1
#   # myMaxKeyLength = 40
#   # for i in inventory_tmpD.keys():
#     # if i == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
#       # #> myMaxKeyLength:
#       # inventory_tmpD['Moffett'] = inventory_tmpD.pop(i)
  
#   # for i in costD.keys():
#     # if i[0] == 'Moffett Field Historical Society Museum, Severyns Avenue, Mountain View, CA 94043, USA': 
#       # costD[('Moffett', i[1], i[2])] = costD.pop(i)
#   print("Function Call!")


#   supplyTotalConstraint = sum(inventory_tmpD.values())
#   maxDemand = demand_tmpD[f_keyWithMaxVal(demand_tmpD)]
#   inventory_tmpDDum = deepcopy(dict(inventory_tmpD.items()))
#   inventory_tmpDDum.update({dummyNodeName: maxDemand + 1})
#   inventory_tmpDTmp = deepcopy(inventory_tmpD)
#   inventory_tmpDBad = deepcopy(inventory_tmpD)
  
#   if sum(minInvItemD.values()) > supplyTotalConstraint:
#     minDemandScale = sum(minInvItemD.values()) / supplyTotalConstraint
#     minInvItemD_tmp = {}
#     for i in minInvItemD.keys():
#       minInvItemD_tmp.update({i: int(numpy.floor(minInvItemD[i] / minDemandScale * 0.99))})
#   else:  
#     minInvItemD_tmp = {}
#     for i in minInvItemD.keys():
#       minInvItemD_tmp.update({i: int(numpy.floor(minInvItemD[i] ))})

 
#   costDDum = deepcopy(dict(costD.items()))
#   for jn_disaster in demandAddress_tmpD.values():
#     for vn_mode in transModesTransParams:
#       costDDum.update({(dummyNodeName, jn_disaster, vn_mode): bigMCostDummy  })

  

#   myArcs_SatDemand = tuplelist([(k, i, j, v)
#                       for i in inventory_tmpDDum.keys()
#                       for ((k, XJUNK), j) in demandAddress_tmpD.items()
#                       for v in transModesTransParams
#                       if costDDum[(i, j, v)] < bigMCostElim or i == dummyNodeName
#                       ])
  
#   myArcs_SetDemandNoDummy = tuplelist([(k, i, j, v)
#                       for i in inventory_tmpDTmp.keys()
#                       for ((k, XJUNK), j) in demandAddress_tmpD.items()
#                       for v in transModesTransParams
#                       if costD[(i, j, v)] < bigMCostElim 
#                       ])

#   m = Model('StochLP')

#   x_satDemand = {}
#   for (k, i, j, v) in myArcs_SatDemand:
#         x_satDemand[(k, i, j, v)] = m.addVar(lb = 0, obj = costDDum[(i, j, v)] * probs_tmpD[k], \
#                                name='xSatFlow_%s_%s_%s_%s' % (k, i, j, v))
 
#   x_howToAllocateInitialInventory = {}
#   for i in inventory_tmpDTmp.keys():
#     x_howToAllocateInitialInventory[i] = m.addVar(lb = 0, name = 'x_howToAllocateInitialInventory_%s' % (i)) #, vtype = 'I')

#   m.update()

#   # RIGHT NOW SET UP JUST TO DO ONE DEMAND NODE PER SCENARIO

#   pi_meetDemand = {}
#   pi_inventoryBalance = {}
#   for k in disasterIDsUnq_tmp:
#     disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#     for kSubLoc in disasterIDsWithSubLocUnq_tmp_subset:
#       #pi_meetDemand[k] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[k], '*')) == min(demand_tmpD[k],supplyTotalConstraint - 1e-6), name = 'EnsureDemandSat_%s' %(k))
#       pi_meetDemand[kSubLoc] = m.addConstr(quicksum(x_satDemand[(k, i, j, v)] for (k, i, j, v) in myArcs_SatDemand.select(k, '*', demandAddress_tmpD[kSubLoc], '*')) == demand_tmpD[kSubLoc], name = 'EnsureDemandSat_%s' %(k))
#       #print 'wrong'
#       #print inventory_tmpDTmp.keys()
      
#     for i in inventory_tmpDTmp.keys():
#       # Added if statement on 9/19/2014 because with cutoffs, some depots had no demands.
#       if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
#           pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= x_howToAllocateInitialInventory[i], name = 'EnsureShipLessInv_%s' %(i))
#         elif areInitialSuppliesVariables_Flag == 0:
#           try:
#             pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
#           except:
#             m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i], name = 'EnsureShipLessInv_%s' %(i))
#             raise NameError('stop')
#           # Went to substring on 9/8/2014 due to gurobi error
#           #pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDTmp[i]) #, name = 'EnsureShipLessInv_%s' %(i[:20]))
#         elif areInitialSuppliesVariables_Flag == 3:
#           pi_inventoryBalance[(k, i)] = m.addConstr(quicksum(x_satDemand[k, i, j, v] for (k, i, j, v) in myArcs_SatDemand.select(k, i, '*', '*')) <= inventory_tmpDBad[i], name = 'EnsureShipLessInv_%s' %(i))
#         else:
#           raise NameError('You do not kave a valid areInitialSuppliesVariables_Flag within the optimization function')


#   if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:  
#     pi_minInvPerCountry = {}  
#     print '***%&%^$&$&$&$&^$ You are excluding Palau manually'
#     for i_ctry in list(set(depotInWhichCountry.values())):
      
#       if i_ctry not in ['Palau', 'Malaysia', 'Papua New Guinea']:

#         #print 'country', i_ctry
#         #print 'depots', [i for i in depotInWhichCountry.keys() if depotInWhichCountry[i] == i_ctry]
#         pi_minInvPerCountry[i_ctry] = m.addConstr(
#                                         sum(
#                                             [x_howToAllocateInitialInventory[i] for i in depotInWhichCountry.keys() if depotInWhichCountry[i] == i_ctry]
#                                             ) >= minInvItemD_tmp[i_ctry]
#                                         , "EnsureMinInvEachCntry"
#                                         )
  
#   if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:        
#     pi_totalSystemInventory = m.addConstr(quicksum(x_howToAllocateInitialInventory[i] for i in  inventory_tmpDTmp.keys()) == supplyTotalConstraint
#           , "EnsureTotalInitialSupplyMatchesTotal")
    
#     for i in depotWhichFixedSubset:
#         pi_fixed_inv = m.addConstr(x_howToAllocateInitialInventory[i] == inventory_tmpDTmp[i])
     
#   # Added 9/19
    
      
#   m.update()  

  
  
#   if areInitialSuppliesVariables_Flag == 2:
#     m.ModelSense = -1
#   elif areInitialSuppliesVariables_Flag == 3:
#     print str(datetime.now()) + indent * 2 +  '  About to Solve worst depot'
#     tmpWorstObj = -1
#     tmpWorstDepot = None
#     for i in inventory_tmpDBad.keys():
#       #print str(datetime.now()) + indent +  ' -- Testing depot' + str(i)
#       for j in inventory_tmpDBad.keys():
#         inventory_tmpDBad[j] = 0
#       inventory_tmpDBad[i] = supplyTotalConstraint
#       #print 'inventory vect'
#       #print inventory_tmpDBad
#       for k in disasterIDsUnq_tmp:
#         disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#         for i2 in inventory_tmpDTmp.keys():
#           if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#             m.remove(pi_inventoryBalance[(k, i2)])
#             pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDBad[i2], name = 'EnsureShipLessInv_%s' %(i2))
#       m.update()
#       m.optimize()
#       if m.status != GRB.status.OPTIMAL:
#         print m.status
#         raise NameError('Non-optimal LP')
#       tmpTmpObj = deepcopy(quicksum([x_satDemand[(k1, i1, j1, v1)].x * costD[(i1, j1, v1)] * probs_tmpD[k1] for (k1, i1, j1, v1) in myArcs_SatDemand if i1 != dummyNodeName]))
#       #print 'tmpTmpObj = ' + str(tmpTmpObj)
#       #print 'tmpWOrst  = ' + str(tmpWorstObj)
#       #print 'old worst depot = ' + str(tmpWorstDepot)
#       #print 'i = ' + str(i)
#       if tmpTmpObj > tmpWorstObj:
#         #print 'found new bad depot'
#         tmpWorstObj = deepcopy(tmpTmpObj)
#         tmpWorstDepot = deepcopy(i)
#         #print 'newWorstObj = ' + str(tmpWorstObj)
#         #print 'newWOrstDepot = ' + str(tmpWorstDepot)
#     #print 'old Inv vect'
#     #print inventory_tmpDTmp    
#     for i2 in inventory_tmpDTmp.keys():
#       inventory_tmpDTmp[i2] = 0
#     inventory_tmpDTmp[tmpWorstDepot] = supplyTotalConstraint    
#     for k in disasterIDsUnq_tmp:
#       disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#       for i2 in inventory_tmpDTmp.keys():
#         if len([costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i2, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#           m.remove(pi_inventoryBalance[(k, i2)])
#           pi_inventoryBalance[(k, i2)] = m.addConstr(quicksum(x_satDemand[k, i2, j, v] for (k, i2, j, v) in myArcs_SatDemand.select(k, i2, '*', '*')) <= inventory_tmpDTmp[i2], name = 'EnsureShipLessInv_%s' %(i2))      
#     #print 'new Inv vect'
#     #print inventory_tmpDTmp   
#     print str(datetime.now()) + indent * 2 +  '  Just Solved worst depot'  
    
      
#   print str(datetime.now()) + indent * 2 +  '  About to Solve'    
#   m.update()
#   m.optimize()
#   print str(datetime.now()) + indent * 2 +  '  Just Solved'
#   #print 'sum from accra'
#   #print quicksum(x_satDemand[k, 'Accra, Ghana', j, v].x for (k, i2, j, v) in myArcs_SatDemand.select(k, 'Accra, Ghana', '*', '*'))
#   #print 'just solved'
#   if m.status != GRB.status.OPTIMAL:
#     print m.status
#     raise NameError('Non-optimal LP')

    
#   #print str(datetime.now()) + indent +  '  Doing Test'    
#   #for   (k, i, j, v) in myArcs_SatDemand.select('ID:9841', '*', '*', '*'):
#   #  print 'k = ' + str(k) + ';i = ' + str(i) + ';j = ' + str(j) + ';v = ' + str(v) + ';flow = ' + str(x_satDemand[(k, i, j, v)].x)
#   #raise NameError('vvv')  
    
    
    
#   #print str(datetime.now()) + indent +  '  part 1'  
#   myObj = quicksum([x_satDemand[(k, i, j, v)].x * costDDum[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
#   #print myObj
#   #print str(datetime.now()) + indent +  '  part 2'  
#   myObjNoDum = quicksum([x_satDemand[(k, i, j, v)].x * costD[(i, j, v)] * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
#   #print myObjNoDum
#   #print str(datetime.now()) + indent +  '  part 3'  
#   myWeightedDemand = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand])
#   # quicksum(demand_tmpD[k] *  probs_tmpD[k] for k in disasterIDs_tmp)
#   #print str(datetime.now()) + indent +  '  part 4'  
#   myWeightedDemandMetNoDum = quicksum([x_satDemand[(k, i, j, v)].x * probs_tmpD[k] for (k, i, j, v) in myArcs_SatDemand if i != dummyNodeName])
  
#   #print str(datetime.now()) + indent +  '  part 5'  
#   # This is pre multiple locs per disastser #myFractionOfDisastersUsingDummy = sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > supplyTotalConstraint]) * 1. / len(disasterIDs_tmp)
#   #myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand if i == dummyNodeName and k == k1]) > 0]) * 1. / len(disasterIDsUnq_tmp)
#   myFractionOfDisastersUsingDummy = sum([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k, i, j, v)].x for (k, i, j, v) in myArcs_SatDemand.select(k1, dummyNodeName, '*', '*')]).getConstant() > 0]) * 1. / len(disasterIDsUnq_tmp)
#   #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
#   #print str(datetime.now()) + indent +  '  part 5 faster'  
#   #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if quicksum([x_satDemand[(k1, dummyNodeName, j, v)].x for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) > 0]) * 1. / len(disasterIDsUnq_tmp)
#   #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
#   #print str(datetime.now()) + indent +  '  part 5 fastest 1'  
#   #myFractionOfDisastersUsingDummy = len([1 for k1 in disasterIDsUnq_tmp if x_satDemand[(k1, dummyNodeName, j, v)].x > 0 for (k1, dummyNodeName, j, v) in myArcs_SatDemand]) * 1. / len(disasterIDsUnq_tmp)
#   #print 'myFractionOfDisastersUsingDummy = ', myFractionOfDisastersUsingDummy
  
#   #print str(datetime.now()) + indent +  '  part 5 ended'  
#   #print myFractionOfDisastersUsingDummy
#   #print myWeightedDemandMetNoDum
#   #print myWeightedDemand
  
  
  
#   #sum([1 for k in disasterIDs_tmp if demand_tmpD[k] > sum(inventory_tmpDTmp.values())]) * 1. / len(disasterIDs_tmp)
#   print str(datetime.now()) + indent * 2 +  '  Doing duals'  
#   disasterIDsWithSubLocUnq_tmpD = {}
#   for k in disasterIDsUnq_tmp:
#     disasterIDsWithSubLocUnq_tmpD.update({k: [ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k]})  
  
#   #print str(datetime.now()) + indent +  '  Just made dict'  
  
  
#   # dualsInvNoDum_PlusDummyCost = {}
#   # kCount = 0
#   # for i in inventory_tmpDTmp.keys():
#     # myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
#     # for k in disasterIDsUnq_tmp:
#       # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#       # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         # myTmpDual += pi_inventoryBalance[(k, i)].Pi
#         # kCount += 1
#     # dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))


#   dualsInvNoDum_PlusDummyCost = {}
#   #kCount = 0
#   for i in inventory_tmpDTmp.keys():
#     myTmpDual = myFractionOfDisastersUsingDummy * bigMCostDummy
#     for k in disasterIDsUnq_tmp:
#       if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         myTmpDual += pi_inventoryBalance[(k, i)].Pi
#         #kCount += 1
#     dualsInvNoDum_PlusDummyCost.update(deepcopy({i: myTmpDual}))



    
#   # print str(datetime.now()) + indent +  '  kCount = ' + str(kCount)  
  
#   # print str(datetime.now()) + indent +  '  Doing duals part 2'  
#   # dualsInvNoDum_UnAdj = {}
#   # for i in inventory_tmpDTmp.keys():
#     # myTmpDual = 0
#     # for k in disasterIDsUnq_tmp:
#       # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#       # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         # myTmpDual += pi_inventoryBalance[(k, i)].Pi
#     # dualsInvNoDum_UnAdj.update(deepcopy({i: myTmpDual}))
#   # print ''
#   # print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)  
#   # print ''
#   # print ''  
  
#   dualsInvNoDum_UnAdj = deepcopy(dualsInvNoDum_PlusDummyCost)
#   for i in dualsInvNoDum_PlusDummyCost.keys():
#     dualsInvNoDum_UnAdj.update({i: dualsInvNoDum_PlusDummyCost[i] - myFractionOfDisastersUsingDummy * bigMCostDummy})
#   #print 'Old duals are = ' + str(dualsInvNoDum_UnAdj)    
#   #print str(datetime.now()) + indent +  '  Doing duals part 3'    
#   # dualsInvNoDum_All = {}
#   # for i in inventory_tmpDTmp.keys():
#     # for k in disasterIDsUnq_tmp:
#       # disasterIDsWithSubLocUnq_tmp_subset = deepcopy([ii for ii in disasterIDsWithSubLocUnq_tmp if ii[0] == k])
#       # if len([costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmp_subset if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         # dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))
        
#   dualsInvNoDum_All = {}
#   for i in inventory_tmpDTmp.keys():
#     for k in disasterIDsUnq_tmp:
#       if len([1 for v1 in transModesTransParams for kSubLocTmp in disasterIDsWithSubLocUnq_tmpD[k] if costDDum[(i, demandAddress_tmpD[kSubLocTmp], v1)] < bigMCostElim]) > 0:
#         dualsInvNoDum_All.update(deepcopy({(k, i): pi_inventoryBalance[(k, i)].Pi}))


#   #print str(datetime.now()) + indent +  '  Doing duals done'      
#   #assert False

#   print str(datetime.now()) + indent * 2 +  '  Doing myFlow'    
#   myFlow = {}
#   for   (k, i, j, v) in myArcs_SatDemand:
#     if x_satDemand[(k, i, j, v)].x > 0:
#       myFlow.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

#   #for   (k, i, j, v) in myArcs_SatDemand:
#   #  print str(k) + ';' + str(i) + ';' + str(j) + ';' + str(v) + ';' + str(x_satDemand[(k, i, j, v)].x)
#   #raise NameError('UUU')

#   print str(datetime.now()) + indent * 2 +  '  Doing myFlowNoDum'  
#   myFlowNoDum = {}
#   for (k, i, j, v) in myArcs_SatDemand:
#     if i != dummyNodeName and x_satDemand[(k, i, j, v)].x > 0:
#       myFlowNoDum.update({(k, i, j, v): x_satDemand[(k, i, j, v)].x})

#   print str(datetime.now()) + indent * 2 +  '  Doing myOptInvNoDum'  
#   myOptInvNoDum = {}
#   for i in inventory_tmpDTmp.keys():
#     if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
#       myOptInvNoDum.update({i: x_howToAllocateInitialInventory[i].x})
#     elif areInitialSuppliesVariables_Flag == 3:
#       myOptInvNoDum.update({i: inventory_tmpDTmp[i]})
#     else:
#       myOptInvNoDum.update({i: None})
      
#   if areInitialSuppliesVariables_Flag == 1 or areInitialSuppliesVariables_Flag == 2:
#     dualTotInv = pi_totalSystemInventory.Pi
#   else:
#     dualTotInv = None  
#   #assert False  
#   #print ''
#   #print 'myObjNoDum = ', myObjNoDum
#   #m.update()
#   #print 'myObjNoDum = ', myObjNoDum
#   #print 'myObjNoDum.const = ', myObjNoDum.getConstant()
#   #print ''
#   #assert False
#   myOutDict = {'myObj': myObj.getConstant()
#                 , 'myObjNoDum': myObjNoDum.getConstant()
#                 , 'myWeightedDemand': myWeightedDemand.getConstant()
#                 , 'myWeightedDemandMetNoDum': myWeightedDemandMetNoDum.getConstant()
#                 , 'myFractionOfDisastersUsingDummy': myFractionOfDisastersUsingDummy
#                 , 'dualsInvNoDum_PlusDummyCost': dualsInvNoDum_PlusDummyCost
#                 , 'dualsInvNoDum_UnAdj': dualsInvNoDum_UnAdj
#                 , 'dualsInvNoDum_All': dualsInvNoDum_All
#                 , 'myFlowNoDum': myFlowNoDum
#                 , 'myFlow': myFlow
#                 , 'myOptInvNoDum': myOptInvNoDum
#                 , 'dualTotInv': dualTotInv
#               }

#   return myOutDict