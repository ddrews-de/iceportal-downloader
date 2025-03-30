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

def testIcePortalReachable():
    url = "https://iceportal.de/api1/rs/page/hoerbuecher"
    response = requests.get(url, headers=cfg.headers)
    # response.content.
    if response.status_code == 200 and len(response.text) > 100:
        return True
    else:
        return False


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
    doneFilePath = "audiobooks/{}/{}.done".format(titleshort, titleshort)

    if os.path.exists(doneFilePath):
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
                with open(jsonFilePath, "w") as jsonFile:
                    jsonFile.write(json.dumps(json_data, indent=4))
                with open(doneFilePath, "w") as doneFile:
                    doneFile.write("done")
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
            print("Chapter already exists")
            continue

        with open(savePath, "wb+") as code:
            code.write(audio.content)

        with open(countFilePath, "w") as countFile:
            countFile.write(str(counter+1))

    with open(jsonFilePath, "w") as jsonFile:
        jsonFile.write(json.dumps(json_data, indent=4))
    
    with open(doneFilePath, "w") as doneFile:
        doneFile.write("done")

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
    filePath = './zeitungskiosk/{}'.format(titleshort)
    createFolder(filePath)
    url = "https://iceportal.de/{}".format(itemurl)
    savePath = "zeitungskiosk/{}/{}-{}".format(titleshort,itemdate,titleshort)+".pdf"
    fileDonePath = "zeitungskiosk/{}/{}-{}".format(titleshort,itemdate,titleshort)+".done"
    if os.path.exists(fileDonePath):
        print("PDF already exists")
        with open(fileDonePath, "w") as code:
            code.write("done")
        return
    #Delete old done files
    for file in os.listdir(filePath):
        if file.endswith(".done"):
            os.remove(os.path.join(filePath, file))
    # download PDF 
    pdffile = requests.get(url)

    with open(savePath, "wb+") as code:
            code.write(pdffile.content)
    # create done file
    with open(fileDonePath, "w") as code:
            code.write("done")

# MAIN
# test if iceportal is reachable
if not testIcePortalReachable():
    print("Iceportal not reachable")
    exit()
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
