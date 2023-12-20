import sys

# pip3 install requests
import requests

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

# pip3 install pandas
import pandas as pd

# Modules
from Modules.fetch import getCatalogAtPageResponse, getPageOfUrl, getSoup
from Modules.helperFunctionsGeneral import strToQueryStr
from Modules.scrapeFunctions import getCatalogsItemLinks, getItemImgLink, getItemText, extractFromItemTextTheValues, getItemEstimatedPrice
from Modules.debugging import printTextToFile, appendTextToFile, clearFile
from Modules.dataConverter import listOfDictToCsv
from Config.config import applyConfig

# Globals

allLinksPathName = './Outputs/item_links.txt'
allItemsPathName = './Outputs/item_data.txt'
dataCsvPathName = './Outputs/data.csv'

# PRIMARY FUNCTIONS
def getAllItemLinks(artistName) :
    clearFile(allLinksPathName)
    stop = False
    count = 1
    itemLinks = []
    while (stop == False):
        response = getCatalogAtPageResponse(count, artistName)
        if (response.status_code != 200):
            printTextToFile(str(itemLinks), allLinksPathName)
            return itemLinks
        soup = getSoup(response)
        pageItemLinks = getCatalogsItemLinks(soup)
        itemLinks.extend(pageItemLinks)
        count += 1
    
    # (won't get here)
    return itemLinks     

def getItemData(itemLink):
    itemData = {}
    response = getPageOfUrl(itemLink)
    if (response.status_code != 200):
        return ""
    soup = getSoup(response)

    itemData['websiteLink'] = itemLink
    itemData['imgLink'] = getItemImgLink(soup)
    itemInfo = getItemText(soup)
    itemData['info'] = itemInfo
    itemData.update(extractFromItemTextTheValues(itemInfo))
    itemData.update(getItemEstimatedPrice(soup))

    return itemData

def getAllItemData(allLinks):
    allItemData = []
    clearFile(allItemsPathName)
    # Get data for each item
    for link in allLinks:
        itemData = getItemData(link)
        allItemData.append(itemData)
        appendTextToFile(str(itemData), allItemsPathName)
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

        # Gather all item links
        print("Gathering links of all the paintings")
        allItemLinks = getAllItemLinks(artistName)
        print("Finished gathering links for each painting page, see: ", allLinksPathName)

        # Gather data on each item
        print("Gathering data on each painting, see: ", allItemsPathName)
        allItemData = getAllItemData(allItemLinks)
        print("Finished gathering all data of paintings")

        # Turn to CSV
        listOfDictToCsv(allItemData, dataCsvPathName)
        print(f"You can find the csv file in: {dataCsvPathName}")

        # Config
        applyConfig(allItemData)


