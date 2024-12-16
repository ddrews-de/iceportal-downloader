import requests
import json
from pprint import pprint as pp
import urllib
import config as cfg
import os


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def getAllAudiobooks():
    audiobooks = []

    url = "https://iceportal.de/api1/rs/page/hoerbuecher"
    response = requests.get(url, headers=cfg.headers)

    # extract titles
    json_data = json.loads(response.text)
    items = json_data["teaserGroups"][0]["items"]

    for item in items:
        name = str(item["navigation"]["href"])
        itemtype = str(item["subtitle"])
        
        # check if itemtype is not Podcast
        if itemtype != "Podcast":
            audiobooks.append(name)

    return audiobooks


def downloadAudiobook(title):
    titleshort = title.split("/")[2]
    print("Downloading audiobook: {}".format(title))
    boolTest = True
    jsonFilePath = "audiobooks/{}/{}.json".format(titleshort, titleshort)

    if os.path.exists(jsonFilePath):
        print("audiobook exists")
        return

    url = "https://iceportal.de/api1/rs/page{}".format(title)
    responseChapter = requests.get(url, headers=cfg.headers)

    createFolder('./audiobooks/{}'.format(titleshort))

    # extract chapters
    json_data = json.loads(responseChapter.text)

    with open(jsonFilePath, "w") as jsonFile:
        jsonFile.write(json.dumps(json_data, indent=4))
    
    playlist = json_data["files"]

    itemcover = str(json_data["picture"]["src"])
    urlcover = "https://iceportal.de/{}".format(itemcover)
    imgsavePath = "audiobooks/{}/cover.jpg".format(titleshort)
    imgdata = requests.get(urlcover)
    with open(imgsavePath, "wb+") as imgcode:
        imgcode.write(imgdata.content)
   
    # extract downloadPath for each chapter
    downloadPath = []
    if boolTest:
        return
    
    for chapter in playlist:
        chapterPath = chapter["path"]

        url = "https://iceportal.de/api1/rs/audiobooks/path{}".format(
            chapterPath)
        responseDownloadPath = requests.get(
            url, headers=cfg.headers, cookies=cfg.cookies)

        path = json.loads(responseDownloadPath.text)["path"]
        downloadPath.append(path)

    # download each track
    for counter, track in enumerate(downloadPath):
        print("{}/{}".format(counter+1, len(downloadPath)))

        url = "https://iceportal.de{}".format(track)
        audio = requests.get(url)

        savePath = "audiobooks/{}/{}_".format(titleshort,
                                              titleshort)+str(counter+1)+".mp3"
        with open(savePath, "wb+") as code:
            code.write(audio.content)


# MAIN
# extract all audiobooks
audiobooks = getAllAudiobooks()
createFolder('./audiobooks')

# download all audibooks
for book in audiobooks:
    downloadAudiobook(str(book))
