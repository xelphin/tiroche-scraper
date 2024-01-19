# ./tiroche-scraper.py

import sys
import asyncio
from bs4 import BeautifulSoup
import time

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

def applyConfigSpecsOnItemData(config):
    print("Applying some config specifications...")
    start_time_config = time.time()
    config.applyConfigFromAllItems(allItemData) # (example: downloads images)
    end_time_config = time.time()
    print(f"Total time config specs took: {end_time_config-start_time_config} sec (downloading, ...)")

async def getAllItemData(scraper, lock):
    allItemData = []
    allItemData = await scraper.getAllItemData(allItemData, lock)        
    printTextToFile(str(allItemData), allLinksPathName)
    return allItemData

def applyScraper(scraper):
    # Gather all item links
    print("Gathering links of all the paintings")
    print(f"Look at file '{allItemsPathName}' to see data collected")

    printSeparatingLines()
    print("------------ SCRAPER ")
    printSeparatingLines()
    start_time_scraping = time.time()
    asyncio_lock_scrape = asyncio.Lock()
    allItemData = asyncio.run(getAllItemData(tirocheScraper, asyncio_lock_scrape))

    printSeparatingLines()
    print("Finished gathering links for each painting page, see: ", allLinksPathName)
    print(f"Collected {len(allItemData)} paintings")
    
    # Turn to CSV
    listOfDictToCsv(allItemData, dataCsvPathName)
    print(f"You can find the csv file in: {dataCsvPathName}")
    printSeparatingLines()

    end_time_scraping = time.time()
    print(f"Total time scraping took: {end_time_scraping-start_time_scraping} sec")

    return allItemData

def initConfig():
    start_time_config_init = time.time()
    config = Config(
                    configPath= configPath,
                    ignoreLinksPath= ignoreLinksPath,
                    ignoreLinksImagesExtractedPath= ignoreLinksImagesExtractedPath,
                    getImgCallback = TirocheScraper.getItemImgLink
                    )
    
    end_time_config_init = time.time()
    print(f"Total time config initialization took: {end_time_config_init-start_time_config_init} sec")

    return config

def clearFiles():
    clearFile(allLinksPathName)
    clearFile(allItemsPathName)

if __name__ == "__main__":
    # Check if an argument (artistName) is provided
    if len(sys.argv) < 2:
        print("Usage: python3 myProgram.py artistName")
    else:

        start_time = time.time()

        # Get the artistName from the command line
        userInput = ' '.join(sys.argv[1:])
        artistName = strToQueryStr(userInput)

        clearFiles()

        config = initConfig()

        # Create Scraper object
        tirocheScraper = TirocheScraper(
                                        artistName=artistName,
                                        allLinksPathName= allLinksPathName,
                                        allItemsPathName= allItemsPathName,
                                        dataCsvPathName= dataCsvPathName,
                                        config= config
                                        )
        
        # Get all item data (paintings) using scraper
        allItemData = applyScraper(tirocheScraper)

        applyConfigSpecsOnItemData(config)

        end_time = time.time()
        print(f"Total time everything took: {end_time-start_time} sec. Collected {len(allItemData)} paintings")


