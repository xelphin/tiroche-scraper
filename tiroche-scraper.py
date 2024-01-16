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

def getAllItemData(scraper, config) :
    stop = False
    pageCount = 1
    allItemData = []
    while (stop == False):
        response = scraper.getCatalogAtPageResponse(pageCount)
        if (response.status_code != 200):
            # Finished going over all the catalog pages
            printTextToFile(str(allItemData), allLinksPathName)
            return allItemData
        # Get html of catalog page, and get all painting/item links from that page
        print(f"Getting paintings from catalog page number #{pageCount}")
        soup = getSoup(response)
        pageItemLinks = scraper.getCatalogsItemLinks(soup)
        pageItemLinksFiltered = [item for item in pageItemLinks if config.filterLinkKeep(item)]
        appendTextToFile(str(pageItemLinksFiltered), allLinksPathName)
        allItemData.extend(getAllItemData_aux(scraper, config, pageItemLinksFiltered)) # get painting/item data from each link
        pageCount += 1
    
    # (won't get here)
    return allItemData 

def getAllItemData_aux(scraper, config, allLinks):
    allItemData = []
    
    # Get data for each item
    # count = 0 # TODO: DELETE!!!!!!!!
    for link in allLinks:
        # if (count < 12): # TODO: DELETE!!!!!!!!
            # print("collecting data on item: ", count) # TODO: DELETE!!!!!!!!
            itemData = scraper.getItemData(link)
            if (not config.filterOutBecauseImageInIgnore(itemData["imgLink"])):
                allItemData.append(itemData)
                appendTextToFile(str(itemData), allItemsPathName)
            # count += 1 # TODO: DELETE!!!!!!!!

    # Reputting it so it's in a nice format
    clearFile(allItemsPathName)
    printTextToFile(str(allItemData), allItemsPathName)
    # Return
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
        allItemData = getAllItemData(tirocheScraper, config)
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


