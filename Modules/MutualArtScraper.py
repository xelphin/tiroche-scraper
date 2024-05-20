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

WAIT_TIME_SCROLL = 3

class MutualArtScraper(Scraper):

    def __init__(self, artistName, allLinksPathName, allItemsPathName, dataCsvPathName, config):
        super().__init__(artistName, allLinksPathName, allItemsPathName, dataCsvPathName, config)
        

    def __getPageOfAllArtistsWithNameResults(self):
        name_arr = (self.artistName).split("-")
        if len(name_arr) == 0:
            raise ValueError("Artist name given is bad format: Empty or just '-'")
        # Create search query string
        search_str = name_arr[0]
        for word in name_arr[1:]:
            search_str += "%20"+word

        pageLink = f"https://www.mutualart.com/Results/search?q={search_str}"
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


    # -----------------
    # CATALOG FUNCTIONS
    # -----------------

    # -----------------------
    # ITEM SCRAPING FUNCTIONS
    # -----------------------
    def getItemImgLink(itemPage):
        return ""

    # -----------------------
    # GETTING LINKS FUNCTIONS
    # -----------------------

    # Get (scrape) data from item/painting link
    # Example for item/painting link: https://www.tiroche.co.il/auction/178-en/lot-507-128/
    async def getItemDataFromLink(self, session, link, lock, itemData_file, allPageItemData, catalogPageNum, itemCount):
        pass

    def getCatalogsItemLinks(self, catalogPage):
        pass

    # Collects all item/painting data from link and the data from the 'next' pages if there are
    async def getAllItemData(self, allItemData, lock):
        allCatalogPagesSoups = []
        link_to_artist_page = self.__getPageOfArtist()
        scrollThroughPageAndGetSoup(link_to_artist_page, WAIT_TIME_SCROLL)
        # TODO:gather paintings
        return allItemData
    


# python3 main.py Avigdor Stematsky
