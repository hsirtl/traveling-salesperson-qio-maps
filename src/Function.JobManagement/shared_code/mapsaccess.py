import requests
import os


def getLatLon(address):
    params = {}
    params['api-version'] = 1.0
    params['subscription-key'] = os.environ["AzureMapsSubscriptionKey"]
    params['query'] = address
    r = requests.get('https://atlas.microsoft.com/search/address/json', params=params)

    r_dict = r.json()
    lat = r_dict.get("results")[0].get("position").get("lat")
    lon = r_dict.get("results")[0].get("position").get("lon")

    return(lat, lon)


def getRoute(latStart, lonStart, latEnd, lonEnd):
    params = {}
    params['api-version'] = 1.0
    params['subscription-key'] = os.environ["AzureMapsSubscriptionKey"]
    params['query'] = "{},{}:{},{}".format(str(latStart), str(lonStart), str(latEnd), str(lonEnd))
    params['report']="effectiveSettings"
    r = requests.get('https://atlas.microsoft.com/route/directions/json', params=params)

    r_dict = r.json()

    return r_dict


def addCoordinates(destinations):
    extDestinations = []
    for destination in destinations:
        (lat, lon) = getLatLon(destination)
        extDestinations.append( { 'address': destination , 'lat': lat, 'lon': lon } )

    return extDestinations


def getCostMatrix(destinations, optCriterion):
    matrix = []
    for startLocation in destinations:
        costRow = []
        for endLocation in destinations:
            route = getRoute(startLocation.get('lat'), startLocation.get('lon'), endLocation.get('lat'), endLocation.get('lon'))
            lengthInMeters = route.get("routes")[0].get("summary").get("lengthInMeters")
            travelTimeInSeconds = route.get("routes")[0].get("summary").get("travelTimeInSeconds")
            if(optCriterion == "travelTimeInSeconds"):
                costRow.append(travelTimeInSeconds)
            elif(optCriterion == "lengthInMeters"):
                costRow.append(lengthInMeters)
        matrix.append(costRow)
    
    return matrix