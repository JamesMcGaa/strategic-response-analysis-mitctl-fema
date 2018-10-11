import pandas as pd                
import os
import matplotlib.pyplot as plt
import sys
import numpy as np
from datetime import datetime
from gurobipy import *

drivingDistanceMatrixFileName = 'drivingDistanceMatrixFEMACountyv2.csv' #'drivingDistanceMatrix.csv' # 'drivingDistanceMatrixFEMACountyv2.csv'
carrierDataFileName =  'fakeCarrierDataFEMA_nototcaplimit.csv' # 'fakeCarrierDataFEMA_onlySM.csv' #'fakeCarrierDataFEMA_nototcap_reduced.csv'  #'fakeCarrierDataFEMA_nototcaplimit.csv' #'fakeCarrierDataFEMA.csv' 
disasterTotAffectedFileName = 'disasterAffectedDataFEMACountyv2.csv' # 'disasterAffectedDataFEMACountyv2.csv' #disasterAffectedDataFEMA.csv
depotInventoryFileName = 'depotInventoryDataFEMA.csv' #'depotInventoryData.csv' 

#Penalize items based on weight or volume
itemAttributesFileName =  'itemAttributesFEMA.csv' # 'itemAttributes.csv'

#Covert people affected into items demanded
betaItemConversionsFileName = 'betaItemConversionsFEMA_oneday.csv' #'betaItemConversions.csv'

#Convert carrier capacity based on current item
conversionRatesFileName = 'fakeCarrierItemConversionRatesFEMA.csv'

bigMCostDummy = 1000000
bigInventoryDummy = 10000000000
n_itemIter = "Water"


output_folder = os.getcwd()+"\\outputData\\"+str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_")+"_"+n_itemIter
os.makedirs(output_folder)


def optimize():
    print("-------------------------------Start------------------------------")

    #Remap output to a new file
    old_stdout = sys.stdout
    log_file = open(output_folder+"\\output_"+n_itemIter+".log","w")
    sys.stdout = log_file

    #Read in inventory values for the particular item
    inventory_tmpD = {}
    matrix = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + depotInventoryFileName) 
    for index, row in matrix.iterrows():
        if row.ItemName == n_itemIter:
            inventory_tmpD[row.gglAddress] = row.Total

    #Generate cost matrices
    monetaryMatrix = {}
    timeMatrix = {}
    matrix = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + drivingDistanceMatrixFileName) 
    for index, row in matrix.iterrows():
      monetaryMatrix[((row.depotGglAddressAscii, row.disasterGglAddressAscii))] = row.distance_km
      timeMatrix[((row.depotGglAddressAscii, row.disasterGglAddressAscii))] = row.drivingTime_hrs

    #Find conversion factor to transform
    conversion_factor = 0
    beta_conversion_file = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + betaItemConversionsFileName) 
    for index, row in beta_conversion_file.iterrows():
      if row.Item == n_itemIter:
        conversion_factor = row.PersonsPerItem
    if conversion_factor == 0:
      print("Could not find beta conversion factor")
      sys.exit()

    #Generate raw inputs
    demand_tmpD = {}
    demandAddress_tmpD = {}
    probs_tmpD = {}

    current_disaster = 0
    disaster_to_ID_count = {}
    disaster_to_count = {}
    disasters = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + disasterTotAffectedFileName) 
    total_disasters = len(disasters)


    for index, row in disasters.iterrows():
      if (row.Day, row.Month, row.Year, row.Type) not in disaster_to_ID_count: #New date
        disaster_to_ID_count[(row.Day, row.Month, row.Year, row.Type)] = (current_disaster, 1)

        disasterString = "0" * (4 - len(str(current_disaster // 10000))) + str(current_disaster // 10000)
        disasterString += "-"
        disasterString += "0" * (4 - len(str(current_disaster % 10000))) + str(current_disaster % 10000)
        sublocationString = 'SubLoc_00000'

        demand_tmpD[(disasterString, sublocationString)] = int(row.TotAffected / conversion_factor)
        demandAddress_tmpD[(disasterString, sublocationString)] = row.gglAddress
        probs_tmpD[disasterString] = 0

        disaster_to_count[disasterString] = 1
        current_disaster += 1

      else: #Existing date
        ID = disaster_to_ID_count[(row.Day, row.Month, row.Year, row.Type)][0]
        count = disaster_to_ID_count[(row.Day, row.Month, row.Year, row.Type)][1]
        disaster_to_ID_count[(row.Day, row.Month, row.Year, row.Type)] = (ID, count+1)

        disasterString = "0" * (4 - len(str(ID // 10000))) + str(ID // 10000)
        disasterString += "-"
        disasterString += "0" * (4 - len(str(ID % 10000))) + str(ID % 10000)
        sublocationString = 'SubLoc_' + "0" * (5-len(str(count))) + str(count)

        demand_tmpD[(disasterString, sublocationString)] = int(row.TotAffected / conversion_factor)
        demandAddress_tmpD[(disasterString, sublocationString)] = row.gglAddress

        disaster_to_count[disasterString] += 1

    #Uniform probability
    for key in probs_tmpD:
      probs_tmpD[key] = 1.0 / len(probs_tmpD)



    adjusted_demand_tmpD = {}
    adjusted_demandAddress_tmpD = {}
    adjusted_probs_tmpD = {}
    adjusted_cost_matrix = {}
    adjusted_time_matrix = {}
    for ID in range(current_disaster):
      total_demand = 0
      disasterString = "0" * (4 - len(str(ID // 10000))) + str(ID // 10000)
      disasterString += "-"
      disasterString += "0" * (4 - len(str(ID % 10000))) + str(ID % 10000)

      for sublocationID in range(disaster_to_count[disasterString]):
        sublocationString = 'SubLoc_' + "0" * (5-len(str(sublocationID))) + str(sublocationID)
        total_demand += demand_tmpD[(disasterString, sublocationString)]

        for depotName in inventory_tmpD:
          indexPair = (depotName, "disasterWeightedAverage"+str(ID))

          if indexPair not in adjusted_time_matrix and indexPair not in adjusted_cost_matrix:
            adjusted_time_matrix[indexPair] = timeMatrix[(depotName, demandAddress_tmpD[(disasterString, sublocationString)])] * demand_tmpD[(disasterString, sublocationString)] 
            adjusted_cost_matrix[indexPair] = monetaryMatrix[(depotName, demandAddress_tmpD[(disasterString, sublocationString)])] * demand_tmpD[(disasterString, sublocationString)] 
          else:
            adjusted_time_matrix[indexPair] += timeMatrix[(depotName, demandAddress_tmpD[(disasterString, sublocationString)])] * demand_tmpD[(disasterString, sublocationString)] 
            adjusted_cost_matrix[indexPair] += monetaryMatrix[(depotName, demandAddress_tmpD[(disasterString, sublocationString)])] * demand_tmpD[(disasterString, sublocationString)] 

      for depotName in inventory_tmpD:
        indexPair = (depotName, "disasterWeightedAverage"+str(ID))
        adjusted_time_matrix[indexPair] /= float(total_demand)
        adjusted_cost_matrix[indexPair] /= float(total_demand)

      adjusted_demand_tmpD[(disasterString, 'SubLoc_00000')] = total_demand
      adjusted_demandAddress_tmpD[(disasterString, 'SubLoc_00000')] = "disasterWeightedAverage"+str(ID)
      adjusted_probs_tmpD[disasterString] = 1.0 / current_disaster

    demand_tmpD = adjusted_demand_tmpD
    demandAddress_tmpD = adjusted_demandAddress_tmpD
    probs_tmpD = adjusted_probs_tmpD
    monetaryMatrix = adjusted_cost_matrix
    timeMatrix = adjusted_time_matrix

    total_unique_disasters = len(demand_tmpD)

        
    plt.hist([disaster_to_count[key] for key in disaster_to_count], bins=np.arange(0, 3000, 25))
    plt.xlabel('Sublocations')
    plt.ylabel('Disaster Count')
    plt.gca().set_yscale("log")
    plt.title('Sublocation Counts (logscale)')
    plt.savefig(output_folder  +"\\sublocation_distribution.png")
    plt.close()
    
    plt.hist([disaster_to_count[key] for key in disaster_to_count], bins=np.arange(0, 500, 5))
    plt.xlabel('Sublocations')
    plt.ylabel('Disaster Count')
    plt.gca().set_yscale("log")
    plt.title('Sublocation Counts (logscale)')
    plt.savefig(output_folder  +"\\sublocation_distribution_trunc.png")
    plt.close()
    
    print("-------------------------------Disaster Stats------------------------------")
    print("Total disasters: " + str(total_unique_disasters))
    demands = [demand_tmpD[key] for key in demand_tmpD]
    print("Minimum demand: " + str(np.min(demands)))
    print("Maximum demand: " + str(np.max(demands)))
    print("Average demand: " + str(np.mean(demands)))
    print("Median demand: " + str(np.median(demands)))
    print("Standard deviation: " + str(np.std(demands)))
    print("1st Quartile: " + str(np.percentile(demands,25)))
    print("3rd Quartile: " + str(np.percentile(demands,75)))
    
    plt.hist(demands, bins=np.arange(0, 10000000, 100000))
    plt.xlabel('Total People Affected')
    plt.ylabel('Disaster Count')
    plt.title('Total People Affected')
    plt.savefig(output_folder  +"\\demand_distribution.png")
    plt.close()
    
    print("Total sublocations: " + str(total_disasters))
    SubLocsForStats = [disaster_to_count[key] for key in disaster_to_count]
    print("Minimum sublocations: " + str(np.min(SubLocsForStats)))
    print("Maximum sublocations: " + str(np.max(SubLocsForStats)))
    print("Average sublocations: " + str(np.mean(SubLocsForStats)))
    print("Median sublocations: " + str(np.median(SubLocsForStats)))
    print("Standard deviation: " + str(np.std(SubLocsForStats)))
    print("1st Quartile: " + str(np.percentile(SubLocsForStats,25)))
    print("3rd Quartile: " + str(np.percentile(SubLocsForStats,75)))       
    
    matrix2 = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + itemAttributesFileName) 
    for index, row in matrix2.iterrows():
        if row.ItemName == n_itemIter:
            ProductWeight = row.WeightMetricTon

    cross_validation = {}
    for mode in ["TIME", "MONETARY"]:
      if mode == "MONETARY":

        dummy_solution = dummyhelper( "MONETARY"
                                    , demand_tmpD
                                    , demandAddress_tmpD
                                    , probs_tmpD   
                                    , inventory_tmpD
                                    , monetaryMatrix
                                    , ProductWeight
                                    )
        cross_validation[("dummy","MONETARY")] = dummy_solution

        nonfixed_dummy_solution = nonfixeddummyinventoryhelper( "MONETARY"
                                                              , demand_tmpD
                                                              , demandAddress_tmpD
                                                              , probs_tmpD
                                                              , inventory_tmpD
                                                              , monetaryMatrix                                                              
                                                              , ProductWeight
                                                              )
        cross_validation[("nonfixed","MONETARY")] = nonfixed_dummy_solution

      if mode == "TIME":
        dummy_solution = dummyhelper( "TIME"
                                    , demand_tmpD
                                    , demandAddress_tmpD
                                    , probs_tmpD
                                    , inventory_tmpD                                    
                                    , timeMatrix
                                    , ProductWeight
                                    )
        cross_validation[("dummy","TIME")] = dummy_solution

        nonfixed_dummy_solution = nonfixeddummyinventoryhelper( "TIME"
                                                              , demand_tmpD
                                                              , demandAddress_tmpD
                                                              , probs_tmpD
                                                              , inventory_tmpD
                                                              , timeMatrix
                                                              , ProductWeight
                                                              )
        cross_validation[("nonfixed","TIME")] = nonfixed_dummy_solution




      print("-------------------------------"+ mode +" METRICS------------------------------\n")
      print 'Printing metrics for ' + n_itemIter
      weight_av_demand = 0
      for key in demand_tmpD:
              weight_av_demand += probs_tmpD[key[0]]*demand_tmpD[key]
      
#       collecting information for dummy model if there is a solution        
      if dummy_solution['dummyObj'] != 'error - no solution':       
              weight_av_demand_met = weight_av_demand - dummy_solution['weightedDummyDemand']
              
              #AXR 18/23/7: identifying number of disasters completely served
              dummyFlowFiltered = {k:v for k,v in dummy_solution['dummyFlow'].iteritems() if 'dummy' in k}
              WeightedFractionCompletelyServed = 1 - float(len(dummyFlowFiltered))/float(len(probs_tmpD))

              average_time = dummy_solution['adjdummyObj'] / weight_av_demand_met
      elif dummy_solution['dummyObj'] == 'error - no solution':
              print 'dummy model: ' + dummy_solution['dummyObj']
              
#       collecting information for non-fixed dummy model if there is a solution            
      if nonfixed_dummy_solution['dummyObj'] != 'error - no solution':
              weight_av_demand_met_nonfixed = weight_av_demand - nonfixed_dummy_solution['weightedDummyDemand']
              
              #AXR 18/23/7: identifying number of disasters completely served
              dummyFlowFilterednonFixed = {k:v for k,v in nonfixed_dummy_solution['dummyFlow'].iteritems() if 'dummy' in k}
              WeightedFractionCompletelyServednonFixed = 1 - float(len(dummyFlowFilterednonFixed))/float(len(probs_tmpD))

              average_timenonFixed = nonfixed_dummy_solution['adjdummyObj'] / weight_av_demand_met_nonfixed                       
      elif nonfixed_dummy_solution['dummyObj'] == 'error - no solution':
              print 'non-fixed dummy model: ' + nonfixed_dummy_solution['dummyObj']
              
#       calculating balance metric if both models solved        
      if nonfixed_dummy_solution['dummyObj'] != 'error - no solution' and nonfixed_dummy_solution['dummyObj'] != 'error - no solution':
              balance_metric = dummy_solution['adjdummyObj'] / float(nonfixed_dummy_solution['adjdummyObj'])
      else:
              balance_metric = 'n/a'

#       just printing the results            
      print("\nTotal Response "+mode+" for current inventory: " + str(dummy_solution['adjdummyObj']))
      print("Total Response "+mode+" for optimal inventory: " + str(nonfixed_dummy_solution['adjdummyObj']))

      print("Balance Metric: " + str(balance_metric))
      
      print("\nWeighted Av. Demand: " + str(weight_av_demand))        
      print("Weighted Av. Demand Met with current inventory: " + str(weight_av_demand_met))
      print("Weighted Av. Demand Met with optimal inventory: " + str(weight_av_demand_met_nonfixed))
      
      print("\n\nFraction Demand Served with current inventory: " + str(weight_av_demand_met / weight_av_demand))
      print("Fraction Demand Served with optimal inventory: " + str(weight_av_demand_met_nonfixed / weight_av_demand))
      
      print("\n\nWeighted Fraction Completely Served with current inventory: " + str(WeightedFractionCompletelyServed))
      print("Weighted Fraction Completely Served with optimal inventory: " + str(WeightedFractionCompletelyServednonFixed))

      print("\n\nAverage "+mode+" with current inventory: " + str(average_time))
      print("Average "+mode+" with optimal inventory: " + str(average_timenonFixed))
      
      print("dummy correction factor (1-delta)*bigMdummy: " + str((1-WeightedFractionCompletelyServed) * bigMCostDummy))
      print("\n\n")
      

      #Calculate adjusted duals from raw duals. Output to CSV
      #Dummy Depot
      dummyDepotDuals = dummy_solution['depotDuals']
      data = {'Depot City':[], 'Dual':[], 'Adjusted Dual':[]}
      for depotName in dummyDepotDuals:
          if depotName != "dummy":
              if dummyDepotDuals[depotName] > 0.001:
                  data['Depot City'].append(depotName)
                  data['Dual'].append(dummyDepotDuals[depotName])
                  data['Adjusted Dual'].append(dummyDepotDuals[depotName] - (1-WeightedFractionCompletelyServed) * bigMCostDummy)
              else:
                  data['Depot City'].append(depotName)
                  data['Dual'].append(dummyDepotDuals[depotName])
                  data['Adjusted Dual'].append(dummyDepotDuals[depotName])

      DualsDF = pd.DataFrame(data)
      DualsDF.to_csv(output_folder+ "\\"+mode+"_dummy_depot_duals_" + n_itemIter + ".csv", header=True, index=False, columns=['Depot City', 'Dual', 'Adjusted Dual'])   

      #Dummy Carrier
      dummyCarrierDuals = dummy_solution['carrierDuals']
      data = {'Carrier':[], 'Dual':[], 'Adjusted Dual':[]}
      for carrierName in dummyCarrierDuals:
          if carrierName != "dummycarrier":
              if dummyCarrierDuals[carrierName] > 0.001:
                  data['Carrier'].append(carrierName)
                  data['Dual'].append(dummyCarrierDuals[carrierName])
                  data['Adjusted Dual'].append(dummyCarrierDuals[carrierName] - (1-WeightedFractionCompletelyServed) * bigMCostDummy)
              else:
                  data['Carrier'].append(carrierName)
                  data['Dual'].append(dummyCarrierDuals[carrierName])
                  data['Adjusted Dual'].append(dummyCarrierDuals[carrierName])
      DualsDF = pd.DataFrame(data)
      DualsDF.to_csv(output_folder+"\\"+mode+"_dummy_carrier_duals_" + n_itemIter + ".csv", header=True, index=False, columns=['Carrier', 'Dual', 'Adjusted Dual'])  

      #Nonfixed Carrier (nonfixed case does not have a depot dual)
      nonfixedCarrierDuals = nonfixed_dummy_solution['carrierDuals']
      for carrierName in nonfixedCarrierDuals:
          if carrierName != "dummycarrier":
              if nonfixedCarrierDuals[carrierName] > 0.001:
                  data['Carrier'].append(carrierName)
                  data['Dual'].append(nonfixedCarrierDuals[carrierName])
                  data['Adjusted Dual'].append(nonfixedCarrierDuals[carrierName] - (1-WeightedFractionCompletelyServed) * bigMCostDummy)
              else:
                  data['Carrier'].append(carrierName)
                  data['Dual'].append(nonfixedCarrierDuals[carrierName])
                  data['Adjusted Dual'].append(nonfixedCarrierDuals[carrierName])                              
      DualsDF = pd.DataFrame(data)
      DualsDF.to_csv(output_folder+"\\"+mode+"_nonfixeddummy_carrier_duals_" + n_itemIter + ".csv", header=True, index=False, columns=['Carrier', 'Dual', 'Adjusted Dual'])  



    
    monetary_dummy_time = 0
    monetary_nonfixed_time = 0
    time_dummy_monetary = 0
    time_nonfixed_monetary = 0

    weight_av_demand_met = 0
    for quadVar in cross_validation[("dummy", "TIME")]["dummyFlow"]:
      if "dummy" not in quadVar:
        weight_av_demand_met += cross_validation[("dummy", "TIME")]["dummyFlow"][quadVar] * 1.0 / len(probs_tmpD)
        time_dummy_monetary += cross_validation[("dummy", "TIME")]["dummyFlow"][quadVar] * cross_validation[("dummy", "MONETARY")]["weightMap"][quadVar]
    print("Monetary average for time-dummy model: " + str(time_dummy_monetary / weight_av_demand_met))

    weight_av_demand_met = 0
    for quadVar in cross_validation[("nonfixed", "TIME")]["dummyFlow"]:
      if "dummy" not in quadVar:
        weight_av_demand_met += cross_validation[("nonfixed", "TIME")]["dummyFlow"][quadVar] * 1.0 / len(probs_tmpD)
        time_nonfixed_monetary += cross_validation[("nonfixed", "TIME")]["dummyFlow"][quadVar] * cross_validation[("nonfixed", "MONETARY")]["weightMap"][quadVar]
    print("Monetary average for time-nonfixed model: " + str(time_nonfixed_monetary / weight_av_demand_met))

    weight_av_demand_met = 0
    for quadVar in cross_validation[("dummy", "MONETARY")]["dummyFlow"]:
      if "dummy" not in quadVar:
        weight_av_demand_met += cross_validation[("dummy", "MONETARY")]["dummyFlow"][quadVar] * 1.0 / len(probs_tmpD)
        monetary_dummy_time += cross_validation[("dummy", "MONETARY")]["dummyFlow"][quadVar] * cross_validation[("dummy", "TIME")]["weightMap"][quadVar]
    print("Time average for monetary-dummy model: " + str(monetary_dummy_time / weight_av_demand_met))

    weight_av_demand_met = 0
    for quadVar in cross_validation[("nonfixed", "MONETARY")]["dummyFlow"]:
      if "dummy" not in quadVar:
        weight_av_demand_met += cross_validation[("nonfixed", "MONETARY")]["dummyFlow"][quadVar] * 1.0 / len(probs_tmpD)
        monetary_nonfixed_time += cross_validation[("nonfixed", "MONETARY")]["dummyFlow"][quadVar] * cross_validation[("nonfixed", "TIME")]["weightMap"][quadVar]
    print("Time average for monetary-nonfixed model: " + str(monetary_nonfixed_time / weight_av_demand_met))

    sys.stdout = old_stdout
    log_file.close()
    print("-------------------------------END------------------------------")
    return None


def dummyhelper( costType
              , demand_tmpD
              , demandAddress_tmpD
              , probs_tmpD
              , inventory_tmpD
              , costD
              , ProductWeight
                ):
    print("\n\n-------------------------------"+ costType+" DUMMY------------------------------")

    m = Model('StochLP')
    m.setParam('OutputFlag', 0)

    #Generate list of string names
    disasterList = demand_tmpD.keys()
    carrierList = []
    constrs = {}
    
    #Adjust carrier capacity based on item
    itemCarrierConversion = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + conversionRatesFileName)
    for index, row in itemCarrierConversion.iterrows():
        if row.Item == n_itemIter:
            itemCarrierConversionRatio = int(row.ConversionRate)
    
    #CarrierDict is a mapping from Depot City Name to a list of (Carrier name, adjusted capacity, fixed time, variable cost) quadruplets
    carrierDict = {}
    carrier_DataFrame = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + carrierDataFileName)
    for index, row in carrier_DataFrame.iterrows():
        if row["Target Depot City"] not in carrierDict:
              carrierDict[row["Target Depot City"]] = []
        carrierDict[row["Target Depot City"]].append((row.Contract, int(row.Capacity)*itemCarrierConversionRatio, int(row["Fixed Time to Warehouse"]), float(row["Variable Cost (mile)"]))) #FLOAT?


    #Initialize triVars, each variable is a DEPOT:CARRIERNAME:DISASTERID trio
    #Initialize CARRIER constraints explicitly rather than using an upper bound in order to extract duals
    #Perhaps check if the relevant tri has already been added?
    triVars = {}
    for depot in carrierDict:
        depotCarriers = carrierDict[depot]
        for carrier in depotCarriers:
              for disasterTuple in disasterList:
                    disasterName = disasterTuple[0]
                    triName = depot+":"+carrier[0]+":"+disasterName
                    triVars[triName] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=triName) 
                    LHS = LinExpr()
                    LHS.addConstant(carrier[1]) #Adjusted capacity
                    RHS = LinExpr()
                    RHS.addTerms(1,triVars[triName])
                    constrs["CARRIER<"+triName+">"] = m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="CARRIER<"+triName+">")


    
    #Initialize quadVars, each variable is a DEPOT:CARRIERNAME:DISASTERID:SUBLOCATIONID quadruplet
    #Create a mapping from each triVar to its corresponding quad sublocations
    quadVars = {}
    triToQuads = {}
    for depot in carrierDict:
        depotCarriers = carrierDict[depot]
        for carrier in depotCarriers:
                for disaster in disasterList:
                    if (depot, demandAddress_tmpD[disaster]) in costD:
                                    triName = depot+":"+carrier[0]+":"+disaster[0]
                                    quadName = depot+":"+carrier[0]+":"+disaster[0]+":"+disaster[1]
                                    var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=quadName) 
                                    quadVars[quadName] = var
                                    if triName not in triToQuads:
                                            triToQuads[triName] = []
                                    triToQuads[triName].append(var)
        m.update()


    #Introducing a fake dummy node across all variables
    #1000000 Capacity for dummy carrier, 0 fixed time, 1 variable cost
    carrierDict["dummy"] = [("dummycarrier",1000000,0,1)]
    for disasterName in disasterList: #triVar
            triVars["dummy:dummycarrier:"+disasterName[0]] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier:"+disasterName[0]) 
            triToQuads["dummy:dummycarrier:"+disasterName[0]] = []
    dummyTris = []
    for disasterName in disasterList: #qudVars
                    var =  m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier:" + disasterName[0]+":"+disasterName[1]) 
                    quadVars["dummy:dummycarrier:" + disasterName[0]+":"+disasterName[1]] = var
                    triToQuads["dummy:dummycarrier:"+ disasterName[0]].append(var)
                    dummyTris.append(var)
    for disasterID in demandAddress_tmpD:
                    costD[('dummy', demandAddress_tmpD[disasterID])] = bigMCostDummy 
    inventory_tmpD['dummy'] = bigInventoryDummy
    m.update()




    #Minimize expected time
    weightMap = {}
    weights = []
    validVars = []
    for triVar in [quadVars[key] for key in quadVars]:
                    ID = triVar.VarName.split(":")[2]
                    ID2 = triVar.VarName.split(":")[3]
                    depotLoc = triVar.VarName.split(":")[0]
                    for key in carrierDict: #Identify proper element
                            elements = carrierDict[key]
                            for element in elements:
                                            if element[0] == triVar.VarName.split(":")[1]:
                                                if costType == "TIME":
                                                    fixed_cost = element[2]
                                                    break
                                                    break
                                                elif costType == 'MONETARY':
                                                    variable_cost = element[3]
                                                    break
                                                    break
                    if (ID,ID2) in demandAddress_tmpD:
                                    if (depotLoc, demandAddress_tmpD[(ID,ID2)]) in costD:
                                        if costType == "TIME":
                                                    weight = probs_tmpD[ID]*(fixed_cost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)])])
                                                    weightMap[triVar.VarName] = weight
                                                    weights.append(weight) 
                                                    validVars.append(triVar)
                                        elif costType == 'MONETARY':
                                                    weight = probs_tmpD[ID]*(variable_cost * ProductWeight * costD[(depotLoc, demandAddress_tmpD[(ID,ID2)])])
                                                    weightMap[triVar.VarName] = weight
                                                    weights.append(weight) 
                                                    validVars.append(triVar)
    expr = LinExpr()
    expr.addTerms(weights, [quadVars[key] for key in quadVars])
    m.setObjective(expr, GRB.MINIMIZE)

    #Collect infos on distance map for T metric
    #AXR 18/8/8: the distance map now appropriately identifies absolute time (and not expected time)
    triToDistanceMap = {}
    triVarList = [quadVars[key] for key in quadVars]
    for i in range(len(weights)):
            triVar = triVarList[i]
            ID = triVar.VarName.split(":")[2]
            triToDistanceMap[triVarList[i]] = weights[i] / probs_tmpD[ID]

    #Satisfy demand
    for disasterTuple in demand_tmpD:
                    demandQuantity = demand_tmpD[disasterTuple]
                    LHS = LinExpr()
                    LHS.addConstant(demandQuantity)
                    RHS = LinExpr()
                    for depot in carrierDict:
                                    depotCarriers = carrierDict[depot]
                                    for carrier in depotCarriers:
                                                    if depot+":"+carrier[0]+":"+disasterTuple[0]+":"+disasterTuple[1] in quadVars:
                                                                    RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterTuple[0]+":"+disasterTuple[1]])
                    m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterTuple[0]+":"+disasterTuple[1]+">")

    #Flow constraint
    for disasterTuple in demand_tmpD:
        for depot in carrierDict:
            depotCarriers = carrierDict[depot]
            for carrier in depotCarriers:
              LHS = LinExpr()
              LHS.addTerms(1, triVars[depot+":"+carrier[0]+":"+disasterTuple[0]])
              RHS = LinExpr()
              if depot+":"+carrier[0]+":"+disasterTuple[0] in triToQuads:
                      for tri in triToQuads[depot+":"+carrier[0]+":"+disasterTuple[0]]:
                            if str(disasterTuple[0]) == tri.VarName.split(":")[2]:
                                    RHS.addTerms(1, tri)
                                    m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">")

                                                                    
                                                                    
    #Depot capacity
    for disasterTuple in demand_tmpD:
        for depot in carrierDict:
            if depot in inventory_tmpD: #Only consider depots we have inventory in
                depotCarriers = carrierDict[depot]
                inventoryCapacity = inventory_tmpD[depot]
                LHS = LinExpr()
                LHS.addConstant(inventoryCapacity)
                RHS = LinExpr()
                for carrier in depotCarriers:
                     if depot+":"+carrier[0]+":"+disasterTuple[0] in triVars:
                         RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterTuple[0]])
                constrs["DEPOT<"+depot+":"+disasterTuple[0]+">"] = m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+disasterTuple[0]+">")

                    
    #Carrier capacity
    #Nonnegativity
    #These two are taken care of by bounds placed on respective variables
    m.update()
    m.optimize()
    m.write(output_folder+"\\dummy_"+ costType+".lp")
    def printSolution():
        solution_flow = {}
        if m.status == GRB.Status.OPTIMAL:
              print('\nTotal Response Time: %g' % m.objVal)
              print('\nDispatch:')
              assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
              for tri in [quadVars[key] for key in quadVars]:
                      if tri.x > 0.0001:
#                            print(tri.VarName, tri.x)
                            solution_flow[tri.VarName] = tri.x
        else:
              print('No solution')
        return solution_flow




    flow = printSolution()

    if m.status == GRB.Status.OPTIMAL:

            #axr: adjusting objective value for dummy
            dummysum = 0
            if costType == 'TIME':
                for dummykey, dummyvalue in flow.iteritems():    
                    if 'dummy' in dummykey:
                        dummysum = dummysum + dummyvalue * bigMCostDummy * probs_tmpD[next(iter(probs_tmpD))]
            elif costType == 'MONETARY':
                for dummykey, dummyvalue in flow.iteritems():    
                    if 'dummy' in dummykey:
                        dummysum = dummysum + dummyvalue * ProductWeight * bigMCostDummy * probs_tmpD[next(iter(probs_tmpD))]
            adjobjVal = m.objVal - dummysum
            dummyObj = m.objVal
                                            
            weighted_dummy_demand = 0
            for dummyVar in dummyTris:
                            disasterID = dummyVar.VarName.split(':')[2][:9]
                            weighted_dummy_demand += probs_tmpD[disasterID] * dummyVar.x
                                                    


    else:

                                    adjobjVal = 'error - no solution'
                                    dummyObj = 'error - no solution'
                                    weighted_dummy_demand = 0

    #Collect information for T-metric and plot metric over time
    if costType == "TIME":
         timeDemandTuples = []
         total_demand = sum([demand_tmpD[key] for key in demand_tmpD])
         for var in triToDistanceMap:
                  if var.X > .01:
                                  disasterID = var.VarName.split(':')[2]
                                  sublocID = var.VarName.split(':')[3]
                                  #timeDemandTuples.append((var.X * probs_tmpD[disasterID] / float(demand_tmpD[(disasterID, sublocID)]), triToDistanceMap[var]))
                                  #imeDemandTuples.append((var.X * 1.0 / (len(probs_tmpD) * float(demand_tmpD[(disasterID, sublocID)])), triToDistanceMap[var]))
                                  timeDemandTuples.append((var.X / total_demand, triToDistanceMap[var]))
         timeDemandTuples.sort(key = lambda x: x[1]) #Sort based on time
         times = [e[1] for e in timeDemandTuples]
         satisfied = [e[0] for e in timeDemandTuples]
         cumulative_satisfied = []
         for i in range(len(satisfied)):
                  cumulative_satisfied.append(sum(satisfied[:i+1]))
    
         adjustedTimes = [0]
         adjustedSatisfied = [0]
         for i in range(len(cumulative_satisfied)):
                 adjustedTimes.append(times[i])
                 adjustedTimes.append(times[i])
                 if i == 0:
                         adjustedSatisfied.append(0)
                 else:
                         adjustedSatisfied.append(cumulative_satisfied[i-1])
                 adjustedSatisfied.append(cumulative_satisfied[i])
    
         import matplotlib.pyplot as plt
    
         plt.step(adjustedTimes, adjustedSatisfied, label="Current State")
         plt.xlabel('Time (hours)')
         plt.ylabel('Cumulative Fraction of Demand Served')
         plt.xlim(xmin=0, xmax=75)
         plt.ylim(ymin=0, ymax=1)
         plt.title('Demand Served Metric')
         plt.savefig(output_folder+"\\"+ costType +"dummy_T_metric_single.png")
#         plt.close()


    #Generate depot duals by summing over all disasters for a fixed depot
    depotDuals = {}
    carrierDuals = {}
    print("\nDummy Depot Duals: ")
    for depotName in inventory_tmpD:
        depotDuals[depotName] = 0
        for disasterTuple in demand_tmpD:
            constrName = "DEPOT<"+depotName+":"+disasterTuple[0]+">"
            if constrName in constrs:
#              print 'Singular Depot Dual ' + depotName + ":" + disasterTuple[0] + '= ' + str(constrs["DEPOT<"+depotName+":"+disasterTuple[0]+">"].Pi)
              depotDuals[depotName] += constrs[constrName].Pi
    print depotDuals
    
    #Generate carrier duals by summing over all disasters for a fixed carrier
    print("\nDummy Carrier Duals: ")
    for depot in carrierDict:
        for carrier in carrierDict[depot]:
            if carrier[0] not in carrierDuals:
                carrierDuals[carrier[0]] = 0
            for disasterTuple in demand_tmpD:
                if "CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">" in constrs:
                    #print 'Singular Carrier Dual ' + str(depot+":"+carrier[0]+":"+disasterTuple[0]) + "= "  + str(constrs["CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">"].Pi)
                    carrierDuals[carrier[0]] += constrs["CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">"].Pi  
    print carrierDuals



    return {'dummyObj': dummyObj, 'adjdummyObj': adjobjVal, 'dummyFlow': flow, 'weightedDummyDemand': weighted_dummy_demand, 'depotDuals': depotDuals, 'carrierDuals':carrierDuals, 'weightMap':weightMap}


def nonfixeddummyinventoryhelper( costType
                                  , demand_tmpD
                                  , demandAddress_tmpD
                                  , probs_tmpD
                                  , inventory_tmpD
                                  , costD 
                                  , ProductWeight
                                ):
                print("-------------------------------"+costType+" NONFIXED-DUMMY------------------------------")
                m = Model('StochLPNonfixedDummy')
                m.setParam('OutputFlag', 0)

                #Generate list of string names
                disasterList = demand_tmpD.keys()
                carrierList = []
                constrs = {}

                #Adjust carrier capacity based on item
                itemCarrierConversion = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + conversionRatesFileName)
                for index, row in itemCarrierConversion.iterrows():
                    if row.Item == n_itemIter:
                        itemCarrierConversionRatio = int(row.ConversionRate)

                #CarrierDict is a mapping from Depot City Name to a list of (Carrier name, adjusted capacity, fixed time, variable cost) quadruplets
                carrierDict = {}
                carrier_DataFrame = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\" + carrierDataFileName)
                for index, row in carrier_DataFrame.iterrows():
                    if row["Target Depot City"] not in carrierDict:
                          carrierDict[row["Target Depot City"]] = []
                    carrierDict[row["Target Depot City"]].append((row.Contract, int(row.Capacity)*itemCarrierConversionRatio, int(row["Fixed Time to Warehouse"]), float(row["Variable Cost (mile)"]))) #FLOAT?


                #Initialize duo variables
                #AXR: Duo variables are all inventory-carrier pairs
                triVars = {}
                for depot in carrierDict:
                        depotCarriers = carrierDict[depot]
                        for carrier in depotCarriers:
                                for disasterName in disasterList:
                                        disasterName = disasterName[0]
                                        triVars[depot+":"+carrier[0]+":"+disasterName] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+disasterName) 
                                        LHS = LinExpr()
                                        LHS.addConstant(carrier[1])
                                        RHS = LinExpr()
                                        RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterName])
                                        constrs["CARRIER<"+depot+":"+carrier[0]+":"+disasterName+">"] = m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="CARRIER<"+depot+":"+carrier[0]+":"+disasterName+">"+">")


                #Initialize triplet variables
                quadVars = {}
                triToQuads = {}
                for depot in carrierDict:
                        depotCarriers = carrierDict[depot]
                        for carrier in depotCarriers:
                                for disaster in disasterList:
                                        if (depot, demandAddress_tmpD[disaster]) in costD:
                                                var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+":"+disaster[1]) 
                                                quadVars[depot+":"+carrier[0]+":"+disaster[0]+":"+disaster[1]] = var
                                                if depot+":"+carrier[0]+":"+disaster[0] not in triToQuads:
                                                        triToQuads[depot+":"+carrier[0]+":"+disaster[0]] = []
                                                triToQuads[depot+":"+carrier[0]+":"+disaster[0]].append(var)
                                m.update()        

                #Introducing a fake dummy node across all variables
                #1000000 Capacity for dummy carrier, 0 fixed time, 1 variable cost
                carrierDict["dummy"] = [("dummycarrier",1000000,0,1)]
                for disasterName in disasterList: #triVar
                        triVars["dummy:dummycarrier:"+disasterName[0]] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier:"+disasterName[0]) 
                        triToQuads["dummy:dummycarrier:"+disasterName[0]] = []
                dummyTris = []
                for disasterName in disasterList: #qudVars
                                var =  m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="dummy:dummycarrier:" + disasterName[0]+":"+disasterName[1]) 
                                quadVars["dummy:dummycarrier:" + disasterName[0]+":"+disasterName[1]] = var
                                triToQuads["dummy:dummycarrier:"+ disasterName[0]].append(var)
                                dummyTris.append(var)
                for disasterID in demandAddress_tmpD:
                                costD[('dummy', demandAddress_tmpD[disasterID])] = bigMCostDummy 
                inventory_tmpD['dummy'] = bigInventoryDummy
                m.update()

                
                #Minimize expected time
                weightMap = {}
                weights = []
                validVars = []
                for triVar in [quadVars[key] for key in quadVars]:
                                ID = triVar.VarName.split(":")[2]
                                ID2 = triVar.VarName.split(":")[3]
                                depotLoc = triVar.VarName.split(":")[0]
                                for key in carrierDict: #Identify proper element
                                        elements = carrierDict[key]
                                        for element in elements:
                                                        if element[0] == triVar.VarName.split(":")[1]:
                                                            if costType == "TIME":
                                                                fixed_cost = element[2]
                                                                break
                                                                break
                                                            elif costType == 'MONETARY':
                                                                variable_cost = element[3]
                                                                break
                                                                break
                                if (ID,ID2) in demandAddress_tmpD:
                                                if (depotLoc, demandAddress_tmpD[(ID,ID2)]) in costD:
                                                    if costType == "TIME":
                                                                weight = probs_tmpD[ID]*(fixed_cost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)])])
                                                                weightMap[triVar.VarName] = weight
                                                                weights.append(weight) 
                                                                validVars.append(triVar)
                                                    elif costType == 'MONETARY':
                                                                weight = probs_tmpD[ID]*(variable_cost * ProductWeight * costD[(depotLoc, demandAddress_tmpD[(ID,ID2)])])
                                                                weightMap[triVar.VarName] = weight
                                                                weights.append(weight) 
                                                                validVars.append(triVar)
                expr = LinExpr()
                expr.addTerms(weights, [quadVars[key] for key in quadVars])
                m.setObjective(expr, GRB.MINIMIZE)

                #Collect infos on distance map for T metric
                #AXR 18/8/8: the distance map now appropriately identifies absolute time (and not expected time)
                triToDistanceMap = {}
                triVarList = [quadVars[key] for key in quadVars]
                for i in range(len(weights)):
                        triVar = triVarList[i]
                        ID = triVar.VarName.split(":")[2]
                        triToDistanceMap[triVarList[i]] = weights[i] / probs_tmpD[ID]

                #Satisfy demand
                for disasterTuple in demand_tmpD:
                        demandQuantity = demand_tmpD[disasterTuple]
                        LHS = LinExpr()
                        LHS.addConstant(demandQuantity)
                        RHS = LinExpr()
                        for depot in carrierDict:
                                depotCarriers = carrierDict[depot]
                                for carrier in depotCarriers:
                                         if depot+":"+carrier[0]+":"+disasterTuple[0]+":"+disasterTuple[1] in quadVars:
                                                RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterTuple[0]+":"+disasterTuple[1]])
                        m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterTuple[0]+":"+disasterTuple[1]+">")

                #Flow constraint
                for disasterTuple in demand_tmpD:
                        for depot in carrierDict:
                                depotCarriers = carrierDict[depot]
                                for carrier in depotCarriers:
                                        LHS = LinExpr()
                                        LHS.addTerms(1, triVars[depot+":"+carrier[0]+":"+disasterTuple[0]])
                                        RHS = LinExpr()
                                        if depot+":"+carrier[0]+":"+disasterTuple[0] in triToQuads:
                                                for tri in triToQuads[depot+":"+carrier[0]+":"+disasterTuple[0]]:
                                                        if str(disasterTuple[0]) == tri.VarName.split(":")[2]:
                                                                RHS.addTerms(1, tri)
                                                                m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">")




                totalCapacity = 0
                for depotName in inventory_tmpD: #Cycle through all depots to find entire inventory corrected for dummy inventory
                                if depotName != 'dummy':
                                                                totalCapacity += inventory_tmpD[depotName]
                
                #assigning all depots except dummy to depotVars and adding it to the LHS. Then setting right hand side of each constraint to entire inventory
                depotVars = {}
                for depotName in inventory_tmpD:
                        if depotName != 'dummy':
                                depotVars[depotName] = m.addVar(lb=0.0, ub=totalCapacity, vtype=GRB.CONTINUOUS, name=depotName+":NONFIXEDCAPACITY")
                LHS = LinExpr()
                for depot in depotVars:
                        inventoryCapacity = depotVars[depot]
                        LHS.addTerms(1.0, inventoryCapacity)                
                RHS = LinExpr()
                RHS.addConstant(totalCapacity)
                m.addConstr(RHS, GRB.EQUAL, LHS, name="TOTALINVENTORY<>")
                
                #now assiging the dummy to depotVars and creating another constraint with dummy inventory level
                for depotName in carrierDict:
                        if depotName == 'dummy':
                                depotVars[depotName] = m.addVar(lb=0.0, ub=bigInventoryDummy, vtype=GRB.CONTINUOUS, name=depotName+":NONFIXEDCAPACITY")
                LHS = LinExpr()
                for depot in depotVars:
                        if depot == 'dummy':
                                inventoryCapacity = depotVars[depot]
                                LHS.addTerms(1.0, inventoryCapacity)
                RHS = LinExpr()
                RHS.addConstant(bigInventoryDummy)
                m.addConstr(RHS, GRB.EQUAL, LHS, name="TOTALINVENTORYDummy<>")


                for disasterTuple in demand_tmpD:
                        for depot in carrierDict:
                                depotCarriers = carrierDict[depot]
                                inventoryCapacity = depotVars[depot]
                                LHS = LinExpr()
                                LHS.addTerms(1.0, inventoryCapacity)
                                RHS = LinExpr()
                                for carrier in depotCarriers:
                                        if depot+":"+carrier[0]+":"+disasterTuple[0] in triVars:
                                                RHS.addTerms(1,triVars[depot+":"+carrier[0]+":"+disasterTuple[0]])
                                m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+disasterTuple[0]+">")



                m.update()
                m.optimize()
                m.write(output_folder+"\\nonfixeddummy_"+ costType+".lp")

                def printSolution():
                    solution_flow = {}
                    if m.status == GRB.Status.OPTIMAL:
                          print('\nTotal Response Time: %g' % m.objVal)
                          print('\nDispatch:')
                          assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
                          for tri in [quadVars[key] for key in quadVars]:
                                  if tri.x > 0.0001:
#                                        print(tri.VarName, tri.x)
                                        solution_flow[tri.VarName] = tri.x
                    else:
                          print('No solution')
                    return solution_flow
                
                flow = printSolution()
                
                
                                
                
                if m.status == GRB.Status.OPTIMAL:
                    dummysum = 0
                    if costType == 'TIME':
                        for dummykey, dummyvalue in flow.iteritems():    
                            if 'dummy' in dummykey:
                                dummysum = dummysum + dummyvalue * bigMCostDummy * probs_tmpD[next(iter(probs_tmpD))]
                    elif costType == 'MONETARY':
                        for dummykey, dummyvalue in flow.iteritems():    
                            if 'dummy' in dummykey:
                                dummysum = dummysum + dummyvalue * ProductWeight * bigMCostDummy * probs_tmpD[next(iter(probs_tmpD))]
#                    for dummykey, dummyvalue in flow.iteritems():    
#                                                    if 'dummy' in dummykey:
#                                                                                    dummysum = dummysum + dummyvalue * ProductWeight * bigMCostDummy * probs_tmpD[next(iter(probs_tmpD))]
                    adjobjVal = m.objVal - dummysum
                    dummyObj = m.objVal
                    weighted_dummy_demand = 0                                
                    for dummyVar in dummyTris:
                                    disasterID = dummyVar.VarName.split(':')[2][:9]
                                    weighted_dummy_demand += probs_tmpD[disasterID] * dummyVar.x


                    

                    print('\nOptimal Inventory Allocation:')
                    for depot, value in depotVars.iteritems():
                                                    if depot != 'dummy':
                                                                                    print(depot + ": " + str(depotVars[depot].X))
                                                                
                                                                

                else:
                    adjobjVal = 'error - no solution'
                    dummyObj = 'error - no solution'
                    weighted_dummy_demand = 0
                                                
                #Collect information for T-metric and plot metric over time                 

                if costType == "TIME":
                     timeDemandTuples = []
                     total_demand = sum([demand_tmpD[key] for key in demand_tmpD])
                     for var in triToDistanceMap:
                              if var.X > .01:
                                              disasterID = var.VarName.split(':')[2]
                                              sublocID = var.VarName.split(':')[3]
                                              #timeDemandTuples.append((var.X * probs_tmpD[disasterID] / float(demand_tmpD[(disasterID, sublocID)]), triToDistanceMap[var]))
                                              #imeDemandTuples.append((var.X * 1.0 / (len(probs_tmpD) * float(demand_tmpD[(disasterID, sublocID)])), triToDistanceMap[var]))
                                              timeDemandTuples.append((var.X / total_demand, triToDistanceMap[var]))
                     timeDemandTuples.sort(key = lambda x: x[1]) #Sort based on time
                     times = [e[1] for e in timeDemandTuples]
                     satisfied = [e[0] for e in timeDemandTuples]
                     cumulative_satisfied = []
                     for i in range(len(satisfied)):
                              cumulative_satisfied.append(sum(satisfied[:i+1]))
                
                     adjustedTimes = [0]
                     adjustedSatisfied = [0]
                     for i in range(len(cumulative_satisfied)):
                             adjustedTimes.append(times[i])
                             adjustedTimes.append(times[i])
                             if i == 0:
                                     adjustedSatisfied.append(0)
                             else:
                                     adjustedSatisfied.append(cumulative_satisfied[i-1])
                             adjustedSatisfied.append(cumulative_satisfied[i])
                
                     import matplotlib.pyplot as plt
                
                     plt.step(adjustedTimes, adjustedSatisfied, label="Sys. Optimum")
                     plt.xlabel('Time (hours)')
                     plt.ylabel('Cumulative Fraction of Demand Served')
                     plt.xlim(xmin=0, xmax=75)
                     plt.ylim(ymin=0, ymax=1)
                     plt.title('Demand Served Metric')
                     plt.legend()
                     plt.savefig(output_folder+"\\" + costType +"_T_metric.png")
                     plt.close()


                #Generate carrier duals by summing over all disasters for a fixed carrier
                carrierDuals = {}
                for depot in carrierDict:
                   for carrier in carrierDict[depot]:
                       if carrier[0] not in carrierDuals:
                           carrierDuals[carrier[0]] = 0
                       for disasterTuple in demand_tmpD:
                           if "CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">" in constrs:
                              #print 'Singular Carrier Dual ' + str(depot+":"+carrier[0]+":"+disasterTuple[0]) + "= "  + str(constrs["CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">"].Pi)
                               carrierDuals[carrier[0]] += constrs["CARRIER<"+depot+":"+carrier[0]+":"+disasterTuple[0]+">"].Pi
                print("\nNonfixed Dummy Carrier Duals: ")               
                print(carrierDuals)


                return {'dummyObj': dummyObj, 'adjdummyObj': adjobjVal, 'dummyFlow': flow, 'weightedDummyDemand': weighted_dummy_demand, 'carrierDuals':carrierDuals, 'weightMap':weightMap}
optimize()