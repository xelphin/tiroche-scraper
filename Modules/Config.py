import json
import os
import requests
from .fetch import getPageOfUrl, getSoup
from .io import appendTextToFile, clearFile

# USES SCRAPER

class Config:

    # INIT
    def __init__(self, configPath, ignoreLinksPath, ignoreLinksImagesExtractedPath, scraper):
        self.configPath = configPath
        self.ignoreLinksPath = ignoreLinksPath
        self.ignoreLinksImagesExtractedPath = ignoreLinksImagesExtractedPath
        self.scraper = scraper
        self.ignoreLinks = []
        self.ignoreImgLinks = []
        print("---- CONFIG ----")
        print("[Loading config...]")
        # config.json
        with open(configPath, 'r') as file:
            self.config =  json.load(file)
        
        if (self.config["ignoreCertainPaintingPageLinks"]):
            print("[-Loading links to ignore from config...]")
            self.ignoreLinks = self.__readLinesFromFile(ignoreLinksPath)
            if (self.config["ignoreCertainImageLinks"]):
                print("[--Loading imgs from links...]")
                # sophisticated: even if not the exact link, enough that they have the same image (painting) so as to make it be ignored
                self.ignoreImgLinks = self.__getImageLinksFromItemLinks(self.ignoreLinks, self.ignoreImgLinks)

        print("[Finished gathering data from config.]")


    def __removeJpgImages(self, folderPath):
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


    def __downloadImage(self, url, folderPath, fileName):
        if (url == ""):
            print("Couldn't find img for: ", fileName)
            return

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


    def __downloadImages(self, allItemData, downloadPath, deleteOldImages):
        if (deleteOldImages):
            self.__removeJpgImages(downloadPath) # clear what was in the images folder before
        count = 0
        for item in allItemData:
            self.__downloadImage(item["imgLink"], downloadPath, item['id']+".jpg")
            count+=1


    def __readLinesFromFile(self, filePath):
        lines = []
        try:
            with open(filePath, 'r') as file:
                lines = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"File not found: {filePath}")
        except Exception as e:
            print(f"Error reading file: {e}")
        
        return lines

    def __getImageLinksFromItemLinks(self, allLinks, arrToAddTo):
        arrToAddTo = []
        if (self.config["ignoreCertainImageLinksAlreadyUpdated"]):
            arrToAddTo = self.__readLinesFromFile(self.ignoreLinksImagesExtractedPath)
            print("[Haven't recalculated the 'ignoreCertainImageLinks' because of the Config/config.json 'ignoreCertainImageLinksAlreadyUpdated' is 'true']")
        else :
            clearFile(self.ignoreLinksImagesExtractedPath)
            for link in allLinks:
                response = getPageOfUrl(link)
                if (response.status_code == 200):
                    soup = getSoup(response)
                    imgLink = self.scraper.getItemImgLink(soup)
                    if (imgLink != ""):
                        arrToAddTo.append(imgLink)
                        appendTextToFile(str(imgLink), self.ignoreLinksImagesExtractedPath)
            print("[Next time, you can write 'true' in 'ignoreCertainImageLinksAlreadyUpdated' in Config/config.json because the img links have been calculated now]")
        
        return arrToAddTo
    
    # PUBLIC FUNCTIONS

    def filterLinkKeep(self, link):
        if (link in self.ignoreLinks):
            print("Need to ignore link: ", link)
            return False
        return True

    def filterOutBecauseImageInIgnore(self, link):
        if (link in self.ignoreImgLinks):
            print("Need to ignore img: ", link)
            return True
        return False

    def applyConfigFromAllItems(self, allItemData):
        if (self.config["downloadImages"]):
            self.__downloadImages(allItemData, self.config["pathToImagesPrinted"], self.config["deleteOldImages"])