import sys

# Modules
from Modules.fetch import getSoup
from Modules.helperFunctionsGeneral import strToQueryStr
from Modules.debugging import printTextToFile, appendTextToFile, clearFile
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

def getAllItemLinks(scraper, config) :
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
        pageItemLinksFiltered = [item for item in pageItemLinks if config.filterLinkKeep(item)]
        itemLinks.extend(pageItemLinksFiltered)
        count += 1
    
    # (won't get here)
    return itemLinks 

def getAllItemData(scraper, config, allLinks):
    allItemData = []
    clearFile(allItemsPathName)

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
        allItemLinks = getAllItemLinks(tirocheScraper, config)
        print("Finished gathering links for each painting page, see: ", allLinksPathName)

        # Gather data on each item
        print("Gathering data on each painting, see: ", allItemsPathName)
        allItemData = getAllItemData(tirocheScraper, config, allItemLinks)
        print("Finished gathering all data of paintings")

        # Turn to CSV
        listOfDictToCsv(allItemData, dataCsvPathName)
        print(f"You can find the csv file in: {dataCsvPathName}")

        # Config
        config.applyConfigFromAllItems(allItemData)


