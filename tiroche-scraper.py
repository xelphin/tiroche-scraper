# pip3 install requests
import requests

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

# pip3 install pandas
import pandas as pd

from Modules.fetch import getCatalogAtPageResponse, getPageOfUrl, getSoup
from Modules.helperFunctionsGeneral import strToQueryStr
from Modules.scrapeFunctions import getCatalogsItemLinks, getItemImgLink, getItemText
from Modules.debugging import printTextToFile, appendTextToFile, clearFile

# GLOBALS
artworks = []
userInput = "Marc Chagall"
artistName = strToQueryStr(userInput)

# PRIMARY FUNCTIONS
def getAllItemLinks(artistName) :
    stop = False
    count = 1
    itemLinks = []
    while (stop == False):
        response = getCatalogAtPageResponse(count, artistName)
        if (response.status_code != 200):
            return itemLinks
        soup = getSoup(response)
        pageItemLinks = getCatalogsItemLinks(soup)
        itemLinks.extend(pageItemLinks)
        count += 1
    return itemLinks # (won't get here)    

def getItemData(itemLink):
    itemData = {}
    response = getPageOfUrl(itemLink)
    if (response.status_code != 200):
        return ""
    soup = getSoup(response)

    itemData['imgLink'] = getItemImgLink(soup)
    itemInfo = getItemText(soup)
    itemData['info'] = itemInfo

    return itemData

def getAllItemData(allLinks):
    allItemData = []
    clearFile('item_data.txt')
    print("See ./item_data.txt to see the data being gathered")
    for link in allLinks:
        itemData = getItemData(link)
        allItemData.extend(itemData)
        appendTextToFile(str(itemData), 'item_data.txt')
    return allItemData


allItemLinks = getAllItemLinks(artistName)
printTextToFile(str(allItemLinks), "item_links.txt")
allItemData = getAllItemData(allItemLinks)

# REFERENCE
# for i in range(1,5):
#   url = f"https://books.toscrape.com/catalogue/page-{i}.html" # the 'f' at the starts makes the 'i' a variable
#   response = requests.get(url)
#   response = response.content
#   soup = BeautifulSoup(response, 'html.parser')
#   ol = soup.find('ol')
#   articles = ol.find_all('article', class_='product_pod')
#   for article in articles:
#     image = article.find('img')
#     title = image.attrs['alt']
#     starTag = article.find('p')
#     star = starTag['class'][1]
#     price = article.find('p', class_='price_color').text
#     price = float(price[1:])
#     books.append([title, star, price])
    

# df = pd.DataFrame(books, columns=['Title', 'Star Rating', 'Price'])
# df.to_csv('books.csv')


