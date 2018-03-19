import csv
import json as simplejson
import urllib
from copy import deepcopy
import unicodedata
import time
# Google map api
# AIzaSyA_bce5AkKxudxufw_BZXHVbMbCfbnPEj0
def column(matrix, i):
    return [row[i] for row in matrix]

def f_myReadCsv(f_filePath):
    mycsv = csv.reader(open(f_filePath, "rb"))
    
    myList = list(mycsv)
    myListData = myList[1:]
    myListHeader = myList[0]
    return([myListHeader, myListData])

def f_writeCsv1D(f_name, f_2DListWithHeader):
    f = open(f_name, 'wb')
    fcsv = csv.writer(f)
    for i in range(len(f_2DListWithHeader)):
      fcsv.writerow([f_2DListWithHeader[i]])
    f.close()

def f_writeCsv(f_name, f_2DListWithHeader):
    f = open(f_name, 'wb')
    fcsv = csv.writer(f)
    for i in range(len(f_2DListWithHeader)):
      fcsv.writerow(f_2DListWithHeader[i])
    f.close()

def f_appendCsv(f_name, f_vect):
    f = open(f_name, 'ab')
    fcsv = csv.writer(f)
    fcsv.writerow(f_vect)
    f.close()

    
    
def f_getDriveInfo(f_origGglAddress, f_destGglAddress):
  time.sleep(0.11)
  #url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(f_origGglAddress),str(f_destGglAddress))
  url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&avoid=ferries&language=en-EN&sensor=false".format(str(f_origGglAddress),str(f_destGglAddress))
  apiOutput = simplejson.load(urllib.urlopen(url))
  #print apiOutput
  if apiOutput['rows'][0]['elements'][0]['status'] == 'OK':
    drivingTime_hrs = apiOutput['rows'][0]['elements'][0]['duration']['value'] / 3600
    distance_km = apiOutput['rows'][0]['elements'][0]['distance']['value'] / 1000
  elif apiOutput['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
    drivingTime_hrs = 1e6
    distance_km = 1e6
  # Figure out how to fix this.......status exists for overquerylimit but not others
  #elif apiOutput['rows'][0]['elements'][0]['status'] == 'OVER_QUERY_LIMIT':
  #  raise NameError('You ran up against your google api distance limit')
  else:
    print apiOutput['rows'][0]['elements'][0]['status']
    raise NameError('Google distanceMatrix API has status unknown')  
 
  return [drivingTime_hrs, distance_km]
     

def f_getDriveInfoLatLong(f_origLat, f_origLong, f_destLat, f_destLong):
  time.sleep(0.11)
  #url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(f_origGglAddress),str(f_destGglAddress))
  url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={0},{1}&destinations={2},{3}&key=AIzaSyA_bce5AkKxudxufw_BZXHVbMbCfbnPEj0".format(str(f_origLat), str(f_origLong), str(f_destLat), str(f_destLong))
  apiOutput = simplejson.load(urllib.urlopen(url))
  #print apiOutput
  if apiOutput['rows'][0]['elements'][0]['status'] == 'OK':
    drivingTime_hrs = apiOutput['rows'][0]['elements'][0]['duration']['value'] / 3600
    distance_km = apiOutput['rows'][0]['elements'][0]['distance']['value'] / 1000
  elif apiOutput['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
    drivingTime_hrs = 1e6
    distance_km = 1e6
  # Figure out how to fix this.......status exists for overquerylimit but not others
  #elif apiOutput['rows'][0]['elements'][0]['status'] == 'OVER_QUERY_LIMIT':
  #  raise NameError('You ran up against your google api distance limit')
  else:
    print apiOutput['rows'][0]['elements'][0]['status']
    raise NameError('Google distanceMatrix API has status unknown')  
 
  return [drivingTime_hrs, distance_km]
    

#-------------------------------------------------------------------------------
    
inputFilePath = "C:/JasonCDrive/Git/Humanitarian_010/Pacific/inputData/inputData02_Pacific/"
depotGglCitiesFileName = 'depotLatLong.csv'
disasterGglCitiesFileName = 'disasterLatLong.csv'
outputFileName = 'drivingDistanceMatrix_pacific2.csv'

depotData = f_myReadCsv(inputFilePath + depotGglCitiesFileName)
disasterData = f_myReadCsv(inputFilePath + disasterGglCitiesFileName)

depotAddresses = column(depotData[1], [i for i in range(len(depotData[0])) if depotData[0][i].strip() == 'gglAddressAscii'][0])
disasterAddresses = column(disasterData[1], [i for i in range(len(disasterData[0])) if disasterData[0][i].strip() == 'gglAddressAscii'][0])

depotAddressesLat = column(depotData[1], [i for i in range(len(depotData[0])) if depotData[0][i].strip() == 'gglLat'][0])
disasterAddressesLat = column(disasterData[1], [i for i in range(len(disasterData[0])) if disasterData[0][i].strip() == 'gglLat'][0])
depotAddressesLong = column(depotData[1], [i for i in range(len(depotData[0])) if depotData[0][i].strip() == 'gglLong'][0])
disasterAddressesLong = column(disasterData[1], [i for i in range(len(disasterData[0])) if disasterData[0][i].strip() == 'gglLong'][0])
depotAddressesLat = [float(i) for i in depotAddressesLat]  
disasterAddressesLat = [float(i) for i in disasterAddressesLat]
depotAddressesLong = [float(i) for i in depotAddressesLong]
disasterAddressesLong = [float(i) for i in disasterAddressesLong]


gglInfo = []

gglInfo.append( depotData[0] +
                disasterData[0] +
                ['drivingTime_hrs'
                , 'distance_km']
                )

f_writeCsv(inputFilePath + outputFileName, gglInfo)

# Do range(0, 10, 1)  range(11, 20, 1) range(21, 22, 1) range(22, 24) range(24, 35, 1) 
k = 1
for i in range(len(depotAddresses)):
  for j in range(len(disasterAddresses)):
    #print depotAddresses[i]
    [myTime, myDist] =  f_getDriveInfoLatLong(depotAddressesLat[i], depotAddressesLong[i], disasterAddressesLat[j], disasterAddressesLong[j])
    f_appendCsv(inputFilePath + outputFileName, depotData[1][i] + disasterData[1][j] + [myTime] + [myDist])
    if k % 50 == 0:
        print 'doing', k, 'of', len(depotAddresses) * len(disasterAddresses)
    k += 1




if 1 == 2:
    f_country = emdatCountries[100].strip().replace(' ','+')
    f_city = emdatCities[100].strip().replace(' ','+')



    if len(f_country) > 0:
      #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&components=country:" + str(f_country) + "&components=locality:" + str(f_city)
      url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_city) + "," + str(f_country)
    else:
      print 'hello'
      #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&components=locality:" + str(f_city)
      #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_city)
      url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_city) 
      
    apiOutput = simplejson.load(urllib.urlopen(url))

    gglAddressComponents = apiOutput['results'][0]['address_components']
    typeVect = []
    for i1 in range(len(gglAddressComponents)):
      typeVect.append(gglAddressComponents[i1]['types'])
    ix_country = [i1 for i1 in range(len(typeVect)) if 'country' in typeVect[i1]][0]
    print apiOutput

#url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_CityCountry),str(dest_CityCountry))

#result= simplejson.load(urllib.urlopen(url))

#driving_time = result['rows'][0]['elements'][0]['duration']['value']
