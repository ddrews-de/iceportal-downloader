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
    boolTest = False
    jsonFilePath = "audiobooks/{}/{}.json".format(titleshort, titleshort)
    countFilePath = "audiobooks/{}/{}.count".format(titleshort, titleshort)

    if os.path.exists(jsonFilePath):
        print("audiobook exists")
        return

 
    url = "https://iceportal.de/api1/rs/page{}".format(title)
    responseChapter = requests.get(url, headers=cfg.headers)

    createFolder('./audiobooks/{}'.format(titleshort))

    # extract chapters
    json_data = json.loads(responseChapter.text)
    
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
        url = "https://iceportal.de/api1/rs/audiobooks/path{}".format(chapterPath)
        responseDownloadPath = requests.get( url, headers=cfg.headers, cookies=cfg.cookies)
        path = json.loads(responseDownloadPath.text)["path"]
        downloadPath.append(path)

    # download each track
    count = 0
    if os.path.exists(countFilePath):
        with open(countFilePath, "r") as countFile:
            count = int(countFile.read())
            if count >= len(downloadPath):
                print("audiobook exists")
                return

    for counter, track in enumerate(downloadPath):
        print("{}/{}".format(counter+1, len(downloadPath)))
        url = "https://iceportal.de{}".format(track)
        ext = track.split(".")[-1]
        audio = requests.get(url)
        savePath = "audiobooks/{}/{}_".format(titleshort, titleshort)+str(counter+1)+"."+ext
        
        if count == (counter+1) and os.path.exists(savePath):
            os.remove(savePath)

        if os.path.exists(savePath):
            continue

        with open(savePath, "wb+") as code:
            code.write(audio.content)

        with open(countFilePath, "w") as countFile:
            countFile.write(str(counter+1))

    with open(jsonFilePath, "w") as jsonFile:
        jsonFile.write(json.dumps(json_data, indent=4))


def getAllPDFs():
    PDFs = []
    url = "https://iceportal.de/api1/rs/page/zeitungskiosk"
    response = requests.get(url, headers=cfg.headers, cookies=cfg.cookies)
    # extract titles
    json_data = json.loads(response.text)
    items = json_data["teaserGroups"][0]["items"]
    for item in items:
        name = str(item["navigation"]["href"])
        # check if itemtype is not Podcast
        PDFs.append(name)

    return PDFs


def downloadPDF(title):
    print("Downloading PDF: {}".format(title))
    url = "https://iceportal.de/api1/rs/page{}".format(title)
    responseChapter = requests.get(url, headers=cfg.headers, cookies=cfg.cookies)
    # extract chapters
    json_data = json.loads(responseChapter.text)
    itemurl = str(json_data["navigation"]["href"])
    itemdate = str(json_data["date"])
    titleshort = str(json_data["segment"])
    createFolder('./zeitungskiosk/{}'.format(titleshort))
    url = "https://iceportal.de/{}".format(itemurl)
    savePath = "zeitungskiosk/{}/{}-{}".format(titleshort,itemdate,titleshort)+".pdf"
    fileDonePath = "zeitungskiosk/{}/{}-{}".format(titleshort,itemdate,titleshort)+".done"
    if os.path.exists(fileDonePath):
        print("PDF already exists")
        return
    
    pdffile = requests.get(url)
    with open(savePath, "wb+") as code:
            code.write(pdffile.content)
    # create done file
    with open(fileDonePath, "w") as code:
            code.write("done")

# MAIN
# extract all audiobooks
PDFs = getAllPDFs()
createFolder('./zeitungskiosk')

# download all audibooks
for PDF in PDFs:
    downloadPDF(str(PDF))

# MAIN
# extract all audiobooks
audiobooks = getAllAudiobooks()
createFolder('./audiobooks')

# download all audibooks
for book in audiobooks:
    downloadAudiobook(str(book))
