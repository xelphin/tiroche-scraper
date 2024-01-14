from .fetch import getPageOfUrl, getSoup, getUID4

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
    
    def getItemData(self, itemLink):
        itemData = self.__itemCreator()
        response = getPageOfUrl(itemLink)
        if (response.status_code != 200):
            return ""
        soup = getSoup(response)

        itemData['id'] = getUID4()
        itemData['artist'] = self.getArtistName(soup)
        itemData['websiteLink'] = itemLink
        itemData['imgLink'] = self.getItemImgLink(soup)
        itemInfo = self.getItemText(soup)
        itemData['info'] = itemInfo
        itemData = self.extractFromItemTextTheValues(itemInfo, itemData)
        itemData = self.getItemEstimatedPrice(soup, itemData)

        return itemData