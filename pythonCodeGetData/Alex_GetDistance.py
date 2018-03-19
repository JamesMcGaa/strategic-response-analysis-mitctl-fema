# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 16:29:45 2018

@author: Alexander Rotkopf (AXR)
"""

import csv
import pandas
import urllib
import simplejson
import random
import time
import numpy
from datetime import datetime

#AXR: Set variables
indent = '       '                     #AXR: This is just to have a nice output
myDropBoxFilePath = "C:/Users/alr06kc/Dropbox (MIT)/" #AXR: Change this path if code runs on a different machine
myMasterFilePath = myDropBoxFilePath + "Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
myOutputFilePath = myDropBoxFilePath + "Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData03_US/"
depotFileName = 'depotLatLong.csv' #AXR: raw data source for depot GPS data
disasterFileName = 'DisasterLatLong.csv' #AXR: raw data source for disaster GPS data
outputFileName = 'drivingDistanceMatrix.csv'
retrieveDistances = 1 #set to 1 if you want to retrieve new Distances, otherwise 0
#AXR: End of setting variables

#AXR: Todos 
#- make the header format fit the structure of Jason's code

def GetDistanceFct(f_origLat, f_origLong, f_destLat, f_destLong,i):
  time.sleep(0.11)
  #url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(f_origGglAddress),str(f_destGglAddress))
  url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={0},{1}&destinations={2},{3}&key=AIzaSyA_bce5AkKxudxufw_BZXHVbMbCfbnPEj0".format(str(f_origLat), str(f_origLong), str(f_destLat), str(f_destLong))
  apiOutput = simplejson.load(urllib.urlopen(url))
  
  if apiOutput['rows'][0]['elements'][0]['status'] == 'OK':
    drivingTime_hrs = apiOutput['rows'][0]['elements'][0]['duration']['value'] / 3600
    distance_km = apiOutput['rows'][0]['elements'][0]['distance']['value'] / 1000
  elif apiOutput['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
    drivingTime_hrs = 1e6
    distance_km = 1e6
  DistanceMatrix.at[i,'distance_km'] = distance_km
  DistanceMatrix.at[i,'drivingTime_hrs'] = drivingTime_hrs
  if i % 25 == 0:
      print indent + '... completed ' + str(i) + '/' + str(len(DistanceMatrix)) + ' queries.'

#---------
print str(datetime.now()) + ' -- Reading GPS source data and generating distance matrix'
disLocationHead = ['disasterGglCountryAscii','disasterGglAddressAscii','disasterGglLat','disasterGglLong']
disLocations = pandas.read_csv(myOutputFilePath + disasterFileName, header=0, names=disLocationHead)
disLocations.insert(loc=4,column='key', value=2)
NumofDisasters = len(disLocations)

invLocationsHead = ['Agency','NameCity','depotGglCountryAscii','depotGglAddressAscii','depotGglLat','depotGglLong','Order']
invLocations = pandas.read_csv(myOutputFilePath + depotFileName, header=0, names=invLocationsHead)
invLocations.insert(loc=7,column='key',value=2)
NumofDepots = len(invLocations)

#DistanceHeader = ['DepotCountry', 'DepotLocation', 'StartLat', 'StartLng', 'DisasterCountry', 'DisasterLocation', 'EndLat', 'EndLng', 'DriveDistance_m', 'DriveTime_s' ]
DistanceMatrix = pandas.DataFrame(index=numpy.arange(0, NumofDisasters * NumofDepots))
DistanceMatrix = pandas.merge(invLocations, disLocations, on='key', how='outer')
DistanceMatrix.drop('key', axis=1, inplace=True)

print str(datetime.now()) + ' -- Retrieving distance (km) and driving time (h)'
if retrieveDistances == 1:
    for i in range(len(DistanceMatrix)):
        GetDistanceFct(DistanceMatrix.at[i,'depotGglLat'],DistanceMatrix.at[i,'depotGglLong'],DistanceMatrix.at[i,'disasterGglLat'],DistanceMatrix.at[i,'disasterGglLong'],i)

print str(datetime.now()) + ' -- Writing results to csv file: ' + outputFileName
print indent + 'path: ' + myOutputFilePath
DistanceMatrix.to_csv(myOutputFilePath + outputFileName, index=False)
print str(datetime.now()) + ' -- done!'

#Agency,NameCity,depotGglCountryAscii,depotGglAddressAscii,depotGglLat,depotGglLong,Order,disasterGglCountryAscii,disasterGglAddressAscii,disasterGglLat,disasterGglLong,drivingTime_hrs,distance_km