#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#TOP----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
                n_itemIter = "Cots"
                print("-------------------------------Start------------------------------")
                import pandas as pd                
                import os

                import sys
                old_stdout = sys.stdout
                log_file = open("outputData//"+ n_itemIter+str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_")+"output_"+n_itemIter+".log","w")
                sys.stdout = log_file

                #Generate cost matrices
                monetaryMatrix = {}
                timeMatrix = {}
                matrix = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\drivingDistanceMatrix.csv") 
                for index, row in matrix.iterrows():
                  monetaryMatrix[((row.depotGglAddressAscii, row.disasterGglAddressAscii))] = row.distance_km
                  timeMatrix[((row.depotGglAddressAscii, row.disasterGglAddressAscii))] = row.drivingTime_hrs

                #Generate demand_tmpD, probs_tmpD, demandAddress_tmpD
                conversion_factor = 0
                beta_conversion_file = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\betaItemConversionsFEMA.csv") 
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
                disasters = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\disasterAffectedDataFEMA.csv") 

                for index, row in disasters.iterrows():
                  if (row.Day, row.Month, row.Year) not in disaster_to_ID_count: #New date
                    disaster_to_ID_count[(row.Day, row.Month, row.Year)] = (current_disaster, 1)

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
                    ID = disaster_to_ID_count[(row.Day, row.Month, row.Year)][0]
                    count = disaster_to_ID_count[(row.Day, row.Month, row.Year)][1]
                    disaster_to_ID_count[(row.Day, row.Month, row.Year)] = (ID, count+1)

                    disasterString = "0" * (4 - len(str(ID // 10000))) + str(ID // 10000)
                    disasterString += "-"
                    disasterString += "0" * (4 - len(str(ID % 10000))) + str(ID % 10000)
                    sublocationString = 'SubLoc_' + "0" * (5-len(str(count))) + str(count)

                    demand_tmpD[(disasterString, sublocationString)] = int(row.TotAffected / conversion_factor)
                    demandAddress_tmpD[(disasterString, sublocationString)] = row.gglAddress

                    disaster_to_count[disasterString] += 1

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

                  for sublocationID in range(disaster_to_count[disasterString]):
                    indexPair = (depotName, "disasterWeightedAverage"+str(ID))
                    adjusted_time_matrix[indexPair] /= total_demand
                    adjusted_cost_matrix[indexPair] /= total_demand

                  adjusted_demand_tmpD[(disasterString, 'SubLoc_00000')] = total_demand
                  adjusted_demandAddress_tmpD[(disasterString, 'SubLoc_00000')] = "disasterWeightedAverage"+str(ID)
                  adjusted_probs_tmpD[disasterString] = 1.0 / current_disaster

                demand_tmpD = adjusted_demand_tmpD
                demandAddress_tmpD = adjusted_demandAddress_tmpD
                probs_tmpD = adjusted_probs_tmpD
                monetaryMatrix = adjusted_cost_matrix
                timeMatrix = adjusted_time_matrix


                #Test 1
                # demand_tmpD = {
                # ('0000-0000', 'SubLoc_00000'): 930000,
                # ('0000-0001', 'SubLoc_00000'): 80000,
                # ('0000-0002', 'SubLoc_00000'): 50000,}
                # probs_tmpD = {'0000-0000':.33333, '0000-0001':.33333, '0000-0002':.33333,}
                # demandAddress_tmpD = {
                # ('0000-0000', 'SubLoc_00000'): "DisasterCity0", 
                # ('0000-0001', 'SubLoc_00000'): "DisasterCity1", 
                # ('0000-0002', 'SubLoc_00000'): "DisasterCity2",}
                # timeMatrix = {
                # ('San Francisco, California', 'DisasterCity0'):10, 
                # ('Dallas, Texas', 'DisasterCity0'):50, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity0'):1,
                # ('San Francisco, California', 'DisasterCity1'):10, 
                # ('Dallas, Texas', 'DisasterCity1'):50, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity1'):1,
                # ('San Francisco, California', 'DisasterCity2'):70, 
                # ('Dallas, Texas', 'DisasterCity2'):1, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity2'):70,}
                # monetaryMatrix = {
                # ('San Francisco, California', 'DisasterCity0'):10, 
                # ('Dallas, Texas', 'DisasterCity0'):50, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity0'):1,
                # ('San Francisco, California', 'DisasterCity1'):10, 
                # ('Dallas, Texas', 'DisasterCity1'):50, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity1'):1,
                # ('San Francisco, California', 'DisasterCity2'):70, 
                # ('Dallas, Texas', 'DisasterCity2'):1, 
                # ("Philadelphia, Pennsylvania", 'DisasterCity2'):70,}
                # inventory_tmpD = {
                # 'Dallas, Texas': 700000, 
                # 'San Francisco, California': 80000, 
                # 'Philadelphia, Pennsylvania': 150000}

                #Test 2
                # demand_tmpD = {
                # ('0000-0000', 'SubLoc_00000'): 940,
                # ('0000-0001', 'SubLoc_00000'): 80,
                # ('0000-0002', 'SubLoc_00000'): 50,}
                # probs_tmpD = {'0000-0000':.33333, '0000-0001':.333333, '0000-0002':.33333,}
                # demandAddress_tmpD = {
                # ('0000-0000', 'SubLoc_00000'): "DisasterCity0", 
                # ('0000-0001', 'SubLoc_00000'): "DisasterCity1", 
                # ('0000-0002', 'SubLoc_00000'): "DisasterCity2",}
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

                #Test 3   
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

                              
                matrix2 = pd.read_csv(os.getcwd()+"\\inputData\\inputData03_US\\itemAttributesFEMA.csv") 
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
                                                , disasterIDsUnq_tmp
                                                , disasterIDsWithSubLocUnq_tmp
                                                , inventory_tmpD
                                                , transModesTransParams
                                                , bigMCostElim
                                                , bigMCostDummy
                                                , monetaryMatrix
                                                , dummyNodeName
                                                , areInitialSuppliesVariables_Flag
                                                , depotWhichFixedSubset
                                                , minInvItemD
                                                , depotInWhichCountry
                                                , ProductWeight
                                                )
                    cross_validation[("dummy","MONETARY")] = dummy_solution

                    nonfixed_dummy_solution = nonfixeddummyinventoryhelper( "MONETARY"
                                                                          , demand_tmpD
                                                                          , demandAddress_tmpD
                                                                          , probs_tmpD
                                                                          , disasterIDsUnq_tmp
                                                                          , disasterIDsWithSubLocUnq_tmp
                                                                          , inventory_tmpD
                                                                          , transModesTransParams
                                                                          , bigMCostElim
                                                                          , bigMCostDummy
                                                                          , monetaryMatrix
                                                                          , dummyNodeName
                                                                          , areInitialSuppliesVariables_Flag
                                                                          , depotWhichFixedSubset
                                                                          , minInvItemD
                                                                          , depotInWhichCountry
                                                                          , ProductWeight
                                                                          )
                    cross_validation[("nonfixed","MONETARY")] = nonfixed_dummy_solution

                  if mode == "TIME":
                    dummy_solution = dummyhelper( "TIME"
                                                , demand_tmpD
                                                , demandAddress_tmpD
                                                , probs_tmpD
                                                , disasterIDsUnq_tmp
                                                , disasterIDsWithSubLocUnq_tmp
                                                , inventory_tmpD
                                                , transModesTransParams
                                                , bigMCostElim
                                                , bigMCostDummy
                                                , timeMatrix
                                                , dummyNodeName
                                                , areInitialSuppliesVariables_Flag
                                                , depotWhichFixedSubset
                                                , minInvItemD
                                                , depotInWhichCountry
                                                , ProductWeight
                                                )
                    cross_validation[("dummy","TIME")] = dummy_solution

                    nonfixed_dummy_solution = nonfixeddummyinventoryhelper( "TIME"
                                                                          , demand_tmpD
                                                                          , demandAddress_tmpD
                                                                          , probs_tmpD
                                                                          , disasterIDsUnq_tmp
                                                                          , disasterIDsWithSubLocUnq_tmp
                                                                          , inventory_tmpD
                                                                          , transModesTransParams
                                                                          , bigMCostElim
                                                                          , bigMCostDummy
                                                                          , timeMatrix
                                                                          , dummyNodeName
                                                                          , areInitialSuppliesVariables_Flag
                                                                          , depotWhichFixedSubset
                                                                          , minInvItemD
                                                                          , depotInWhichCountry
                                                                          , ProductWeight
                                                                          )
                    cross_validation[("nonfixed","TIME")] = nonfixed_dummy_solution




                  print("-------------------------------"+ mode +" METRICS------------------------------\n")
                  print 'Printing metrics for ' + n_itemIter
  #        print dummy_solution
  #        print ""
  #        print nonfixed_dummy_solution
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
                  DualsFileName =  str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_") + "_"+mode+"_dummy_depot_duals_" + n_itemIter + ".csv"
                  DualsDF.to_csv("outputData//"+n_itemIter+DualsFileName, header=True, index=False, columns=['Depot City', 'Dual', 'Adjusted Dual'])   

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
                  DualsFileName =  str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_") + "_"+mode+"_dummy_carrier_duals_" + n_itemIter + ".csv"
                  DualsDF.to_csv("outputData//"+n_itemIter+DualsFileName, header=True, index=False, columns=['Carrier', 'Dual', 'Adjusted Dual'])  

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
                  DualsFileName =  str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_") + "_"+mode+"_nonfixeddummy_carrier_duals_" + n_itemIter + ".csv"
#                  DualsDF.to_csv("outputData//"+n_itemIter+DualsFileName, header=True, index=False, columns=['Carrier', 'Dual', 'Adjusted Dual'])  



                
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
                                                                                                                                #Optimal inv distribution if moving inventory is  allowed
                                                                                                                                , 'myOptInvNoDum': {'Dallas, Texas': 839996.0, 'Atlanta, Georgia': 4400055.2, 'San Francisco, California': 256021.6, 'Philadelphia, Pennsylvania': 24680549.2} 
                                                                                                                                , 'dualTotInv': 0.0
                                                                                                                }

                return myOutDict

#----------------------------------------------------------------------------------------------------------------------------------

def dummyhelper( costType
              , demand_tmpD
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
              , ProductWeight
                                                                                                                                                                    ):
    print("\n\n-------------------------------"+ costType+" DUMMY------------------------------")

    m = Model('StochLP')

    #Generate list of string names
    disasterList = demand_tmpD.keys()
    carrierList = []
    constrs = {}
    

    #Create a mapping from depot city names to (contractor, capacity, cost) triplets
    #Populate carrierList
    #Convert number trucks to capacity
    itemCarrierConversionParse0 = f_myReadCsv(inputPath + itemCarrierConversionFileName)
    itemCarrierConversionParse = itemCarrierConversionParse0[1]
    for row in itemCarrierConversionParse:
        if row[0] == n_itemIter:
            itemCarrierConversionRatio = int(row[1])
    
    #CarrierDict is a mapping from Depot City Name to a list of (Carrier name, adjusted capacity, fixed time, variable cost) quadruplets
    carrierDict = {}
    carrierParse = f_myReadCsv(inputPath + carrierListFileName)
    carrierDataParse = carrierParse[1]
    for row in carrierDataParse:
        if row[5] not in carrierDict:
              carrierDict[row[5]] = []
        carrierDict[row[5]].append((row[0], int(row[1])*itemCarrierConversionRatio, int(row[2]), float(row[4]))) #FLOAT?

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
    m.write("dummy_"+ costType+".lp")
    def printSolution():
        solution_flow = {}
        if m.status == GRB.Status.OPTIMAL:
              print('\nTotal Response Time: %g' % m.objVal)
              #print('\nDispatch:')
              assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
              for tri in [quadVars[key] for key in quadVars]:
                      if tri.x > 0.0001:
                            #print(tri.VarName, tri.x)
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
    # if costType == "TIME":
    #      timeDemandTuples = []
    #      total_demand = sum([demand_tmpD[key] for key in demand_tmpD])
    #      for var in triToDistanceMap:
    #               if var.X > .01:
    #                               disasterID = var.VarName.split(':')[2]
    #                               sublocID = var.VarName.split(':')[3]
    #                               #timeDemandTuples.append((var.X * probs_tmpD[disasterID] / float(demand_tmpD[(disasterID, sublocID)]), triToDistanceMap[var]))
    #                               #imeDemandTuples.append((var.X * 1.0 / (len(probs_tmpD) * float(demand_tmpD[(disasterID, sublocID)])), triToDistanceMap[var]))
    #                               timeDemandTuples.append((var.X / total_demand, triToDistanceMap[var]))
    #      timeDemandTuples.sort(key = lambda x: x[1]) #Sort based on time
    #      times = [e[1] for e in timeDemandTuples]
    #      satisfied = [e[0] for e in timeDemandTuples]
    #      cumulative_satisfied = []
    #      for i in range(len(satisfied)):
    #               cumulative_satisfied.append(sum(satisfied[:i+1]))
    
    #      adjustedTimes = [0]
    #      adjustedSatisfied = [0]
    #      for i in range(len(cumulative_satisfied)):
    #              adjustedTimes.append(times[i])
    #              adjustedTimes.append(times[i])
    #              if i == 0:
    #                      adjustedSatisfied.append(0)
    #              else:
    #                      adjustedSatisfied.append(cumulative_satisfied[i-1])
    #              adjustedSatisfied.append(cumulative_satisfied[i])
    
    #      import matplotlib.pyplot as plt
    
    #      plt.step(adjustedTimes, adjustedSatisfied)
    #      plt.xlabel('Time (hours)')
    #      plt.ylabel('Cumulative Fraction of Demand Served')
    #      plt.xlim(xmin=0, xmax=200)
    #      plt.title('Demand Served Metric')
    #      plt.savefig("outputData//" + str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_") + costType +"dummy_T_metric.png")

    #Generate depot duals by summing over all disasters for a fixed depot
    depotDuals = {}
    carrierDuals = {}
    print("\nDummy Depot Duals: ")
    for depotName in inventory_tmpD:
        depotDuals[depotName] = 0
        for disasterTuple in demand_tmpD:
            constrName = "DEPOT<"+depotName+":"+disasterTuple[0]+">"
            if constrName in constrs:
              #print 'Singular Depot Dual ' + depotName + ":" + disasterTuple[0] + '= ' + str(constrs["DEPOT<"+depotName+":"+disasterTuple[0]+">"].Pi)
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
                                  , ProductWeight
                                          ):
                print("-------------------------------"+costType+" NONFIXED-DUMMY------------------------------")
                m = Model('StochLPNonfixedDummy')
                #Generate list of string names
                disasterList = demand_tmpD.keys()
                carrierList = []
                constrs = {}

                #Convert number trucks to capacity
                itemCarrierConversionParse0 = f_myReadCsv(inputPath + itemCarrierConversionFileName)
                itemCarrierConversionParse = itemCarrierConversionParse0[1]
                for row in itemCarrierConversionParse:
                    if row[0] == n_itemIter:
                          itemCarrierConversionRatio = int(row[1])
                
                #Map of depot to list of [(carrierID, adjusted capacity, fixed time, variable cost),...] 
                carrierDict = {}
                carrierParse = f_myReadCsv(inputPath + carrierListFileName)
                carrierDataParse = carrierParse[1]
                for row in carrierDataParse:
                    if row[5] not in carrierDict:
                        carrierDict[row[5]] = []
                    carrierDict[row[5]].append((row[0], int(row[1])*itemCarrierConversionRatio, int(row[2]), float(row[4]))) #FLOAT?
                
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
                m.write("nonfixeddummy_"+ costType+".lp")

                def printSolution():
                    solution_flow = {}
                    if m.status == GRB.Status.OPTIMAL:
                          print('\nTotal Response Time: %g' % m.objVal)
                          #print('\nDispatch:')
                          assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
                          for tri in [quadVars[key] for key in quadVars]:
                                  if tri.x > 0.0001:
                                        #print(tri.VarName, tri.x)
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
                # if costType == "TIME":
                #      timeDemandTuples = []
                #      total_demand = sum([demand_tmpD[key] for key in demand_tmpD])
                #      for var in triToDistanceMap:
                #               if var.X > .01:
                #                               disasterID = var.VarName.split(':')[2]
                #                               sublocID = var.VarName.split(':')[3]
                #                               #timeDemandTuples.append((var.X * probs_tmpD[disasterID] / float(demand_tmpD[(disasterID, sublocID)]), triToDistanceMap[var]))
                #                               #imeDemandTuples.append((var.X * 1.0 / (len(probs_tmpD) * float(demand_tmpD[(disasterID, sublocID)])), triToDistanceMap[var]))
                #                               timeDemandTuples.append((var.X / total_demand, triToDistanceMap[var]))
                #      timeDemandTuples.sort(key = lambda x: x[1]) #Sort based on time
                #      times = [e[1] for e in timeDemandTuples]
                #      satisfied = [e[0] for e in timeDemandTuples]
                #      cumulative_satisfied = []
                #      for i in range(len(satisfied)):
                #               cumulative_satisfied.append(sum(satisfied[:i+1]))
                
                #      adjustedTimes = [0]
                #      adjustedSatisfied = [0]
                #      for i in range(len(cumulative_satisfied)):
                #              adjustedTimes.append(times[i])
                #              adjustedTimes.append(times[i])
                #              if i == 0:
                #                      adjustedSatisfied.append(0)
                #              else:
                #                      adjustedSatisfied.append(cumulative_satisfied[i-1])
                #              adjustedSatisfied.append(cumulative_satisfied[i])
                
                #      import matplotlib.pyplot as plt
                
                #      plt.step(adjustedTimes, adjustedSatisfied)
                #      plt.xlabel('Time (hours)')
                #      plt.ylabel('Cumulative Fraction of Demand Served')
                #      plt.xlim(xmin=0, xmax=200)
                #      plt.title('Demand Served Metric')
                #      plt.savefig("outputData//" + str(datetime.now()).replace(":", "_").replace(".","_").replace(" ","_") + costType +"dummy_T_metric.png")

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









#----------------------------------------------------------------------------------------------------------------------------------



 # m = Model('StochLP')

                # #Generate list of string names
                # disasterList = demand_tmpD.keys()
                # carrierList = []

                # #Populate carrierList
                # #Convert number trucks to capacity *I pick from file conversion rate and multiple number of trucks by conversion rate which yields carrier capacity
                # itemCarrierConversionParse0 = f_myReadCsv(inputPath + itemCarrierConversionFileName)
                # itemCarrierConversionParse = itemCarrierConversionParse0[1]
                # for row in itemCarrierConversionParse:
                #     if row[0] == n_itemIter:
                #         itemCarrierConversionRatio = int(row[1])
                
                # carrierDict = {}
                # carrierParse = f_myReadCsv(inputPath + carrierListFileName)
                # carrierDataParse = carrierParse[1]
                # for row in carrierDataParse:
                #   if row[5] not in carrierDict:
                #     carrierDict[row[5]] = []
                #   carrierDict[row[5]].append((row[0], int(row[1])*itemCarrierConversionRatio, int(row[2])))

                # #------axr code ends-----


                # #Initialize duo variables
                # carrierConstrs = []
                # triVars = {}
                # for depot in carrierDict:
                #   depotCarriers = carrierDict[depot]
                #   for carrier in depotCarriers:
                #     key = depot+":"+carrier[0]
                #     triVars[key] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]) 
                #     LHS = LinExpr()
                #     LHS.addConstant(carrier[1])
                #     RHS = LinExpr()
                #     RHS.addTerms(1,triVars[key])
                #     carrierConstrs.append(m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="CARRIERCAPACITY<"+key+">"))


                # #Initialize triplet variables
                # quadVars = {}
                # triToQuads = {}
                # for depot in carrierDict:
                #   depotCarriers = carrierDict[depot]
                #   for carrier in depotCarriers:
                #     triToQuads[depot+":"+carrier[0]] = []
                #     for disaster in disasterList:
                #       if (depot, demandAddress_tmpD[disaster], 'Truck') in costD:
                #         var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+disaster[1]) 
                #         quadVars[depot+":"+carrier[0]+":"+disaster[0]+disaster[1]] = var
                #         triToQuads[depot+":"+carrier[0]].append(var)
                # m.update()

                
                # #Minimize expected time
                # weights = []
                # for triVar in [quadVars[key] for key in quadVars]:
                #   ID = triVar.VarName.split(":")[2].split("SubLoc")[0]
                #   ID2 = "SubLoc" + triVar.VarName.split(":")[2].split("SubLoc")[1]
                #   depotLoc = triVar.VarName.split(":")[0]
                #   for key in carrierDict: #Identify proper element
                #     elements = carrierDict[key]
                #     for element in elements:
                #       if element[0] == triVar.VarName.split(":")[1]:
                #         extraCost = element[2]
                #         break
                #         break
                #   if (ID,ID2) in demandAddress_tmpD:
                #     if (depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck") in costD:
                #       total_cost = (extraCost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck")])
                #       weights.append(probs_tmpD[ID]*total_cost) #Check order preservation?
                # expr = LinExpr()
                # expr.addTerms(weights, [quadVars[key] for key in quadVars]) 
                # m.setObjective(expr, GRB.MINIMIZE)

                # triToDistanceMap = {}
                # triVarList = [quadVars[key] for key in quadVars]
                # for i in range(len(weights)):
                #   triToDistanceMap[triVarList[i]] = weights[i]


                # #Satisfy demand
                # demandConstrs = []
                # for disasterTuple in demand_tmpD:
                #   disasterString = disasterTuple[0]+disasterTuple[1]
                #   demandQuantity = demand_tmpD[disasterTuple]
                #   LHS = LinExpr()
                #   LHS.addConstant(demandQuantity)
                #   RHS = LinExpr()
                #   for depot in carrierDict:
                #     depotCarriers = carrierDict[depot]
                #     for carrier in depotCarriers:
                #       if depot+":"+carrier[0]+":"+disasterString in quadVars:
                #         RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterString])
                #   demandConstrs.append(m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterString+">"))



                # #Flow constraint
                # flowConstrs = []
                # for depot in carrierDict:
                #   depotCarriers = carrierDict[depot]
                #   for carrier in depotCarriers:
                #         LHS = LinExpr()
                #         LHS.addTerms(1, triVars[depot+":"+carrier[0]])
                #         RHS = LinExpr()
                #         for tri in triToQuads[depot+":"+carrier[0]]:
                #           RHS.addTerms(1, tri)
                #         flowConstrs.append(m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+">"))



                # #Depot capacity
                # for disasterTuple in demand_tmpD:
                #     disasterString = disasterTuple[0]+disasterTuple[1] 
                #     for depot in carrierDict:
                #         depotCarriers = carrierDict[depot]
                #         inventoryCapacity = inventory_tmpD[depot]
                #         LHS = LinExpr()
                #         LHS.addConstant(inventoryCapacity)
                #         RHS = LinExpr()
                #         for carrier in depotCarriers:
                #              if depot+":"+carrier[0]+":"+disasterString in quadVars:
                #                  RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterString])
                #         m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+carrier[0]+">")


                # m.update()
                # m.optimize()
                # m.write("jamesmodel.lp")

                # def printSolution():
                #   if m.status == GRB.Status.OPTIMAL:
                #       print('\nTotal Response Time: %g' % m.objVal)
                #       print('\nDispatch:')
                #       assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
                #       for tri in [quadVars[key] for key in quadVars]:
                #           if tri.x > 0.0001:
                #             print(tri.VarName, tri.x)
                #   else:
                #       print('No solution')
                
                # flow = printSolution()

                #non-fixed solution without dummy is disabled
                #  nonfixed_solution = nonfixedinventoryhelper(demand_tmpD
                #                                  , demandAddress_tmpD
                #                                  , probs_tmpD
                #                                  , disasterIDsUnq_tmp
                #                                  , disasterIDsWithSubLocUnq_tmp
                #                                  , inventory_tmpD
                #                                  , transModesTransParams
                #                                  , bigMCostElim
                #                                  , bigMCostDummy
                #                                  , costD
                #                                  , dummyNodeName
                #                                  , areInitialSuppliesVariables_Flag
                #                                  , depotWhichFixedSubset
                #                                  , minInvItemD
                #                                  , depotInWhichCountry
                #                                  )



                # def nonfixedinventoryhelper(demand_tmpD
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
                #   import pandas as pd
                #   print("-------------------------------NONFIXED------------------------------")
                #   m = Model('StochLPNonfixed')
                #   #Generate list of string names
                #   disasterList = demand_tmpD.keys()
                #   carrierList = []



                #   #Create a mapping from depot city names to (contractor, capacity, cost) triplets
                #   #------james code start-----
                #   #Populate carrierList
                # #  carrierDict = {}
                # #  carrierParse = f_myReadCsv(inputPath + carrierListFileName)
                # #  carrierDataParse = carrierParse[1]
                # #  for row in carrierDataParse:
                # #    if row[5] not in carrierDict:
                # #      carrierDict[row[5]] = []
                # #    carrierDict[row[5]].append((row[0], int(row[1]), int(row[2])))
                #   #------james code end-----
                #   #------axr code start-----
                #   #Populate carrierList
                #   #Convert number trucks to capacity
                #   itemCarrierConversionParse0 = f_myReadCsv(inputPath + itemCarrierConversionFileName)
                #   itemCarrierConversionParse = itemCarrierConversionParse0[1]
                #   for row in itemCarrierConversionParse:
                #       if row[0] == n_itemIter:
                #           itemCarrierConversionRatio = int(row[1])
                                
                #   carrierDict = {}
                #   carrierParse = f_myReadCsv(inputPath + carrierListFileName)
                #   carrierDataParse = carrierParse[1]
                #   for row in carrierDataParse:
                #     if row[5] not in carrierDict:
                #       carrierDict[row[5]] = []
                #     carrierDict[row[5]].append((row[0], int(row[1])*itemCarrierConversionRatio, int(row[2])))
                #   #------axr code ends-----


                #   #Initialize duo variables
                #   triVars = {}
                #   for depot in carrierDict:
                #     depotCarriers = carrierDict[depot]
                #     for carrier in depotCarriers:
                #       triVars[depot+":"+carrier[0]] = m.addVar(lb=0.0, ub=carrier[1], vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]) 



                #   #Initialize triplet variables
                #   quadVars = {}
                #   triToQuads = {}
                #   for depot in carrierDict:
                #     depotCarriers = carrierDict[depot]
                #     for carrier in depotCarriers:
                #       triToQuads[depot+":"+carrier[0]] = []
                #       for disaster in disasterList:
                #         if (depot, demandAddress_tmpD[disaster], 'Truck') in costD:
                #           var = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=depot+":"+carrier[0]+":"+disaster[0]+disaster[1]) 
                #           quadVars[depot+":"+carrier[0]+":"+disaster[0]+disaster[1]] = var
                #           triToQuads[depot+":"+carrier[0]].append(var)
                #   m.update()

                                
                #   #Minimize expected time
                #   weights = []
                #   for triVar in [quadVars[key] for key in quadVars]:
                #     ID = triVar.VarName.split(":")[2].split("SubLoc")[0]
                #     ID2 = "SubLoc" + triVar.VarName.split(":")[2].split("SubLoc")[1]
                #     depotLoc = triVar.VarName.split(":")[0]
                #     for key in carrierDict: #Identify proper element
                #       elements = carrierDict[key]
                #       for element in elements:
                #         if element[0] == triVar.VarName.split(":")[1]:
                #           extraCost = element[2]
                #           break
                #           break
                #     if (ID,ID2) in demandAddress_tmpD:
                #       if (depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck") in costD:
                #         weights.append(probs_tmpD[ID]*(extraCost + costD[(depotLoc, demandAddress_tmpD[(ID,ID2)],"Truck")])) #Check order preservation?
                #   expr = LinExpr()
                #   expr.addTerms(weights, [quadVars[key] for key in quadVars]) 
                #   m.setObjective(expr, GRB.MINIMIZE)



                #   #Satisfy demand
                #   for disasterTuple in demand_tmpD:
                #     disasterString = disasterTuple[0]+disasterTuple[1]
                #     demandQuantity = demand_tmpD[disasterTuple]
                #     LHS = LinExpr()
                #     LHS.addConstant(demandQuantity)
                #     RHS = LinExpr()
                #     for depot in carrierDict:
                #       depotCarriers = carrierDict[depot]
                #       for carrier in depotCarriers:
                #         if depot+":"+carrier[0]+":"+disasterString in quadVars:
                #           RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterString])
                #     m.addConstr(LHS, GRB.EQUAL, RHS, name="DEMAND<"+disasterString+">")

                #   #Flow constraint
                #   for depot in carrierDict:
                #     depotCarriers = carrierDict[depot]
                #     for carrier in depotCarriers:
                #           LHS = LinExpr()
                #           LHS.addTerms(1, triVars[depot+":"+carrier[0]])
                #           RHS = LinExpr()
                #           for tri in triToQuads[depot+":"+carrier[0]]:
                #             RHS.addTerms(1, tri)
                #           m.addConstr(LHS, GRB.EQUAL, RHS, name="FLOW<"+depot+":"+carrier[0]+">")


                #   #THIS IS THE ONLY MODIFIED SECTION
                #   #Depot capacity
                                
                # #---------------AXR 18/24/7 modification starts
                #   totalCapacity = 0
                #   for depotName in inventory_tmpD: #Cycle through all depots to find entire inventory
                #     totalCapacity += inventory_tmpD[depotName]


                #   depotVars = {}
                #   for depotName in carrierDict:
                #     depotVars[depotName] = m.addVar(lb=0.0, ub=totalCapacity, vtype=GRB.CONTINUOUS, name=depotName+":NONFIXEDCAPACITY") 
                #   LHS = LinExpr()
                #   for depot in depotVars:
                #     inventoryCapacity = depotVars[depot]
                #     LHS.addTerms(1.0, inventoryCapacity)

                                                
                #   RHS = LinExpr()
                #   RHS.addConstant(totalCapacity)
                #   m.addConstr(RHS, GRB.EQUAL, LHS, name="TOTALINVENTORY<>")


                #   for disasterTuple in demand_tmpD:
                #       disasterString = disasterTuple[0]+disasterTuple[1] 
                #       for depot in carrierDict:
                #           depotCarriers = carrierDict[depot]
                #           inventoryCapacity = depotVars[depot]
                #           LHS = LinExpr()
                #           LHS.addTerms(1.0, inventoryCapacity)
                #           RHS = LinExpr()
                #           for carrier in depotCarriers:
                #                if depot+":"+carrier[0]+":"+disasterString in quadVars:
                #                    RHS.addTerms(1,quadVars[depot+":"+carrier[0]+":"+disasterString])
                #           m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depot+":"+carrier[0]+">")
                # #---------------AXR 18/24/7 modification ends
                                                                                                
                # #---------------James code begins------------
                # #  totalCapacity = 0
                # #  for depotName in inventory_tmpD:
                # #    totalCapacity += inventory_tmpD[depotName]
                # #
                # #  depotVars = {}
                # #  for depotName in carrierDict:
                # #    depotVars[depotName] = m.addVar(lb=0.0, ub=totalCapacity, vtype=GRB.CONTINUOUS, name=depotName+":NONFIXEDCAPACITY") 
                # #
                # #  LHS = LinExpr()
                # #  for depot in depotVars:
                # #    inventoryCapacity = depotVars[depot]
                # #    LHS.addTerms(1.0, inventoryCapacity)
                # #  RHS = LinExpr()
                # #  RHS.addConstant(totalCapacity)
                # #  m.addConstr(RHS, GRB.EQUAL, LHS, name="TOTALINVENTORY<>") #Can also use GREATER_EQUAL
                # #
                # #  for depotName in carrierDict:
                # #    depotCarriers = carrierDict[depotName]
                # #    inventoryCapacity = depotVars[depotName]
                # #    LHS = LinExpr()
                # #    LHS.addTerms(1.0, inventoryCapacity)
                # #    RHS = LinExpr()
                # #    for carrier in depotCarriers:
                # #      RHS.addTerms(1,triVars[depotName+":"+carrier[0]])
                # #
                # #    m.addConstr(LHS, GRB.GREATER_EQUAL, RHS, name="DEPOT<"+depotName+":"+carrier[0]+">")
                # #---------------James code ends------------



                #   m.update()
                #   m.optimize()
                #   m.write("jamesmodelnonfixed.lp")

                #   def printSolution():
                #     solution_flow = {}
                #     if m.status == GRB.Status.OPTIMAL:
                #         values = []
                #         print('\nTotal Response Time: %g' % m.objVal)
                #         print('\nDispatch:')
                #         assignments = m.getAttr('x', [quadVars[key] for key in quadVars])
                #         for tri in [quadVars[key] for key in quadVars]:
                #             if tri.x > 0.0001:
                #               print(tri.VarName, tri.x)
                #               solution_flow[tri.VarName] = tri.x
                #         for depotVar in depotVars:
                #           depotVar = depotVars[depotVar]
                #           print(depotVar.VarName, depotVar.x)
                #           values.append([depotVar.VarName.split(":")[0], depotVar.x])
                #         total_inventory = str(sum([e[1] for e in values]))
                #         pd.DataFrame(data=values, columns = ["Depot", ("Allocation (Total Inventory: " + total_inventory + ")")]).to_csv("Nonfixed_Inventory_Assignments.csv", index=False)

                #     else:
                #         print('No solution')
                #     return solution_flow
                                
                #   flow = printSolution()

                #   if m.status == GRB.Status.OPTIMAL:
                #     obj = m.objVal
                #   else:
                #     obj = 'No Solution'


                                
                #   grid = []
                #   if m.status == GRB.Status.OPTIMAL:
                #       for tri in [quadVars[key] for key in quadVars]:
                #             grid.append(tri.VarName.split(":") + [tri.x])
                #       flow = pd.DataFrame(grid, columns = ['Depot City', 'Carrier', 'Disaster Location', 'Allocation'])
                #       flow.to_csv("NonfixedFlow.csv", index=False)

                #   return {'nonfixedObj': obj, 'nonfixedFlow': flow}
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#BOT----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

























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