import json
import os
import requests
import asyncio
import aiohttp
import threading
from .fetch import getPageOfUrl_async, getSoupFromContent
from .io import appendTextToFile, clearFile


# USES SCRAPER

class Config:

    # INIT
    def __init__(self, configPath, ignoreLinksPath, ignoreLinksImagesExtractedPath, getImgCallback):
        self.configPath = configPath
        self.ignoreLinksPath = ignoreLinksPath
        self.ignoreLinksImagesExtractedPath = ignoreLinksImagesExtractedPath
        self.getImgCallback = getImgCallback
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
                self.ignoreImgLinks = asyncio.run(self.__getImageLinksFromItemLinks(self.ignoreLinks, self.ignoreImgLinks))

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

            print(f"All JPG images removed from '{folderPath}'.")
        else:
            print(f"Folder '{folderPath}' does not exist.")


    async def __downloadImage(self, session, url, lock, folderPath, fileName):
        if (url == ""):
            print("Couldn't find img for: ", fileName)
            return

        # (Asked chatGPT lol)
        os.makedirs(folderPath, exist_ok=True) # Create folder if needed
        filePath = os.path.join(folderPath, fileName) # Combine the folder path and file name to get the full file path
        content = await getPageOfUrl_async(session, url) # Send an HTTP request to the URL

        if content is not None:
            # Open the file in binary write mode and write the content
            # TODO: Maybe use "with lock: "
            print(f"Downloading: {fileName}")
            with open(filePath, 'wb') as file:
                file.write(content)
            
        else:
            print(f"Failed to download image {fileName}.")


    async def __downloadImages(self, allItemData, downloadPath, deleteOldImages):
        if (deleteOldImages):
            self.__removeJpgImages(downloadPath) # clear what was in the images folder before
        
        async with aiohttp.ClientSession() as session:
            lock = threading.Lock()
            tasks = [self.__downloadImage(session, item["imgLink"], lock, downloadPath, item['id']+".jpg") for item in allItemData]
            await asyncio.gather(*tasks)

        print(f"Finished downloading images. Can be found in: {downloadPath}")


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
    
    async def __getImageLinksFromItemLinks_aux(self, session, link, lock, arrToAddTo):
        content = await getPageOfUrl_async(session, link)

        if (content is not None):
            soup = getSoupFromContent(content)
            imgLink = self.getImgCallback(soup)
            if (imgLink != ""):
                with lock:
                    arrToAddTo.append(imgLink)
                with lock:
                    appendTextToFile(str(imgLink), self.ignoreLinksImagesExtractedPath)


    async def __getImageLinksFromItemLinks(self, allLinks, arrToAddTo):
        async with aiohttp.ClientSession() as session:
            lock = threading.Lock()
            arrToAddTo = []
            if (self.config["ignoreCertainImageLinksAlreadyUpdated"]):
                arrToAddTo = self.__readLinesFromFile(self.ignoreLinksImagesExtractedPath)
                print("[Haven't recalculated the 'ignoreCertainImageLinks' because of the Config/config.json 'ignoreCertainImageLinksAlreadyUpdated' is 'true']")
            else :
                clearFile(self.ignoreLinksImagesExtractedPath)

                tasks = [self.__getImageLinksFromItemLinks_aux(session, link, lock, arrToAddTo) for link in allLinks]
                await asyncio.gather(*tasks)


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
            asyncio.run(self.__downloadImages(allItemData, self.config["pathToImagesPrinted"], self.config["deleteOldImages"]))