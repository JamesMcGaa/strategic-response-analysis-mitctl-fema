def column(matrix, i):
    return [row[i] for row in matrix]
    
def columnByName(matrix, header, colname):
  headerPos = [i for i in range(len(header)) if header[i] == colname][0]
  return column(matrix, headerPos)  
    

def stripVect(vect):
  outVect = []
  for i in range(len(vect)):
    if type(vect[i]) == type('s'):
      outVect.append(vect[i].strip())
    else:
      outVect.append(vect[i])
  return outVect
  
def stripMat(matrix):
  outMat = []
  for i in range(len(matrix)):
    outMat.append(stripVect(matrix[i]) )
  return outMat    
           
    
    
def createSubMatrixByColAndVectLkup(matrix, header, colname, subsetVect):
  matCol = columnByName(matrix, header, colname)
  s = [i for i in range(len(matCol)) if matCol[i] in subsetVect]
  outMat = [matrix[i] for i in s]
  return outMat
  
  
def changeColType(matrix, header, colname, newType):
  headerPos = [j for j in range(len(header)) if header[j] == colname][0]
  outMat = []
  for i in range(len(matrix)):
    myRow = matrix[i]
    if newType == 'int':
      myRow[headerPos] = deepcopy(int(float(myRow[headerPos])))
    elif newType == 'float':
      myRow[headerPos] = deepcopy(float(myRow[headerPos]))
    elif newType == 'str':
      myRow[headerPos] = deepcopy(str(myRow[headerPos]))
    else:
      raise NameError('You have tried to change a column type in matrix, with an invalid type.')  
    outMat.append(deepcopy(myRow))
  return outMat
    
    
    
def returnValuePossibleDefaults(masterList
                                , lkupMat
                                , lkupHeader
                                , matchVectMasterToLkupTxt
                                , ix_defaultsInMasterTxt
                                , ix_finalNumTxt
                                ):                                  
  matchVectMasterToLkup = [j for i in range(len(matchVectMasterToLkupTxt)) for j in range(len(lkupHeader)) if lkupHeader[j] == matchVectMasterToLkupTxt[i]]                                  
  matchVectMasterToLkup = []
  for i in range(len(matchVectMasterToLkupTxt)):
    ix = [j for j in range(len(lkupHeader)) if lkupHeader[j] == matchVectMasterToLkupTxt[i]]
    if len(ix) > 1: 
      raise NameError('Check function returnValuePossibleDefaults')
    elif len(ix) == 0:
      matchVectMasterToLkup.append(-1)
    else:
      matchVectMasterToLkup.append(ix[0])
  ix_defaultsInMaster = []
  for i in range(len(ix_defaultsInMasterTxt)):
    ix = [j for j in range(len(lkupHeader)) if lkupHeader[j] == ix_defaultsInMasterTxt[i]]
    if len(ix) != 1: 
      print ix
      print lkupHeader
      print ix_defaultsInMasterTxt[i]
      raise NameError('Check function returnValuePossibleDefaults')
    else:
      ix_toWrite = [j for j in range(len(matchVectMasterToLkup)) if matchVectMasterToLkup[j] == ix[0]]
      ix_defaultsInMaster.append(ix_toWrite[0])
  ix_finalNum = [i for i in range(len(lkupHeader)) if lkupHeader[i] == ix_finalNumTxt][0]
  masterListTmp = deepcopy([masterList[i] for i in range(len(masterList)) if matchVectMasterToLkup[i] >= 0])
  for i_iter in range(len(ix_defaultsInMaster) + 1):
    #x = [i for i in range(len(lkupMat)) if masterListTmp == [lkupMat[i][j] for j in matchVectMasterToLkup if j >= 0]]  
    x = [i for i in range(len(lkupMat)) if [str(masterListTmp[i1]) for i1 in range(len(masterListTmp))] == [str(lkupMat[i][j]) for j in matchVectMasterToLkup if j >= 0]]  
    if len(x) > 1:
      raise NameError('When working with defaults, you have more than one value returned!!')
    elif len(x) == 1:
      break
    elif i_iter < len(ix_defaultsInMaster):
      masterListTmp[ix_defaultsInMaster[i_iter]] = 'DEFAULT'
  if len(x) != 1:
    raise NameError('Finding Default Values Failed')
  else:
    return lkupMat[x[0]][ix_finalNum]
    
    
def convertLatLongsToKm(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6378.1
  


def f_extractSubDict(
                    myDict
                    , keyPosToMatchList
                    , textToMatchKeysList
                    ):  
                      
  #myDict = {('a', 'blue'): 5, ('b', 'orange'): 7}
  #keyPosToMatchList = [1]
  #textToMatchKeysList = ['orange']
  myKeys = myDict.keys()
  mySubKeys = []
  for i in range(len(myKeys)):
    myKey1 = list(myKeys[i])
    if [myKey1[j] for j in keyPosToMatchList] == textToMatchKeysList:
      mySubKeys.append(deepcopy(tuple(myKey1)))
  return  {k: myDict[k] for k in tuple(mySubKeys)}




  
def f_keyWithMaxVal(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]  
  
    
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    
    
def f_myReadCsv(f_filePath):
    mycsv = csv.reader(open(f_filePath, "rb"))
    
    myList = list(mycsv)
    myListData = stripMat(myList[1:])
    myListHeader = stripVect(myList[0])
    return([myListHeader, myListData])
    

def f_writeCsv(f_name, f_2DListWithHeader):
    f = open(f_name, 'wb')
    fcsv = csv.writer(f)
    for i in range(len(f_2DListWithHeader)):
        fcsv.writerow(f_2DListWithHeader[i])
    f.close()

    
def f_appendCsv(f_name, f_2DListWithHeader):
    if os.path.isfile(f_name):
      myHeaderRead = f_myReadCsv(f_name)[0]
      myHeaderWrite = f_2DListWithHeader[0]
      if myHeaderRead != myHeaderWrite:
        raise NameError('You are trying to append to a file that has different headers')
      f_2DListToWriteAppend = deepcopy([r for r in f_2DListWithHeader if r != myHeaderRead])
    else:
      f_2DListToWriteAppend = deepcopy(f_2DListWithHeader)
    f = open(f_name, 'ab')
    fcsv = csv.writer(f)
    for i in range(len(f_2DListToWriteAppend)):
        fcsv.writerow(f_2DListToWriteAppend[i])
    f.close()
    
def f_appendOrWriteCsv(f_name, f_2DListWithHeader, writeOrAppendTxt):
  if writeOrAppendTxt == 'writeOver':
    f_writeCsv(f_name, f_2DListWithHeader)
  elif writeOrAppendTxt == 'append':
    f_appendCsv(f_name, f_2DListWithHeader)
  else:
    raise NameError('You do not have a valid write or append value')
    
    
    
def f_addToCsv(f_name, f_2DListWithHeader):
    try:
        open(f_name, 'rb')
        #print 'all good'
    except IOError:
        f = open(f_name, 'wb')
        fcsv = csv.writer(f)
        myHeaderRow = f_2DListWithHeader[0]
        fcsv.writerow(myHeaderRow)
        f.close()
        #print 'uh-oh'
    f = open(f_name, 'ab')
    fcsv = csv.writer(f)
    for i in range(1,len(f_2DListWithHeader)):
        fcsv.writerow(f_2DListWithHeader[i])
    f.close()        
    
    
    
        
def f_reduceCostMatrixToFCSet(f_costsDict, f_newSetOfFCs):
    f_costsDict = costsDict
    f_newSetOfFCs = ['ABE', 'PHX']
    
    f_costsDictNew = {(i, j):f_costsDict[i, j] for (i, j) in f_costsDict if i in f_newSetOfFCs}
    



def f_convertDemandCostsDicstsToArrays(d, c):
    #d = demandProportionsDict
    #c = costsDict
    demandNames = dict.keys(d)
    demandProportionsVect = [0] * len(demandNames)
    for i in range(len(demandNamesProportion)):
        demandProportionsVect[i] = d[demandNames[i]]

    FCNames = list(set(zip(*dict.keys(c))[0]))  
    #print FCNames    
    costsMatrixRead = [[0] * len(FCNames) for i in range(len(demandNames))]   
    for i in range(len(FCNames)):
        for j in range(len(demandNames)):
            costsMatrixRead[j][i] = c[(FCNames[i],demandNames[j])]
    
    return [demandProportionsVect, costsMatrixRead]    






def f_createRandomFCLocations(n):
    myCoords = [0] * n
    seed(10)
    for i in range(n):
        myCoords[i] = [random(), random()]
    return myCoords
    
def f_calcDistancesFromLoc(myCoords):
    myDistances = array(
        [[0. * i for i in range(len(myCoords))] for row in range(len(myCoords))]
        )
    
    for i in range(len(myCoords)):
        #myTempVect = [0] * len(myCoords)
        for j in range(len(myCoords)):
            xDiff = myCoords[i][0] - myCoords[j][0]
            yDiff = myCoords[i][1] - myCoords[j][1]

            myDistances[i][j] = deepcopy(sqrt(xDiff**2 + yDiff**2))

            #myTempVect[j] = sqrt(xDiff**2 + yDiff**2)
        #myDistances[i] = myTempVect
    return myDistances        

def f_calcOverflowRankFromDist(myDistances):
    myTempOverflowRank = array(
        [[0 * i for i in range(len(myDistances[0]))] for row in range(len(myDistances))]
        )
    for i in range(len(myDistances)):
        v = [argsort(argsort(myDistances[i]))[j] for j in range(len(myDistances[0]))]
        for j in range(len(myDistances[0])):
            myTempOverflowRank[i][j] = v[j] #[argsort(argsort(myDistances[i]))[j] for j in range(len(myDistances))]
    return myTempOverflowRank
                




# Changes a myopic "order" into a distance matrix

def f_convertFCOrderToDistance(f_overflowRank \
                                , f_geometricFactor \
                                ):
    # Input: a rank matrix (for each FC, what's the order of overflow considerint myopic?)
    # output: fake distances between FC's
    
    myDistanceMatrix = [[0*i for i in range(len(f_overflowRank[0]))] for row in range(len(f_overflowRank))] 
    for i in range(len(f_overflowRank)):
        for j in range(len(f_overflowRank[0])):
            myVect = deepcopy([ f_geometricFactor**k for k in range( f_overflowRank[i][j] + 1) ])
            if len(myVect) == 0:
                myDistanceMatrix[i][j] = 1.
            else:
                myDistanceMatrix[i][j] = round(sum(myVect), (len(f_overflowRank[0]) + 1))
    
    return myDistanceMatrix



def f_getTransLPHorizon(f_leadTime, f_reviewPeriod):
    return(int(math.ceil((max(f_leadTime) * 1.0 + 0.001) / f_reviewPeriod)*f_reviewPeriod))

        
        
        
        
        

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



def f_getDemandPerFC(d, c):
    whichFCNearest = [0] * len(d)
    for i in range(len(d)):
        whichFCNearest[i] = numpy.nonzero(array(c[i]) == min(array(c[i])))[0][0]

    sumDemandFC = [0] * len(c[0])
    for i in range(len(sumDemandFC)):
        a = numpy.nonzero(array(whichFCNearest) == array(i))[0]
        sumDemandFC[i] = sum(d[a[j]] for j in range(len(a)))
    return  sumDemandFC  
    
    
    
    
    
    
    
    

def f_chooseFC_Myopic(inv, c, dx):
    minCost = min(c[dx][i] for i in range(len(inv)) if inv[i] > 0)
    cheapestFCs = [i for i in range(len(inv)) if c[dx][i] == minCost and inv[i] > 0]
    if len(cheapestFCs) == 0:
        raise NameError('didnt find feasible FC to fulfill from')
    return cheapestFCs[0]




def f_scaleOrderAmountsToEqualLocalBasestock(orderAmts \
                                                , basestockLevels \
                                                , futureInboundInventory \
                                                , inventoryRightNow):
    orderAmountWhatWouldHaveBeen = [0] * len(orderAmts)
    orderAmtOutput = [0] * len(orderAmts)
    systemInventoryPosition = sum(futureInboundInventory) +  sum(inventoryRightNow)
    for i in range(len(orderAmts)):
        orderAmountWhatWouldHaveBeen[i] = deepcopy(min(max(basestockLevels[i] - inventoryRightNow[i] - futureInboundInventory[i], 0) \
                          , max(sum(basestockLevels) -  systemInventoryPosition, 0)))

        systemInventoryPosition = deepcopy(systemInventoryPosition + orderAmountWhatWouldHaveBeen[i])
    #print 'bbbbb' 
    #print orderAmountWhatWouldHaveBeen
        
    myTempTempDDiff =  sum(orderAmountWhatWouldHaveBeen) - sum(orderAmts )
    
    #print myTempTempDDiff
    if myTempTempDDiff < 0:
        myScaleDownParam = deepcopy(sum(orderAmountWhatWouldHaveBeen) * 1. / sum(orderAmts ))
        for i in range(len(orderAmts)):
            orderAmtOutput[i]  = deepcopy(floor(orderAmts[i]  *  myScaleDownParam))
    else:
        orderAmtOutput = deepcopy(orderAmts)
    #print orderAmtOutput
    
    myTempDDiff =  deepcopy(sum(orderAmountWhatWouldHaveBeen) - sum(orderAmtOutput ) )
    #print myTempDDiff
    if myTempDDiff < 0:
        raise NameError('Scaling went wrong')
    
    elif myTempDDiff > 0:
        if sum(orderAmtOutput ) > 0:
            whatToAddToOrder = numpy.random.multinomial( myTempDDiff, [orderAmtOutput[i] / sum(orderAmtOutput) for i in range(len(orderAmts))] )
            #print 'w'
            #print whatToAddToOrder
        else:
            whatToAddToOrder = numpy.random.multinomial( myTempDDiff, [1 / len(orderAmts) for i in range(len(orderAmts))] )
        #print whatToAddToOrder   
        for i in range(len(orderAmts)):
            orderAmtOutput[i] = deepcopy(orderAmtOutput[i]  + whatToAddToOrder[i] )
    
    return orderAmtOutput
    
    
    
def f_printAsCsv(f):
    for i in range(len(f)):
        r = f[i]
        l = str(r[0])
        for j in range(1,len(r)):
            l = l + ',' + str(r[j])
        print l    
    
    
    
    
def f_rearrangeInventory(inv, severity):
    a = list(numpy.random.uniform(0, 1, len(inv)))
    myRandomProbs = [round(a[i] / sum(a), 3) for i in range(len(a))]
    myOldProbs = [round(inv[i] / sum(inv), 3) for i in range(len(inv))]
    myProbs = [myRandomProbs[i] * severity + myOldProbs[i] * (1 - severity) for i in range(len(inv))]
    return numpy.random.multinomial(sum(inv), myProbs)
    
    
    
def f_calcDips(L, d, r):
    dip = [0] * len(L)
    for i in range(len(L)):
        inv = 0
        for j in range(len(L)):
            inv += d[j] * ((L[j] - L[i]) % r)
        dip[i] = inv
    return dip
    
    
def f_calcLOLED(L, d, r, k, sigma):
    dOverL = [d[i] * L[i] for i in range(len(L))]
    #dOverL = [d[i] * (L[i] + r) for i in range(len(L))]
    LWeights = [round(dOverL[i] / sum(dOverL), 3) for i in range(len(L)) ] 
    LTilde = sum([L[i] * LWeights[i] for i in range(len(L))])
    #rPlusLTilde = sum([(r + L[i]) * LWeights[i] for i in range(len(L))])
    return k * sigma * numpy.sqrt(r + LTilde)    
    #return k * sigma * numpy.sqrt(rPlusLTilde)



def f_calcSysSSHeteroL(L, d, r, k, sigma):
    minDip = min(f_calcDips(L, d, r)) 
    LOLED =  f_calcLOLED(L, d, r, k, sigma)
    return LOLED - minDip    
    
def f_spreadSSProporToSigmaOverL(SS, sigmaFC, L, r):
    sigmaOverLPerFC = [numpy.sqrt(L[i]) * sigmaFC[i] for i in range(len(L))]
    #sigmaOverLPerFC = [numpy.sqrt(r + L[i]) * sigmaFC[i] for i in range(len(L))]
    weightsSS = [sigmaOverLPerFC[i] / sum(sigmaOverLPerFC) for i in range(len(L))]
    return [round(weightsSS[i] * SS, 3) for i in range(len(L))]
    
    
    
def f_saveObj(obj, name , path):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def f_loadObj(name, path ):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)    