# ./Modules/TirocheScraper.py

import requests
import re
import aiohttp
import asyncio

from .Scraper import Scraper
from .fetch import getSoup, getSoupFromContent, getPageOfUrl_async
from .io import printTextToFile, appendTextToFile, clearFile

# Main class for web scraping Tiroche website specifically

class TirocheScraper(Scraper):

    # -----------------
    # CATALOG FUNCTIONS
    # -----------------
        
    def __getFirstNonNumericChar(self, str):
        for char in str:
            if char not in ['-', '.', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return char

        return ""
    
    def __getLinkAtPage(self, pageNum):
        return f"https://www.tiroche.co.il/paintings-authors/{self.artistName}/page/{pageNum}/"
    
    def __getAmountOfPagesToLoad(self, catalogPageSoup):
        navElem = catalogPageSoup.find(attrs={'role': 'navigation'})
        if not navElem:
            print("Only one catalog page to load.")
            return 1
        navContainer = navElem.find(class_="nav-links")
        navContainer_elems = navContainer.find_all()
        if len(navContainer_elems) >= 2:
            # Get the second-to-last child element
            lastPageNumberLink = navContainer_elems[-2]
            print(f"There are {lastPageNumberLink.get_text()} catalog pages that need to be loaded.")
            return lastPageNumberLink.get_text()
        else:
            print("Odd page configuration -> ???")
            return 1
    
    # Get catalogue from Tiroche at page
    def __getCatalogAtPageResponse(self, pageNum):
        url = self.__getLinkAtPage(str(pageNum))
        response = requests.get(url)
        return response
    
    async def getItemDataFromLink(self, session, link, lock, itemData_file, allPageItemData, config, catalogPageNum, itemCount):
        itemData = await self.getItemData(link, session, catalogPageNum, itemCount)

        if (not config.filterOutBecauseImageInIgnore(itemData["imgLink"])):
            async with lock:
                allPageItemData.append(itemData)
            async with lock:
                with open(itemData_file, 'a', encoding='utf-8') as file:
                    file.write(str(itemData) + '\n\n')
        
        else:
            print(f"## from catalog page {catalogPageNum}, item {itemCount} -> ignoring item because of config")

    def getCatalogsItemLinks(self, catalogPage):
        itemsLinks = []
        catalog =  catalogPage.find(id="catalog-section")

        itemDivs = catalog.find_all('div', recursive=False)

        for itemDiv in itemDivs:
            itemImgDiv = itemDiv.find('div', class_='lot-item__img')
            if itemImgDiv is not None:
                itemLinkElem =  itemImgDiv.find('a')
                itemsLinks.append(itemLinkElem.attrs['href'])

        return itemsLinks
     
    async def __getCatalogAtPageSoup_async(self, link, catalogPageNum, allCatalogPagesSoups, allItemData, config, lock, session):
        content =  await getPageOfUrl_async(session, link)
        soup = getSoupFromContent(content)
        async with lock:
            print("Read catalog page: ", catalogPageNum)
            allCatalogPagesSoups.append(soup)

        # Get items
        pageItemLinks = self.getCatalogsItemLinks(soup)
        pageItemLinksFiltered = [item for item in pageItemLinks if config.filterLinkKeep(item)]
        appendTextToFile(str(pageItemLinksFiltered), self.allLinksPathName)
        itemsFromLinksFromPage = await self.getAllItemDataFromLinks(config, pageItemLinksFiltered, catalogPageNum, lock)

        async with lock:
            allItemData.extend(itemsFromLinksFromPage)
        

    async def getAllItemData(self, config, allItemData, lock):
        # Get first page (sync)
        allCatalogPagesSoups = []
        firstPage = self.__getCatalogAtPageResponse(1)
        soupFirstPage = getSoup(firstPage)
        # Get amount of pages that will need to be loaded (can find in first page) TODO
        pagesToLoad = int(self.__getAmountOfPagesToLoad(soupFirstPage))
        # Load the rest of the pages and their items (async)
        catalogPagesLinksToLoad = [self.__getLinkAtPage(str(i)) for i in range(1, pagesToLoad+1)]
        async with aiohttp.ClientSession() as session:
            tasks = [self.__getCatalogAtPageSoup_async(link, index+1, allCatalogPagesSoups, allItemData, config, lock, session) for index, link in enumerate(catalogPagesLinksToLoad)]
            await asyncio.gather(*tasks)

            # Return all catalog page soups
            return allItemData

    # --------------
    # ITEM FUNCTIONS
    # --------------

    # Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
    # returns artist name
    def getArtistName(self, itemPage):
        titleDiv =  itemPage.find(class_="single-lot__h1")
        if titleDiv is None:
            return ""
        titleElem =  titleDiv.find('h1')
        if titleElem is None:
            return ""
        return titleElem.get_text()

    # Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
    # returns img link
    @staticmethod
    def getItemImgLink(itemPage):
        imageDiv =  itemPage.find(id="wrpLotImages")
        if imageDiv is None:
            return ""
        imageElem =  imageDiv.find('a')
        if imageElem is None:
            return ""
        imageLink = imageElem.attrs['href']
        if imageLink is not None:
            return imageLink
        return ""

    # Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
    # returns the text of the information on the item
    def getItemText(self, itemPage):
        textDiv =  itemPage.find(class_="single-lot__body")
        if textDiv is None:
            return ""
        textElem =  textDiv.find('p')
        if textElem is None:
            return ""
        text = textElem.get_text()
        return text

    # Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
    # returns the estimated price
    def getItemEstimatedPrice(self, itemPage, itemData):
        textElem =  itemPage.find(class_="single-lot__estimate")
        if textElem is None:
            return ""
        textElem =  textElem.find('strong')
        if textElem is None:
            return ""
        text = textElem.get_text()
        textArr = text.split('-')
        
        itemData["currency"] = self.__getFirstNonNumericChar(text)
        if (len(textArr) == 2):
            itemData["low-estimate"] = re.sub(r'[^0-9.]', '', textArr[0])
            itemData["high-estimate"] = re.sub(r'[^0-9.]', '', textArr[1])
        elif (len(textArr) == 1):
            itemData["high-estimate"] = re.sub(r'[^0-9.]', '', textArr[0])
        
        return itemData


    # Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
    # extracts from the paragraph (text) found the values: innacurate extraction!
    # EXTRACT FROM ITEM TEXT THE VALUES

    def __dimensionsSplitter(self, dim):
        if ('×' in dim):
            return dim.split('×')
        if ('X' in dim):
            return dim.split('X')
        if ('/' in dim):
            return dim.split('/')
        return ""

    def __extractFromItemTextTheValues_dimensiones(self, dim):
        dimensions = {
            "height": "",
            "width": "",
            "units": ""
        }
        dimSepArr = self.__dimensionsSplitter(dim)
        if (dimSepArr == ""):
            return dimensions
        units = ""
        if (len(dimSepArr) > 1):
            units = re.sub(r'[^a-zA-Z]', '', dimSepArr[1]) # Get only letters
        if (len(dimSepArr) < 2):
            return dimensions
        return {
            "height": re.sub(r'[^0-9.]', '', dimSepArr[0]),
            "width": re.sub(r'[^0-9.]', '', dimSepArr[1]),
            "units": units
        }

    def __extractFromItemTextTheValues_year(self, text):
        match = re.search(r'\b\d{4}\b', text) # first 4-digit number that appears
        if match:
            return match.group()
        return ""

    def __cleanupText(self, text):
        text = text.replace('\n', ',') # Replace '\n' with comma
        text = re.sub(r',\s*,', ',', text) # Replace consecutive commas with a single comma
        if text.endswith('.'):
            text = text[:-1]
        return text

    def extractFromItemTextTheValues(self, text, itemData):
        # Assumes text appears as "Title, type, 00×00 units . signed/unsigned" for it to work properly
        text = self.__cleanupText(text)
        pointSepArr = text.rsplit('.', 1) # Splits with the last '.' that appears
        if (len(pointSepArr) == 0):
            return ""
        commaSepArr = pointSepArr[0].split(',')

        itemData["guessed-year"] = self.__extractFromItemTextTheValues_year(text)
        if (len(pointSepArr) > 1):
            itemData["guessed-signed"] = pointSepArr[1]
        if (len(commaSepArr) > 0):
            itemData["guessed-title"] = ''.join(commaSepArr[:-2])
        if (len(commaSepArr) > 1):
            itemData["guessed-paintingType"] = commaSepArr[-2]
        if (len(commaSepArr) > 2):
            dimensions = self.__extractFromItemTextTheValues_dimensiones(commaSepArr[-1])
            itemData["guessed-height"] = dimensions["height"]
            itemData["guessed-width"] = dimensions["width"]
            itemData["guessed-units"] = dimensions["units"]

        return itemData