# ./tiroche-scraper.py

import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import threading

# Modules
from Modules.fetch import getSoup
from Modules.helperFunctionsGeneral import strToQueryStr
from Modules.io import printTextToFile, appendTextToFile, clearFile
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

# PRIMARY FUNCTIONS

async def getItemDataFromLink(session, link, lock, itemData_file, allPageItemData, scraper, config):
    itemData = await scraper.getItemData(link, session)

    if (not config.filterOutBecauseImageInIgnore(itemData["imgLink"])):
        async with lock:
            allPageItemData.append(itemData)
        async with lock:
            with open(itemData_file, 'a', encoding='utf-8') as file:
                file.write(str(itemData) + '\n\n')

async def getAllItemDataFromLinks(scraper, config, allLinks, lock):
    if not os.path.exists('Outputs'):
        os.makedirs('Outputs')

    async with aiohttp.ClientSession() as session:
        allPageItemData = []
        tasks = [getItemDataFromLink(session, link, lock, allItemsPathName, allPageItemData, scraper, config) for link in allLinks]
        await asyncio.gather(*tasks)

        print("Finished gathering data from catalog page")
        return allPageItemData

async def getAllItemData(scraper, config, lock):
    stop = False
    pageCount = 1
    allItemData = []
    while not stop:
        response = scraper.getCatalogAtPageResponse(pageCount)
        if (response.status_code != 200):
            # Finished going over all the catalog pages
            printTextToFile(str(allItemData), allLinksPathName)
            return allItemData
        print(f"Getting paintings from catalog page number #{pageCount}")
        soup = getSoup(response)
        pageItemLinks = scraper.getCatalogsItemLinks(soup)
        pageItemLinksFiltered = [item for item in pageItemLinks if config.filterLinkKeep(item)]
        appendTextToFile(str(pageItemLinksFiltered), allLinksPathName)

        # USING ASYNC
        itemsFromLinksFromPage = await getAllItemDataFromLinks(scraper, config, pageItemLinksFiltered, lock)

        async with lock:
            allItemData.extend(itemsFromLinksFromPage)
        pageCount += 1
    
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

        print("---- SCRAPER ----")

        # Create Scraper object
        tirocheScraper = TirocheScraper(
                                        artistName=artistName,
                                        allLinksPathName= allLinksPathName,
                                        allItemsPathName= allItemsPathName,
                                        dataCsvPathName= dataCsvPathName
                                        )
        
        # Create Config object
        config = Config(
                        configPath= configPath,
                        ignoreLinksPath= ignoreLinksPath,
                        ignoreLinksImagesExtractedPath= ignoreLinksImagesExtractedPath,
                        scraper = tirocheScraper
                        )
        
        # Gather all item links
        print("Gathering links of all the paintings")
        print(f"Look at file '{allItemsPathName}' to see data collected")

        asyncio_lock = asyncio.Lock()
        allItemData = asyncio.run(getAllItemData(tirocheScraper, config, asyncio_lock))

        print("Finished gathering links for each painting page, see: ", allLinksPathName)
        print(f"Collected {len(allItemData)} paintings")

        # # Gather data on each item
        # print("Gathering data on each painting, see: ", allItemsPathName)
        # allItemData = getAllItemData(tirocheScraper, config, allItemLinks)
        # print("Finished gathering all data of paintings")

        # Turn to CSV
        listOfDictToCsv(allItemData, dataCsvPathName)
        print(f"You can find the csv file in: {dataCsvPathName}")

        # Config
        config.applyConfigFromAllItems(allItemData)


