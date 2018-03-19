# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 12:53:14 2018

@author:Alexander Rothkopf (AXR)
"""
import csv
import pandas
import urllib
import simplejson
import random
import time
from datetime import datetime

#AXR: Set variables
indent = '       '                     #AXR: This is just to have a nice output
myMasterFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
myOutputFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData03_US/"
disastersWhichToUseReadInvFileName = 'disasterAffectedData.csv' #AXR: raw data source 
outputFileName = 'DisasterLatLong.csv'
disasterCountryWhichToUseReadInFileName = 'disasterCountryWhichToInclude.csv'
disasterTypesWhichToUseFileName = 'disasterTypeWhichToUse.csv'
disasterCountryWhichToUseFileName ='disasterCountryWhichToInclude.csv'
gglCountryLookUpFileName = 'gglCountryContinentLkup.csv'
RetrieveDisasterGPSData = 0 # set to 1 if you want to acquire new GPS data for all potential disaster locations, otherwise 0
WriteDisastersToIncludeFile = 0 # set to 1 if you want to write a new file with the disaster locations that are included in the analysis, otherwise 0
WriteDisasterTypesToIncludeFile = 0 # set to 1 if you want to write a new file with the disaster types to include, otherwise 0
WriteDisasterCountriesToIncludeFile = 0 # set to 1 if you want to write a new file with the disaster countries to include, otherwise 0
WritegglCountryContinentLkupFile = 1 # set to 1 if you want to write a new file with the countries and the contintent, otherwise 0
#AXR: End of setting variables

print str(datetime.now()) + ' -- Reading ASCII disaster locations'
#disLocationHead = ['gglCountryAscii', 'gglAddressAscii', 'ggLat', 'gglLong']
disLocations = pandas.read_csv(myOutputFilePath + disastersWhichToUseReadInvFileName, usecols=['gglAddress', 'gglCountry'])
disLocations.rename(columns={'gglAddress':'gglAddressAscii','gglCountry':'gglCountryAscii'},inplace=True)
disLocations.drop_duplicates(subset='gglCountryAscii', inplace=True)
#disLocations.insert(loc=2, column='gglLat', value=0)
#disLocations.insert(loc=3, column='gglLong', value=0)
disLocations.reset_index(drop=True, inplace=True)
#disLocations.apply(pandas.to_numeric, errors='ignore')

#AXR: Subroutine to retrieve GPS data for a disaster 
def FindLatLongFct(findCity, findState,i):
        findCountry = 'United States'
        time.sleep(0.15)
        #ggLat = 0
        #ggLong = 0    
        #print indent + "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
        url = indent + "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
        
        #gglLat = random.randint(1, 10)
        #gglLong = random.randint(1, 10)
        #print indent + "i=" + str(i) + ";" + str(gglLat) + str(gglLong)
        #invLocations.at[i,'lat'] = gglLat
        #invLocations.at[i,'lng'] = gglLong
        
        apiOutput = simplejson.load(urllib.urlopen(url))
        
        if apiOutput['status'] == 'OK':
            gglLat = apiOutput['results'][0]['geometry']['location']['lat']
            gglLong = apiOutput['results'][0]['geometry']['location']['lng']
            print indent * 2 + "Lat " + str(gglLat) + " Long " + str(gglLong) + " (" + str(findCity) + " )"
            disLocations.at[i,'gglLat'] = gglLat
            disLocations.at[i,'gglLong'] = gglLong
        else:
            print "Something went wrong acquiring GPS data for " + str(findCity) 

#AXR: Subroutine to identify all relevant disaster types (eliminate manually 1 in output file to exclude disaster types)            
def FindDisasterTypes():
    disTypes = pandas.read_csv(myOutputFilePath + 'disasterAffectedData.csv', usecols=['Type'])
    disTypes.rename(columns={'Type':'disasterType'},inplace=True)
    disTypes.drop_duplicates(subset='disasterType',inplace=True)
    disTypes.reset_index(drop=True, inplace=True)
    disTypes.insert(loc=1, column='include', value=1)
    print str(datetime.now()) + ' -- Writing results to csv file: ' + disasterTypesWhichToUseFileName
    disTypes.to_csv(myOutputFilePath + disasterTypesWhichToUseFileName, index=False)
    print str(datetime.now()) + '...success!'
    
    
def genCountryListFct():
    print str(datetime.now()) + ' -- Reading ASCII US states'
    stateList = pandas.read_csv(myMasterFilePath + 'USStatesCapitals.csv', usecols=[0], header=None)
    stateList.rename(columns={0:'gglCountry'},inplace=True)
    stateList.insert(loc=1,column='Continent',value='United States')
    stateList.insert(loc=2,column='UseMe',value=1)
    print str(datetime.now()) + ' -- Writing results to csv file: ' + disasterCountryWhichToUseFileName
    stateList.to_csv(myOutputFilePath + disasterCountryWhichToUseFileName, index=False)
    print str(datetime.now()) + '...success!'
    
def genCountryContinentFct():
    print str(datetime.now()) + ' -- Reading ASCII US states'   
    stateList = pandas.read_csv(myMasterFilePath + 'USStatesCapitals.csv', usecols=[0], header=None)
    stateList.rename(columns={0:'gglCountry'},inplace=True)
    stateList.insert(loc=1,column='Continent',value='United States')
    print str(datetime.now()) + ' -- Writing results to csv file: ' + gglCountryLookUpFileName
    stateList.to_csv(myOutputFilePath + gglCountryLookUpFileName, index=False)
    print str(datetime.now()) + '...success!'    
#gglCountry,Continent
    
#------
#AXR: Call function to retrieve GPS data
if RetrieveDisasterGPSData == 1:
    print str(datetime.now()) + ' -- Acquiring GPS data of'
    for i in range(len(disLocations.gglAddressAscii)):
        FindLatLongFct(disLocations.at[i,'gglAddressAscii'],disLocations.at[i,'gglCountryAscii'],i)
        
    print str(datetime.now()) + ' -- Writing results to csv file: '+ str(outputFileName)
    disLocations.to_csv(myOutputFilePath + outputFileName, index=False)
    print str(datetime.now()) + '...success!'
    
#AXR: write a file that includes all relevant distaster locations
if WriteDisastersToIncludeFile == 1:
    disLocationsListHead = ['gglCountry','Continent','UseMe']
    disLocationsList = pandas.read_csv('C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData02_Pacific/disasterCountryWhichToInclude.csv', names=disLocationsListHead)
    for i in range(len(disLocationsList)):
        if disLocationsList.at[i,'gglCountry'] == 'United States':
            disLocationsList.at[i,'UseMe'] = 1
        else:
            disLocationsList.at[i,'UseMe'] = 0
    print str(datetime.now()) + ' -- Writing results to csv file: ' + disasterCountryWhichToUseReadInFileName
    disLocationsList.to_csv(myOutputFilePath + disasterCountryWhichToUseReadInFileName, index=False)
    print str(datetime.now()) + '...success!'
    
#AXR: write a file that includes all relevant disaster types
if WriteDisasterTypesToIncludeFile == 1: 
    FindDisasterTypes()

#AXR: write a file that includes all relevant countries (in my case states)
if WriteDisasterCountriesToIncludeFile == 1:
    genCountryListFct()
 
if WritegglCountryContinentLkupFile == 1:
    genCountryContinentFct()
#gglCountry,Continent