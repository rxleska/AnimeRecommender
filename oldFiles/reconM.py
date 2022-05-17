import requests
from os import walk
from numpy import asarray

from requests.models import requote_uri


def returnNonDict(dict_var):
    """
    This function returns the closest non dictionary item in a line of dictionaries\n
    Used to remove excess items in api response\n
    :param dict_var: dictionary item or dictionary object\n
    :return: assorted objected stored in given dictionary
    """
    for k, v in dict_var:
        s = type(v)
        if s == 'dict_items':
            yield returnNonDict(v)
        elif s == 'dict':
            yield returnNonDict(v.items())
        else:
            yield v


def getList(jsonRes):
    """
    This function returns the show lists from the AniList query Response\n
    :param jsRep: json response from anilist query\n
    :return: list object of Media item arrays\n
    """
    return returnNonDict(
        returnNonDict(
            returnNonDict(
                jsonRes.items()
            ).__next__().items()
        ).__next__().items()
    ).__next__()


def getMedia(jsonRes):
    """
    This function returns the watched show list from the AniList query Response\n
    :param jsRep: json response from anilist query\n
    :return: list object of Media items from watched list\n
    """
    ls = getList(jsonRes)
    ls = list(ls[0].values()) + list(ls[1].values())
    print(len(ls))
    return ls[0] + ls[1]


def getTitleFromMediaDict(dict_media):
    """
    Gets Title from Media Item\n
    :param dict_media: Dictionary containing Information on a single show\n
    :returns: Title String\n
    """
    s = list(dict_media.values())[0]  # enter media
    s = list(s.values())[1]  # navigate to title
    s = list(s.values())
    return s[0] if s[1] == None else s[1]


def getRecsDict(dict_media):  # returns dict of reconmendations title:rating
    """
    Gets Reconmendations from Media Item\n
    :param dict_media: Dictionary containing Information on a single show\n
    :returns:  Dictionary of reconmendation in title:rating format\n
    """
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
    """
    Combines Dictionaries\n
    :param dicts: List of Dictionaries to be combined\n
    :return: single dictionary\n
    """
    finalDict = dict()
    for d in dicts:
        for k, v in d.items():
            if k in finalDict:
                finalDict[k] = finalDict[k] + v
            else:
                finalDict[k] = v
    return finalDict


def removeWatched(watched, recs):
    """
    Removed Watched Shows from reconmendation list\n
    :param watched: list of watched titles\n
    :param recs: dictionary of reconmendations\n
    :return: new dictionary of reconmendations
    """
    for t in watched:
        if t in recs:
            del recs[t]
    return recs


def reconmendationsToReadable(recons):
    """
    Converst Reconmendations into a readable format\n
    :param recons: Dictionary of Reconmendations\n
    :return: returns readable string of reconmendations 
    """
    ret = ''
    for x in recons:
        k = x[0]
        v = x[1]
        ret = ret + k + ":" + v.__str__() + "\n"
    return ret


def generateGoodReconmendations(media):
    """
    Gets and Sorts Reconmendations for easiest use\n
    :param media: list of media items\n
    :return: string of sorted reconmendations\n 
    """
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


def generateGoodReconmendations(media, numberOfShows):
    """
    Gets and Sorts Reconmendations for easiest use\n
    :param media: list of media items\n
    :param numberOfShows: int of number of shows to be considered\n
    this value will count from the highest rated show to the lowest\n
    -1 will do all shows\n
    _________________________________________________________________\n
    :return: string of sorted reconmendations\n 
    """
    watched = []
    listOfdicts = []

    infin = True if numberOfShows == -1 else False

    for ent in media:
        watched.append(getTitleFromMediaDict(ent))
        if infin or numberOfShows > 0:
            listOfdicts.append(getRecsDict(ent))
        numberOfShows -= 1

    recs = combineDictionaries(listOfdicts)
    del recs[None]
    recs = removeWatched(watched, recs)
    recs = sorted(recs.items(), key=lambda x: x[1], reverse=True)
    recs = reconmendationsToReadable(recs)
    return recs

    # Here we define our query as a multi-line string
query = '''
query ($name: String) { # Define which variables will be used in the query (id)
  MediaListCollection (userName: $name, type: MANGA) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
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
nameId = input().__str__()

# Define our query variables and values that will be used in the query request
variables = {
    'name': nameId
}

# anilist public api url
url = 'https://graphql.anilist.co'

# Make the HTTP Api request
response = requests.post(url, json={'query': query, 'variables': variables})
js = response.json()

# gets media elements from your anilist
media = getMedia(js)


# Ask for number of shows
print("\ntype number of mangas to consider in reconmendations\nType nothing to do all manga")
nos = input("#Mangas:")

nos = -1 if not nos.isnumeric() else int(nos)
print("\n\n\n")

# combines and simplifies reconmendations
recs = generateGoodReconmendations(media, nos)

# read the line below and guess what it does
print(recs)

# prints reconmendations to a file
recs = ("all" if nos == -1 else nos.__str__()) + " manga\n" + recs
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(recs.__str__())
