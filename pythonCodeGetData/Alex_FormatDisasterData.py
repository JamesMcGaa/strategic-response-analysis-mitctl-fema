# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:13:19 2018

@author: Alexander Rothkopf
"""

import csv
import pandas
import urllib
import simplejson
import random
import time
import numpy
from datetime import datetime
import dateutil

#AXR: Set variables
indent = '       '                     #AXR: This is just to have a nice output
DisasterStartDate = "1990-01-01"       #AXR: The date from which on we consider a disaster to be relevant for our analysis 
DisasterEndDate = "2018-01-01"       #AXR: The date from which on we do not consider a disaster to be relevant for our analysis 
myMasterFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/pythonCodeGetData/"
myOutputFilePath = "C:/Users/alr06kc/Dropbox (MIT)/Humanitarian Response Capacity Stockpile/Alex/04 - Python Strategic Response Analysis/inputData/inputData03_US/"
depotWhichToUseReadInvFileName = '130628RawDataEMDAT.csv' #AXR: raw data source 
stateCapitalReadFileName = 'USStatesCapitals.csv'
SubstituteStateCapital = 1 #AXR: set to 1 if you want to substitute for states captials, otherwise 0
#AXR: End of setting variables

print str(datetime.now()) + ' -- Reading ASCII disaster locations.'
disLocationHead = ['StartDate', 'EndDate', 'Country', 'Location', 'Type', 'SubType', 'Name', 'TotalKilled', 'TotalAffected', 'TotalDamage', 'DisasterID']
disLocations = pandas.read_csv(myMasterFilePath + depotWhichToUseReadInvFileName, names=disLocationHead )
pandas.to_numeric(disLocations.TotalAffected, errors='coerce')


#AXR: Subroutine to cut off any text in the Location field that follows a "," or a "(" and substituting the shortend expression in the location-columnn
def subLocationStrip(OrigLocation,i):
        SubsLocation= OrigLocation.split(",", 1)[0]
        SubsLocation = SubsLocation.split(";", 1)[0]
        SubsLocation = SubsLocation.split("(", 1)[0]
        if OrigLocation != SubsLocation:
            disLocations.at[(i,'Location')] = SubsLocation 
            
def subLocation(findCity,i):
        time.sleep(0.15)
        findCountry = 'United States'
        #print indent + "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
        url = "https://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(findCity) + "," + str(findCountry) + "&key=AIzaSyDXDGr9FneS1SO3MumD3DBGDkf8LP9M5Xc"
               
        apiOutput = simplejson.load(urllib.urlopen(url))
        if apiOutput['status'] == 'OK':
            ShortLoc = len(apiOutput['results'][0]['address_components'])
            print str(ShortLoc) + ' returned outputs for location: ' + str(findCity)
            #AXR: extracting state location information
            for j in range(len(apiOutput['results'][0]['address_components'])):
                if len(apiOutput['results'][0]['address_components'][j]['short_name'].encode('utf-8')) == 2 and apiOutput['results'][0]['address_components'][j]['short_name'].encode('utf-8') != 'US':
                    print indent +'State: ' + apiOutput['results'][0]['address_components'][j]['long_name'].encode('utf-8')
                    StateName = apiOutput['results'][0]['address_components'][j]['long_name'].encode('utf-8')
                    #AXR: identifying correspondign state capital and returning value 
                    #AXR: including error routine for D.C.-region because it does not return state capital
                    #AXR: including error routine for 'from gorgia to New York' to quick-fix
                    #AXR: including error routine for 'Majurok' which is Marshall Islands to quick-fix
                    if StateName == 'District of Columbia':
                        StateCapital = 'Washington D.C.'
                    elif findCity == 'From Georgia to New York ':
                        StateCapital = 'Atlanta'
                    elif findCity == 'Majuro ':
                        StateCapital = 'None'
                    elif findCity == 'Nuku Hiva Island ':
                        StateCapital = 'None'
                    elif findCity == 'Near Kensington ':
                        StateCapital = 'Annapolis'
                    elif StateName == 'United States':
                        StateCapital = 'None'
                    elif findCity == 'Honululu':
                        StateCapital = 'None'
                    elif StateName == 'Marshall Islands':
                        StateCaptial = 'None'
                    elif StateName == 'Frensh Polynesia':
                        StateCapital = 'None'
                    else:
                        df = StateCapitals[StateCapitals['State'].str.match(StateName)]
                        StateCapital = df.iloc[(0,1)]
                    Address = StateCapital + ", " + StateName
                    print indent + 'gglAddress is: ' + Address
                    disLocationsFiltered2.at[(i,'Location')] = Address
                    disLocationsFiltered2.at[(i,'Country')] = StateName
        else:
            print "Something went wrong acquiring GPS data for " + str(findCity) +": " + str(apiOutput['status'])

   
#------
#AXR: Identifying timestamps with "00" for day or month and marking them na in the column
print str(datetime.now()) + ' -- Identifying invalid timestamps.'      
for i in range(len(disLocations)):
    StrEndDate = disLocations.iloc[(i,1)][:2]
    if StrEndDate == '00':
        disLocations.at[(i,'EndDate')] = 'na'

#AXR: Calling the subroutine to eliminate multiple disaster locations
print str(datetime.now()) + ' -- Substituting multiple disaster location for the first.'
for i in range(len(disLocations)):
    subLocationStrip(disLocations.iloc[(i,3)],i)

print str(datetime.now()) + ' -- Filtering irrelevant US disasters (no time stamp, no people affected)'
disLocationsFiltered = disLocations[(disLocations.Country == 'United States ') & (disLocations.EndDate != 'na') & (disLocations.Location != " ") & (disLocations.TotalAffected != 'nan' )]

disLocationsFiltered = disLocationsFiltered[~pandas.isnull(disLocationsFiltered.TotalAffected)]

#AXR: changing EndDate to datetime format and filtering for relevant dates
pandas.options.mode.chained_assignment = None
disLocationsFiltered['EndDate'] = pandas.to_datetime(disLocationsFiltered['EndDate'], errors='coerce', dayfirst=True)

disLocationsFiltered2 = disLocationsFiltered[(disLocationsFiltered.EndDate > DisasterStartDate) & (disLocationsFiltered.EndDate < DisasterEndDate)]
disLocationsFiltered2 = disLocationsFiltered2.reset_index(drop=True)

#AXR: calling subroutine to change disaster location to states' captials
if SubstituteStateCapital == 1:
    print str(datetime.now()) + ' -- Substituting disaster locations for states\' capitels '
    StateCapitals = pandas.read_csv(myMasterFilePath + stateCapitalReadFileName, names=['State','Capital'])
    for i in range(len(disLocationsFiltered2)):
        subLocation(disLocationsFiltered2.iloc[(i,3)],i)

#AXR: eliminate disaster locations with no entry (those are Hawaii, i.e. not continental US)
disLocationsFiltered2 = disLocationsFiltered2[~pandas.isnull(disLocationsFiltered2.Location)]
disLocationsFiltered2 = disLocationsFiltered2[((disLocationsFiltered2.gglCountry != 'United States ') & (disLocationsFiltered2.gglCountry != 'Hawaii') & (disLocationsFiltered2.gglCountry != 'Frensh Polynesia ') & (disLocationsFiltered2.gglCountry != 'Marshall Islands '))]

#AXR: Formatting dataframe to fit the file structure and writing file
#Day,Month,Year,gglAddress,gglCountry,Type   ,Sub Type   ,TotAffected   ,DisasterID
disLocationsFiltered2.drop(['StartDate','Name','TotalKilled','TotalDamage'], axis=1, inplace=True)
disLocationsFiltered2.rename(columns={'Location': 'gglAddress', 'Country': 'gglCountry', 'TotalAffected': 'TotAffected'}, inplace=True)

disLocationsFiltered2.insert(loc=0, column='Day', value=pandas.DatetimeIndex(disLocationsFiltered2['EndDate']).day)
disLocationsFiltered2.insert(loc=1, column='Month', value=pandas.DatetimeIndex(disLocationsFiltered2['EndDate']).month)
disLocationsFiltered2.insert(loc=3, column='Year', value=pandas.DatetimeIndex(disLocationsFiltered2['EndDate']).year)
disLocationsFiltered2.drop(['EndDate'], axis=1, inplace=True)

print str(datetime.now()) + ' -- Writing output file: ' + 'disasterAffectedData.csv'
disLocationsFiltered2.to_csv(myOutputFilePath + 'disasterAffectedData.csv', index=False)


