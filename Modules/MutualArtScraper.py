# ./Modules/MutualArtScraper.py

import requests
import re
import aiohttp
import asyncio

from .Scraper import Scraper
from .fetch import getSoup, getSoupFromContent, getPageOfUrl_async, scrollThroughPageAndGetSoup, getPageOfUrl_useHeaders
from .io import printTextToFile, appendTextToFile, clearFile
from bs4 import BeautifulSoup


# Main class for web scraping Tiroche website specifically

WAIT_TIME_SCROLL = 0.1 # TODO: Change to higher number (for testing, am leaving at low number)

class MutualArtScraper(Scraper):

    # -----------------
    # CATALOG FUNCTIONS
    # -----------------
        
    def getCatalogsItemLinks(self, catalogPage):
        itemsLinks = []
        all_items_div = catalogPage.find('div', id='artworkmasonrygrid')
        itemDivs = all_items_div.find_all('div', recursive=False)

        for itemDiv in itemDivs:
            itemLink = itemDiv.find('div').get('data-link')
            itemLink = "https://www.mutualart.com" + itemLink
            itemsLinks.append(itemLink)

        return itemsLinks

    # -----------------------
    # ITEM SCRAPING FUNCTIONS
    # -----------------------
    def getArtistName(self, itemPage):
        return "" # TODO

    @staticmethod
    def getItemImgLink(itemPage):
        imageDiv = itemPage.find(id="lot-carousel-slick")
        if imageDiv is None:
            return ""
        imageElem =  imageDiv.find('img')
        if imageElem is None:
            return ""
        imageLink = imageElem.get('data-src')
        if imageLink is not None:
            return imageLink
        return ""
    
    def getItemText(self, itemPage):
        return "" # TODO
    
    def extractFromItemTextTheValues(self, text, itemData):
        return itemData # TODO
    
    def getItemEstimatedPrice(self, itemPage, itemData):
        return itemData # TODO
    
    async def getItemDataFromLink(self, session, link, lock, itemData_file, allPageItemData, catalogPageNum, itemCount):
        # TODO: Maybe move to abstract class?
        itemData = await self.getItemData(link, session, catalogPageNum, itemCount)

        if (not self.config.filterOutBecauseImageInIgnore(itemData["imgLink"])):
            async with lock:
                allPageItemData.append(itemData)
            async with lock:
                with open(itemData_file, 'a', encoding='utf-8') as file:
                    file.write(str(itemData) + '\n\n')
        
        else:
            print(f"## from catalog page {catalogPageNum}, item {itemCount} -> ignoring item because of config")

    # -----------------------
    # GETTING LINKS FUNCTIONS
    # -----------------------

    def __getPageOfAllArtistsWithNameResults(self):
        name_arr = (self.artistName).split("-")
        if len(name_arr) == 0:
            raise ValueError("Artist name given is bad format: Empty or just '-'")
        # Create search query string
        search_str = name_arr[0]
        for word in name_arr[1:]:
            search_str += "%20"+word

        pageLink = f"https://www.mutualart.com/Results/search?q={search_str}"
        print(f"searching for artist on {pageLink}")
        page = getPageOfUrl_useHeaders(pageLink)
        soup = getSoup(page)
        return soup
    
    def __getPageOfArtist(self):
        page_of_results_for_artist_name = self.__getPageOfAllArtistsWithNameResults()
        all_results_for_artist_name = page_of_results_for_artist_name.find('div', class_='related-items-list')
        if not all_results_for_artist_name:
            print("No results for this artist.")
            return None
        first_result_for_artist_name = all_results_for_artist_name.find('div')
        if not first_result_for_artist_name:
            print("Unusual formatting in page")
            return None
        link_for_artist_page = first_result_for_artist_name.find('a').get('href')
        link_for_artist_page = "https://www.mutualart.com" + link_for_artist_page + "/Artworks"
        print("link is: ", link_for_artist_page)
        return link_for_artist_page


    # Collects all item/painting data from link and the data from the 'next' pages if there are
    async def getAllItemData(self, allItemData, lock):
        try:
            link_to_artist_page = self.__getPageOfArtist()
        except Exception as e:
            print("Trouble using page")
            print("Possible, that the website blocked you for the time being. Try coming back tomorrow.")
            return []
        catalog_soup = scrollThroughPageAndGetSoup(link_to_artist_page, WAIT_TIME_SCROLL)
        allPageItemLinks = self.getCatalogsItemLinks(catalog_soup)
        pageItemLinksFiltered = [item for item in allPageItemLinks if self.config.filterLinkKeep(item)]
        # Gather items async
        allItemData = await self.getAllItemDataFromLinks( pageItemLinksFiltered, 1, lock)

        return allItemData
    


# python3 main.py Avigdor Stematsky
