# ./Modules/Scraper.py
import os
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from .fetch import getUID4_async, getPageOfUrl_async, getSoupFromContent

# DON'T IMPORT CONFIG

class Scraper:

    # INIT
    def __init__(self, artistName, allLinksPathName, allItemsPathName, dataCsvPathName):
        self.artistName = artistName
        self.allLinksPathName = allLinksPathName
        self.allItemsPathName = allItemsPathName
        self.dataCsvPathName = dataCsvPathName

    # -----------------------
    # ITEM SCRAPING FUNCTIONS
    # -----------------------
        
    # self.getItemData() methods -> Scraping the item/painting page
    # Example for item/painting page: https://www.tiroche.co.il/auction/178-en/lot-507-128/
    # --->
    def getArtistName(self, itemPage):
        return ""
    
    @staticmethod
    @abstractmethod
    def getItemImgLink(itemPage):
        return ""
    
    def getItemText(self, itemPage):
        return ""
    
    def extractFromItemTextTheValues(self, text, itemData):
        itemData = itemData
    
    def getItemEstimatedPrice(self, itemPage, itemData):
        itemData = itemData
    
    def __itemCreator(self):
        item = {
            "id": "",
            "artist": "",
            "websiteLink": "",
            "imgLink": "",
            "height": "",
            "width": "",
            "units": "",
            "low-estimate": "",
            "high-estimate": "",
            "currency": "",
            "info": "",
            "guessed-year": "",
            "guessed-signed": "",
            "guessed-title": "",
            "guessed-paintingType": "",
            "guessed-height": "",
            "guessed-width": "",
            "guessed-units": ""
        }
        return item
    
    async def getItemData(self, itemLink, session, catalogPageNum, itemCount):
        itemData = self.__itemCreator()
        content = await getPageOfUrl_async(session, itemLink)
        print(f"## Finished awaiting: catalog page {catalogPageNum}, item {itemCount}")
        
        soup = getSoupFromContent(content)

        itemData['id'] = await getUID4_async() # Because of this line, you get a "break" between the two prints
        itemData['artist'] = self.getArtistName(soup)
        itemData['websiteLink'] = itemLink
        itemData['imgLink'] = self.getItemImgLink(soup)
        itemInfo = self.getItemText(soup)
        itemData['info'] = itemInfo
        itemData = self.extractFromItemTextTheValues(itemInfo, itemData)
        itemData = self.getItemEstimatedPrice(soup, itemData)

        print(f"## Finished analyzing: catalog page {catalogPageNum}, item {itemCount} and getting UID: {itemData['id']}")

        return itemData
    
    # <---

    # -----------------------
    # GETTING LINKS FUNCTIONS
    # -----------------------

    # Get (scrape) data from item/painting link
    # Example for item/painting link: https://www.tiroche.co.il/auction/178-en/lot-507-128/
    @abstractmethod
    async def getItemDataFromLink(self, session, link, lock, itemData_file, allPageItemData, config, catalogPageNum, itemCount):
        pass

    # From collection of item/painting links, for each link, retrieves data (by calling self.getItemData())
    # Example for item/painting link: https://www.tiroche.co.il/auction/178-en/lot-507-128/
    async def getAllItemDataFromLinks(self, config, allLinks, catalogPageNum, lock):
        if not os.path.exists('Outputs'):
            os.makedirs('Outputs')

        async with aiohttp.ClientSession() as session2:
            allPageItemData = []
            tasks = [self.getItemDataFromLink(session2, link, lock, self.allItemsPathName, allPageItemData, config, catalogPageNum, index) for index, link in enumerate(allLinks)]
            await asyncio.gather(*tasks)

            print("# Finished collecting all data from catalog page: ", catalogPageNum)
            return allPageItemData

    # Given catalogPage (soup of website like: https://www.tiroche.co.il/paintings-authors/izhak-frenkel-frenel/)
    # returns all the itemLinks present in the page, such as: https://www.tiroche.co.il/auction/178-en/lot-507-128/
    @abstractmethod
    def getCatalogsItemLinks(self, catalogPage):
        pass

    # Collects all item/painting data from link and the data from the 'next' pages if there are
    # Example for page(s) where collection is done from: https://www.tiroche.co.il/paintings-authors/izhak-frenkel-frenel/
    @abstractmethod
    async def getAllItemData(self, config, allItemData, lock):
        pass
    

