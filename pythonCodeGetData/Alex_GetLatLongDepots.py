# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 11:36:48 2018

@author: Alex Rothkopf
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
indent = '       '
myMasterFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
myOutputFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData03_US/"
depotWhichToUseReadInvFileName = 'warehouseCitiesAlex.csv'
depotOutputFileNameLongLat = 'depotLatLong.csv'
depottoIncludeFileName = 'depotsWhichToInclude.csv'
inventoryLevelsFileName = 'depotInventoryData.csv'
depotsWhichtoMapToFileName ='depotsWhichToMapTo.csv'
countryResponseCapactiy = 'countryAbilityToRespond.csv'
AcquireDepotLongLat = 0 #set to 1 if you want to acquire long lat of deptos, otherwise 0
WriteNewInventoryLevels = 1 #set to 1 if you want to write new random inventory levels, otherwise 0
WriteNewDepotsWhichtoMapToFile = 0 #set to 1 if you want to write newfile called "depotswhichtomapt", otherwise 0
WriteNewCountryAbilityToRespondFile = 0 #set to 1 if you want to write newfile called "countryabilitytorespond", otherwise 0
#AXR: End of setting variables


invLocationHead = ['gglCountryAscii', 'gglAddressAscii', 'lat', 'lng']
invLocationHeadtoInclude = ['gglCountryAscii', 'gglAddressAscii', 'include', 'FixedInventory']
invLocationHeadOutput = ['Agency','NameCity','gglCountryAscii', 'gglAddressAscii', 'gglLat', 'gglLong','Order']
CommodityListHead =['ItemName','Key']

print str(datetime.now()) + ' -- Reading ASCII inventory locations'
invLocations = pandas.read_csv(myMasterFilePath + depotWhichToUseReadInvFileName , skiprows=[0], names=invLocationHead )
invLocationsOutput = pandas.DataFrame(columns=invLocationHeadOutput)
invLocationsOutputtoInclude = pandas.DataFrame(columns=invLocationHeadtoInclude)

def FindLatLongFct(findCity, findCountry,i):
        findCityCountry = findCity + ", " + findCountry
        time.sleep(0.15)
       #print indent + "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
        url = indent + "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
               
        apiOutput = simplejson.load(urllib.urlopen(url))
        
        if apiOutput['status'] == 'OK':
            gglLat = apiOutput['results'][0]['geometry']['location']['lat']
            gglLong = apiOutput['results'][0]['geometry']['location']['lng']
            print indent * 2 + "Lat " + str(gglLat) + " Long " + str(gglLong) + " (" + str(findCityCountry) + " )"
            #this writes the location infos in the appropriate data frame
            invLocationsOutput.at[i,'Agency'] = 'FEMA'
            invLocationsOutput.at[i,'NameCity'] = findCity.strip()
            invLocationsOutput.at[i,'gglCountryAscii'] = findCountry
            invLocationsOutput.at[i,'gglAddressAscii'] = "".join((str(findCity.strip()),", ",str(findCountry.strip())))
            invLocationsOutput.at[i,'gglLat'] = gglLat
            invLocationsOutput.at[i,'gglLong'] = gglLong
            invLocationsOutput.at[i,'Order'] = i
            invLocationsOutputtoInclude.at[i,'gglCountryAscii'] = findCountry
            invLocationsOutputtoInclude.at[i,'gglAddressAscii'] = "".join((str(findCity.strip()),", ",str(findCountry.strip())))
            invLocationsOutputtoInclude.at[i,'include'] = 1
            #this creates the data frame to write the file that holds the inventory -> the inventory will be addedd manually, though
        else:
            print "Something went wrong acquiring GPS data for " + str(findCityCountry) 

def writeCountryAbilityToRespondFileFct():
    countryList = pandas.read_csv(myOutputFilePath + 'disasterAffectedData.csv', usecols=['gglCountry'])
    countryList.drop_duplicates(subset='gglCountry', inplace=True)
    countryList.reset_index(drop=True, inplace=True)
    countryList.insert(loc=1, column='item', value='DEFAULT')
    countryList.insert(loc=2, column='capacityToRespond', value=10)
    print str(datetime.now()) + ' -- Writing a new csv file: ' + str(countryResponseCapactiy)
    print indent + myOutputFilePath
    countryList.to_csv(myOutputFilePath + countryResponseCapactiy, index=False)
    print str(datetime.now()) + ' ...success!'
#.....
if AcquireDepotLongLat == 1:
    print str(datetime.now()) + ' -- Acquiring GPS data of'
    for i in range(len(invLocations.gglAddressAscii)):
        FindLatLongFct(invLocations.at[i,'gglAddressAscii'],invLocations.at[i,'gglCountryAscii'],i)
        
    print str(datetime.now()) + ' -- Writing GPS location results to csv file: ' + str(depotOutputFileNameLongLat)
    print indent + myOutputFilePath
    invLocationsOutput.to_csv(myOutputFilePath + depotOutputFileNameLongLat, index=False)
    
    print str(datetime.now()) + ' -- Writing locations to include results to csv file: ' + str(depottoIncludeFileName)
    print indent + myOutputFilePath
    invLocationsOutputtoInclude.to_csv(myOutputFilePath + depottoIncludeFileName, index=False)
    
    print str(datetime.now()) + ' ...success!'

if WriteNewInventoryLevels == 1:
    print str(datetime.now()) + ' -- Writing new randomized inventory levels'
    #create a df for the different commodities
    d=['BlanketGen', 'JerryCanGen', 'KitchenSetGen', 'MosquitoNetGen', 'ShelterKit', 'SleepingMats', 'Tarpaulin4x6', 'Tent']
    CommodityList = pandas.DataFrame({'ItemName': d, 'key': [2,2,2,2,2,2,2,2]})
    NumofCommodity = len(CommodityList.ItemName)
    
    invLocationsList = pandas.DataFrame(columns=['Warehouse(Region)', 'gglAddress', 'gglCountry', 'Total','key'])
    invLocationsList['Warehouse(Region)'] = invLocations['gglCountryAscii']    
    invLocationsList['gglAddress'] = invLocations['gglAddressAscii'] + ", " + invLocations['gglCountryAscii']
    invLocationsList['gglCountry'] = invLocations['gglCountryAscii']
    for i in range(len(invLocationsList)):
        invLocationsList.at[i, 'key'] = 2
        invLocationsList.at[i, 'gglAddress']=invLocationsList.at[i, 'gglAddress'].strip()
    NumofDepots = len(invLocationsList.gglAddress)
    #create a df for the inventory levels and fill it by mergeing the commodity list df and the depot df
    invLevelLocationMatrix = pandas.DataFrame(index=numpy.arange(0, NumofCommodity * NumofDepots))
    invLevelLocationMatrix = pandas.merge(CommodityList, invLocationsList, on='key', how='outer')
    invLevelLocationMatrix.drop('key', axis=1, inplace=True)
    UpperInvBoundary = 50000
    for i in range(len(invLevelLocationMatrix)):
        invLevelLocationMatrix.at[i, 'Total'] = random.randint(0,UpperInvBoundary)
            
    print str(datetime.now()) + ' -- Writing random inventory levels to include results to csv file: ' + str(inventoryLevelsFileName)
    print indent + myOutputFilePath
    invLevelLocationMatrix.to_csv(myOutputFilePath + inventoryLevelsFileName, index=False)
    print str(datetime.now()) + ' ...success!'
    
if WriteNewDepotsWhichtoMapToFile == 1:
    print str(datetime.now()) + ' -- Writing a new csv file: ' + str(depotsWhichtoMapToFileName)
    depotsListHeader = ['gglAddressAsciiMapFrom','gglAddressAsciiMapTo']
    depotsList = pandas.DataFrame(columns=depotsListHeader)
    for j in range(len(invLocations)):
        depotsList.at[j,'gglAddressAsciiMapFrom'] = "".join((str(invLocations.at[j,'gglAddressAscii'].strip()),", ",str(invLocations.at[j,'gglCountryAscii'].strip())))
        depotsList.at[j,'gglAddressAsciiMapTo'] = "".join((str(invLocations.at[j,'gglAddressAscii'].strip()),", ",invLocations.at[j,'gglCountryAscii']))
    print indent + myOutputFilePath
    depotsList.to_csv(myOutputFilePath + depotsWhichtoMapToFileName, index=False)
    print str(datetime.now()) + ' ...success!'
    
if WriteNewCountryAbilityToRespondFile == 1:
    writeCountryAbilityToRespondFileFct()
    
#    gglCountry,item,capacityToRespond