import sys

# pip3 install requests
import requests

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

# pip3 install pandas
import pandas as pd

# Modules
from Modules.fetch import getCatalogAtPageResponse, getPageOfUrl, getSoup, getUID4
from Modules.helperFunctionsGeneral import strToQueryStr
from Modules.debugging import printTextToFile, appendTextToFile, clearFile
from Modules.dataConverter import listOfDictToCsv
from Modules.config import applyConfigFromAllItems, filterLinkKeep, filterOutBecauseImageInIgnore

from Modules.TirocheScraper import TirocheScraper

# Globals

allLinksPathName = './Outputs/item_links.txt'
allItemsPathName = './Outputs/item_data.txt'
dataCsvPathName = './Outputs/data.csv'

# PRIMARY FUNCTIONS

def getAllItemLinks(scraper) :
    clearFile(allLinksPathName)
    stop = False
    count = 1
    itemLinks = []
    while (stop == False):
        response = scraper.getCatalogAtPageResponse(count)
        if (response.status_code != 200):
            printTextToFile(str(itemLinks), allLinksPathName)
            return itemLinks
        soup = getSoup(response)
        pageItemLinks = scraper.getCatalogsItemLinks(soup)
        pageItemLinksFiltered = [item for item in pageItemLinks if filterLinkKeep(item)]
        itemLinks.extend(pageItemLinksFiltered)
        count += 1
    
    # (won't get here)
    return itemLinks 

def getAllItemData(scraper, allLinks):
    allItemData = []
    clearFile(allItemsPathName)

    # Get data for each item
    # count = 0 # TODO: DELETE!!!!!!!!
    for link in allLinks:
        # if (count < 12): # TODO: DELETE!!!!!!!!
            # print("collecting data on item: ", count) # TODO: DELETE!!!!!!!!
            itemData = scraper.getItemData(link)
            if (not filterOutBecauseImageInIgnore(itemData["imgLink"])):
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



        # Create Scraper object
        tirocheScraper = TirocheScraper(
                                        artistName=artistName,
                                        allLinksPathName= allLinksPathName,
                                        allItemsPathName= allItemsPathName,
                                        dataCsvPathName= dataCsvPathName
                                        )



        # Gather all item links
        print("Gathering links of all the paintings")
        allItemLinks = getAllItemLinks(tirocheScraper)
        print("Finished gathering links for each painting page, see: ", allLinksPathName)

        # Gather data on each item
        print("Gathering data on each painting, see: ", allItemsPathName)
        allItemData = getAllItemData(tirocheScraper, allItemLinks)
        print("Finished gathering all data of paintings")

        # Turn to CSV
        listOfDictToCsv(allItemData, dataCsvPathName)
        print(f"You can find the csv file in: {dataCsvPathName}")

        # Config
        applyConfigFromAllItems(allItemData)


