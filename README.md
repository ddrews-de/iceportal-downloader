# iceportal-downloader
Works only when connected to the WifionICE wifi and the website iceportal.de is online.

As the title describes...
A script which downloads all offerd newspapers, magazins and audiobooks from the deutsche bahn iceportal. Potcasts will be ignored.
It will test, if the pdf or the audiobook is already downloaded. You can delete/move the mp3, m4b and pdf files, to save space.
The test is looking for the .json file in the audiobooks subfolder or the .done file (including the date of the release date)
To download te files again, the best way is to delete the corresponding folder.
It will run even on Android in Termux. 



![](https://github.com/ddrews-de/iceportal-downloader/blob/master/git.gif)


## Setup Windows, Mac, Linux
1. git clone 'https://github.com/ddrews-de/iceportal-downloader.git'
2. cd iceportal-audiobooks-downloader
3. virtualenv env (make sure you are using python > 3.4)
4. source env/bin/activate
5. pip install -r requirements.txt
6. python main.py
7. enjoy


## Setup Termux on Android
1. Download Termux (https://github.com/termux/termux-app)
2. Run the following in the app
  1. pkg update && pkg upgrade
  2. termux-setup-storage
    (to access the files https://wiki.termux.com/wiki/Termux-setup-storage)
  3. pkg install python git
  4. git clone https://github.com/ddrews-de/iceportal-downloader.git
  5. cd iceportal-audiobooks-downloader
  6. pip install -r requirements.txt
  7. python main.py


### To-Do
* check for the website 
* add dynamic selection for types (magazin, newspaper, podcasts, audiobooks)
* extract new cookie automatically
* Update/completing Termux documantations


