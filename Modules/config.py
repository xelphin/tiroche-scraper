import json
import os
import requests
from .scrapeFunctions import getItemImgLink
from .fetch import getPageOfUrl, getSoup
from .debugging import appendTextToFile, clearFile

# GLOBALS

# NOTE: Called from ../tiroche-scraper.py , so that's why the paths are written as they are
# TODO: kinda think this is bad code that only works because the only caller actually does have this in its relative paths
configPath = "./Config/config.json"
ignoreLinksPath = "./Config/ignoreLinks.txt"
ignoreLinksImagesExtractedPath = "./Config/ignoreLinksImages.txt"
ignoreLinks = []
ignoreImgLinks = []
def getConfig():
    with open(configPath, 'r') as file:
        return json.load(file)
config = getConfig()

# HELPER FUNCTIONS

def removeJpgImages(folderPath):
    # (Asked chatGPT lol)
    if os.path.exists(folderPath):
        # Iterate over all files in the folder
        for item in os.listdir(folderPath):
            itemPath = os.path.join(folderPath, item)

            # Check if it's a file and has a ".jpg" or ".jpeg" extension
            if os.path.isfile(itemPath) and item.lower().endswith(('.jpg', '.jpeg')):
                os.remove(itemPath)
                print(f"Removed: {itemPath}")

        print(f"All JPG images removed from '{folderPath}'.")
    else:
        print(f"Folder '{folderPath}' does not exist.")

def downloadImage(url, folderPath, fileName):
    # (Asked chatGPT lol)
    os.makedirs(folderPath, exist_ok=True) # Create folder if needed
    filePath = os.path.join(folderPath, fileName) # Combine the folder path and file name to get the full file path
    response = requests.get(url) # Send an HTTP request to the URL

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the file in binary write mode and write the content
        with open(filePath, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {filePath}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")



def downloadImages(allItemData, downloadPath, deleteOldImages):
    if (deleteOldImages):
        removeJpgImages(downloadPath) # clear what was in the images folder before
    count = 0
    for item in allItemData:
        downloadImage(item["imgLink"], downloadPath, item['id']+".jpg")
        count+=1

def readLinesFromFile(filePath):
    lines = []
    try:
        with open(filePath, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File not found: {filePath}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return lines

def getImageLinksFromItemLinks(allLinks, arrToAddTo):
    arrToAddTo = []
    clearFile(ignoreLinksImagesExtractedPath)
    for link in allLinks:
        response = getPageOfUrl(link)
        if (response.status_code == 200):
            soup = getSoup(response)
            imgLink = getItemImgLink(soup)
            if (imgLink != ""):
                arrToAddTo.append(imgLink)
                appendTextToFile(str(imgLink), ignoreLinksImagesExtractedPath)
    
    return arrToAddTo



# PRE MUST DO


if (config["ignoreCertainLinks"]):
    ignoreLinks = readLinesFromFile(ignoreLinksPath)
    if (config["sophisticatedIgnoreCertainLinks"]):
        # sophisticated: even if not the exact link, enough that they have the same image (painting) so as to make it be ignored
        ignoreImgLinks = getImageLinksFromItemLinks(ignoreLinks, ignoreImgLinks)
        
                


# MAIN CONFIG FUNCTIONS
        
def filterLinkKeep(link):
    if (link in ignoreLinks):
        print("Need to ignore link: ", link)
        return False
    return True

def filterOutBecauseImageInIgnore(link):
    if (link in ignoreImgLinks):
        print("Need to ignore img: ", link)
        return True
    return False

def applyConfigFromAllItems(allItemData):
    if (config["downloadImages"]):
        downloadImages(allItemData, config["pathToImagesPrinted"], config["deleteOldImages"])