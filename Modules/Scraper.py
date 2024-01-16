# ./Modules/Scraper.py

from .fetch import getUID4_async, getPageOfUrl_async, getSoupFromContent

# DON'T IMPORT CONFIG

class Scraper:

    # INIT
    def __init__(self, artistName, allLinksPathName, allItemsPathName, dataCsvPathName):
        self.artistName = artistName
        self.allLinksPathName = allLinksPathName
        self.allItemsPathName = allItemsPathName
        self.dataCsvPathName = dataCsvPathName

    def getCatalogAtPageResponse(self, pageNum):
        pass

    def getCatalogsItemLinks(self, catalogPage):
        pass
    
    def getArtistName(self, itemPage):
        return ""
    
    def getItemImgLink(self, itemPage):
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
    
    async def getItemData(self, itemLink, session):
        itemData = self.__itemCreator()
        content = await getPageOfUrl_async(session, itemLink)
        # if (response.status_code != 200):
        #     return ""
        soup = getSoupFromContent(content)

        itemData['id'] = await getUID4_async()
        itemData['artist'] = self.getArtistName(soup)
        itemData['websiteLink'] = itemLink
        itemData['imgLink'] = self.getItemImgLink(soup)
        itemInfo = self.getItemText(soup)
        itemData['info'] = itemInfo
        itemData = self.extractFromItemTextTheValues(itemInfo, itemData)
        itemData = self.getItemEstimatedPrice(soup, itemData)

        return itemData