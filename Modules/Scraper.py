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
    
    def extractFromItemTextTheValues(self, text):
        return ""
    
    def getItemEstimatedPrice(self, itemPage):
        return ""
    
    def getItemData(self, itemLink):
        # TODO: then have it be the one getting filled
        itemData = {}
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
        itemData.update(self.extractFromItemTextTheValues(itemInfo)) # fix this so its generic here
        itemData.update(self.getItemEstimatedPrice(soup))

        return itemData