import requests
import json
from PIL import Image, ImageDraw, ImageFilter
from os import walk
from numpy import asarray
import glob
import random
import math
import operator
import tkinter as tk
import queue

from requests.models import requote_uri


def returnNonDict(dict_var):
    for k, v in dict_var:
        s = type(v)
        if s == 'dict_items':
            yield returnNonDict(v)
        elif s == 'dict':
            yield returnNonDict(v.items())
        else:
            yield v


def getList(jsRep):  # this looks dumb but it words and is only iterating once in each for loop
    for x in returnNonDict(jsRep.items()):
        for y in returnNonDict(x.items()):
            for z in returnNonDict(y.items()):
                return z


def getMedia(jsonRes):
    ls = getList(jsonRes)
    ls = list(ls[0].values())
    return ls[0]


def getTitleFromMediaDict(dict_media):
    s = list(dict_media.values())[0]  # enter media
    s = list(s.values())[1]  # navigate to title
    s = list(s.values())
    return s[0] if s[1] == None else s[1]


def getRecsDict(dict_media):  # returns dict of reconmendations title:rating
    s = list(dict_media.values())[0]  # enter media
    s = list(s.values())[2]  # navigate to reconmendation object
    s = list(s.values())[0]  # to edges
    recs = dict()
    for node in s:
        inNode = list(node.values())[0]  # inside the node
        rat = list(inNode.values())[0]  # ratings
        title = list(inNode.values())[1]  # titles out
        if not title == None:
            title = list(title.values())[0]  # titles in
            title = list(title.values())[0]
            recs[title] = rat
    return recs


def combineDictionaries(dicts):
    finalDict = dict()
    for d in dicts:
        for k, v in d.items():
            if k in finalDict:
                finalDict[k] = finalDict[k] + v
            else:
                finalDict[k] = v
    return finalDict


def removeWatched(watched, recs):
    for t in watched:
        if t in recs:
            del recs[t]
    return recs


def reconmendationsToReadable(recons):
    ret = ''
    for x in recons:
        k = x[0]
        v = x[1]
        ret = ret + k + ":" + v.__str__() + "\n"
    return ret


def generateGoodReconmendations(media):
    watched = []
    listOfdicts = []

    for ent in media:
        watched.append(getTitleFromMediaDict(ent))
        listOfdicts.append(getRecsDict(ent))

    recs = combineDictionaries(listOfdicts)
    del recs[None]
    recs = removeWatched(watched, recs)
    recs = sorted(recs.items(), key=lambda x: x[1], reverse=True)
    recs = reconmendationsToReadable(recs)
    return recs

    # Here we define our query as a multi-line string
query = '''
query ($name: String) { # Define which variables will be used in the query (id)
  MediaListCollection (userName: $name, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
    lists{
        entries{
            media{
                id
                title{
                    romaji
                    english
                }
                recommendations(sort:RATING_DESC){
                    edges {
                        node {
                            rating
                            mediaRecommendation{
                                title{
                                    english
                                    native
                                }
                            }
                        }
                    }
                }
            }
        }
    }
  }
}
'''


print("type your anilist id:")
input = input().__str__()

# Define our query variables and values that will be used in the query request
variables = {
    'name': input
}

# anilist public api url
url = 'https://graphql.anilist.co'

# Make the HTTP Api request
response = requests.post(url, json={'query': query, 'variables': variables})
js = response.json()

# gets media elements from your anilist
media = getMedia(js)

# combines and simplifies reconmendations
recs = generateGoodReconmendations(media)

# read the line below and guess what it does
print(recs)

# prints reconmendations to a file
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(recs.__str__())
