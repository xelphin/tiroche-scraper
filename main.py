# ./tiroche-scraper.py

import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import threading

# Modules
from Modules.helperFunctionsGeneral import strToQueryStr, printSeparatingLines
from Modules.io import printTextToFile, clearFile
from Modules.dataConverter import listOfDictToCsv

from Modules.Config import Config
from Modules.TirocheScraper import TirocheScraper

# Globals

allLinksPathName = './Outputs/item_links.txt'
allItemsPathName = './Outputs/item_data.txt'
dataCsvPathName = './Outputs/data.csv'
configPath = "./Config/config.json"
ignoreLinksPath = "./Config/ignoreCertainPaintingPageLinks.txt"
ignoreLinksImagesExtractedPath = "./Config/ignoreCertainImageLinks.txt"


async def getAllItemData(scraper, config, lock):
    allItemData = []
    allItemData = await scraper.getAllCatalogPages(config, allItemData, lock)        
    printTextToFile(str(allItemData), allLinksPathName)
    return allItemData

if __name__ == "__main__":
    # Check if an argument (artistName) is provided
    if len(sys.argv) < 2:
        print("Usage: python3 myProgram.py artistName")
    else:
        # Get the artistName from the command line
        userInput = ' '.join(sys.argv[1:])
        artistName = strToQueryStr(userInput)

        clearFile(allLinksPathName)
        clearFile(allItemsPathName)

        # Create Config object
        config = Config(
                        configPath= configPath,
                        ignoreLinksPath= ignoreLinksPath,
                        ignoreLinksImagesExtractedPath= ignoreLinksImagesExtractedPath,
                        getImgCallback = TirocheScraper.getItemImgLink
                        )

        # Create Scraper object
        tirocheScraper = TirocheScraper(
                                        artistName=artistName,
                                        allLinksPathName= allLinksPathName,
                                        allItemsPathName= allItemsPathName,
                                        dataCsvPathName= dataCsvPathName
                                        )
        
        
        # Gather all item links
        print("Gathering links of all the paintings")
        print(f"Look at file '{allItemsPathName}' to see data collected")

        printSeparatingLines()
        print("------------ SCRAPER ")
        printSeparatingLines()
        asyncio_lock_scrape = asyncio.Lock()
        allItemData = asyncio.run(getAllItemData(tirocheScraper, config, asyncio_lock_scrape))

        printSeparatingLines()
        print("Finished gathering links for each painting page, see: ", allLinksPathName)
        print(f"Collected {len(allItemData)} paintings")
        

        # Turn to CSV
        listOfDictToCsv(allItemData, dataCsvPathName)
        print(f"You can find the csv file in: {dataCsvPathName}")
        printSeparatingLines()

        # Config
        print("Applying some config specifications...")
        config.applyConfigFromAllItems(allItemData) # (example: downloads images)


