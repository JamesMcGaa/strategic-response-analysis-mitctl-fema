import csv
import json as simplejson
import urllib
from copy import deepcopy
import unicodedata
import time


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


def f_getLatLong(f_city, f_country):
  time.sleep(0.15)
  f_city.strip()
  f_country.strip()
  f_cityPlus = deepcopy(f_city.replace(' ', '+'))
  f_countryPlus = deepcopy(f_country.replace(' ','+')    )

  if len(f_country) > 0:
    #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&components=country:" + str(f_country) + "&components=locality:" + str(f_city)
    url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_cityPlus) + "," + str(f_countryPlus)
  else:
    #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&components=locality:" + str(f_city)
    #url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_city)
    url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_cityPlus) 
  
  apiOutput = simplejson.load(urllib.urlopen(url))
  # this little test is for Ngerulmud, Palau, which doesn't come back.  Only the country works.
  if apiOutput['status'] == 'ZERO_RESULTS':
    url = "http://maps.googleapis.com/maps/api/geocode/json?language=en-EN&sensor=false&address=" + str(f_countryPlus)
    apiOutput = simplejson.load(urllib.urlopen(url))
  
  if apiOutput['status'] == 'OK':
    gglLat = apiOutput['results'][0]['geometry']['location']['lat']
    gglLong = apiOutput['results'][0]['geometry']['location']['lng']
    gglAddressComponents = apiOutput['results'][0]['address_components']
    typeVect = []
    for i1 in range(len(gglAddressComponents)):
      typeVect.append(gglAddressComponents[i1]['types'])
    ix_countryVect = [i1 for i1 in range(len(typeVect)) if 'country' in typeVect[i1]]
    # This "if" is for cyprus, which doesn't return country name?
    if len(ix_countryVect) > 0:
      ix_country = ix_countryVect[0]
    else:
      ix_country = 0
    gglCountry = unicodedata.normalize('NFKD', apiOutput['results'][0]['address_components'][ix_country]['long_name']).encode('ascii','ignore') 
    #gglCity = apiOutput['results'][0]['address_components'][0]['long_name']
    gglFormattedAddress = unicodedata.normalize('NFKD', apiOutput['results'][0]['formatted_address']).encode('ascii','ignore')
  elif apiOutput['status'] == 'ZERO_RESULTS':
    print 'You just tried to geocode API ' + str(f_city)  + ', ' + str(f_country)
    raise NameError('You Have an incorrect City Country Name')  
  elif apiOutput['status'] == 'OVER_QUERY_LIMIT':
    raise NameError('You are over your google geocode API limit')
  else:
    raise NameError('Unknown Status while Trying to query the Google API Geocoder')
  return [f_city, f_country, gglCountry, gglFormattedAddress, gglLat, gglLong]
    

#-------------------------------------------------------------------------------
    
inputFilePath = 'C:/Users/jaa26/Dropbox/Academic/Papers/Jarrod/MyStuff/DisasterAnalysis2.0/GettingRawData/RawDataFiles/'
emdatCitiesFileName = 'emdatCitiesLookupOutput.csv'

emdatCitiesData = f_myReadCsv(inputFilePath + emdatCitiesFileName)

#emdatCountryNames = column(emdatData[1], [i for i in range(len(emdatData[0])) if emdatData[0][i].strip() == 'Country'][0])  
#emdatCountryNames = [emdatCountryNames[i].strip() for i in range(len(emdatCountryNames))]
#emdatCountryNames = list(set(emdatCountryNames))

#f_writeCsv(inputFilePath + 'emdatCountryNames.csv', emdatCountryNames)


emdatCities = column(emdatCitiesData[1], [i for i in range(len(emdatCitiesData[0])) if emdatCitiesData[0][i].strip() == 'OutputCity'][0])
emdatCountries = column(emdatCitiesData[1], [i for i in range(len(emdatCitiesData[0])) if emdatCitiesData[0][i].strip() == 'OutputLocation'][0])

gglInfo = []

gglInfo.append(['emdatCity', 'emdatCountry', 'gglCountryAscii', 'gglAddressAscii', 'gglLat', 'gglLong'])

for i in range(len(emdatCities)):
  gglInfo.append(deepcopy(f_getLatLong(emdatCities[i], emdatCountries[i])))

  


f_writeCsv(inputFilePath + 'emdatGglLatLong.csv', gglInfo)



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
