import requests
import os

from routing import codeAddress

import operator

def apply_operator(inp, relate, cut):
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq}
    return ops[relate](inp, cut)

def find_nearby_trails(address, bounds, details):
    url = "https://trailapi-trailapi.p.rapidapi.com/trails/explore/"

    coords = codeAddress(address, bounds)
    
    if details is not None and "Distance" in details:
        radius = details["Distance"]
    else:
        radius = "15"

    querystring = {"lat":str(coords[0]), "lon":str(coords[1]), "radius": radius}

    headers = {
        "X-RapidAPI-Key": os.environ["TRAILAPI_KEY"],
        "X-RapidAPI-Host": "trailapi-trailapi.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()

    if details is not None:
        i = 0
        while i < len(response["data"]):
            item_removed = False
            if "Rating" in details:
                operator = "=="
                if len(details["Rating"]) > 1:
                    operator = details["Rating"][1]

                if not apply_operator(float(response["data"][i]["rating"]), operator, float(details["Rating"][0])):
                    response["data"].pop(i)
                    i -= 1
                    item_removed = True

            if not item_removed and "Length" in details:
                operator = "=="
                if len(details["Length"]) > 1:
                    operator = details["Length"][1]

                if not apply_operator(float(response["data"][i]["length"]), operator, float(details["Length"][0])):
                    response["data"].pop(i)
                    i -= 1
                    item_removed = True

            if not item_removed and "Difficulty" in details:
                operator = "=="

                if not apply_operator(response["data"][i]["difficulty"], operator, details["Difficulty"][0]):
                    response["data"].pop(i)
                    i -= 1
                    item_removed = True

            i+=1


    return response

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    find_nearby_trails(43.13555267673683, -77.62851386398442)