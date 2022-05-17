import requests
from os import walk
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


def getMedia(jsonRes, includeCurrent):
    """
    This function returns the watched show list from the AniList query Response\n
    :param jsRep: json response from anilist query\n
    :param includeCurrent: boolean on whether or not to include shows/mangas currently being read or watched
    :return: list object of Media items from watched list\n
    """
    ls = getList(jsonRes)
    ls = list(ls[0].values()) + list(ls[1].values())
    # print(len(ls))
    return ls[0] + ls[1] if includeCurrent else ls[0]


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


def getRecsDict(dict_media):
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
