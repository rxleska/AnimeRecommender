from urllib import response
import requests
from os import walk
from requests.models import requote_uri
import AnilistQueryAbstraction as aqa


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
        watched.append(aqa.getTitleFromMediaDict(ent))
        listOfdicts.append(aqa.getRecsDict(ent))

    recs = aqa.combineDictionaries(listOfdicts)
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
        watched.append(aqa.getTitleFromMediaDict(ent))
        if infin or numberOfShows > 0:
            listOfdicts.append(aqa.getRecsDict(ent))
        numberOfShows -= 1

    recs = aqa.combineDictionaries(listOfdicts)
    del recs[None]
    recs = removeWatched(watched, recs)
    recs = sorted(recs.items(), key=lambda x: x[1], reverse=True)
    recs = reconmendationsToReadable(recs)
    return recs


# Here we define our querys as a multi-line string
MangaQuery = '''
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

AnimeQuery = '''
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

# Anilist public api url
url = 'https://graphql.anilist.co'


# Prompt Anime or Manga and select query
print("\n\n\nType anime or a for Anime\nor Type manga or m for Manga\n:::Default is Anime:::")
reconType = input("Type:").__str__()
reconType = reconType.lower()
isAnime = False if reconType == "m" or reconType == "manga" else True
query = AnimeQuery if isAnime else MangaQuery

# Prompt for Anilist Username/ID
print("\n\n\nType your Anilist id")
nameId = input("id:").__str__()
variables = {
    'name': nameId  # used in query
}

# Creates API Request Based on Prompts listed above, requests data from api, and Gathers the Medias (elements show/comic) from the query
response = requests.post(url, json={'query': query, 'variables': variables})
js = response.json()
media = aqa.getMedia(js, not isAnime)

# Prompt for Number of Media Elements to use (# of shows/comics to consider) convert nothing to -1 for infinite consideration in other methods
print("\n\n\nType number of shows/mangas to consider in reconmendations\n:::Type nothing to include all:::")
numConsideration = input("# of shows/mangas to consider:")
numConsideration = -1 if not numConsideration.isnumeric() else int(numConsideration)
print("\n\n\n")

# Combine Reconmendations under prompted Parameters, then print and save them
recs = generateGoodReconmendations(media, numConsideration)
print(recs)
recs = ("all" if numConsideration == -1 else numConsideration.__str__()
        ) + " " + ("anime" if isAnime else "manga")+"\n" + recs
with open("out.txt", "w", encoding="utf-8") as f:
    f.write(recs.__str__())
