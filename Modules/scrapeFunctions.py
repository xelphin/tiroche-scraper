# Given catalogPage (soup of website like: https://www.tiroche.co.il/paintings-authors/marc-chagall/)
# returns all the links to the items
def getCatalogsItemLinks(catalogPage):
    itemsLinks = []
    catalog =  catalogPage.find(id="catalog-section")

    itemDivs = catalog.find_all('div', recursive=False)

    for itemDiv in itemDivs:
        itemImgDiv = itemDiv.find('div', class_='lot-item__img')
        if itemImgDiv is not None:
            itemLinkElem =  itemImgDiv.find('a')
            itemsLinks.append(itemLinkElem.attrs['href'])

    return itemsLinks

# Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
# returns img link
def getItemImgLink(itemPage):
    imageDiv =  itemPage.find(id="wrpLotImages")
    imageElem =  imageDiv.find('a')
    imageLink = imageElem.attrs['href']
    if imageLink is not None:
        return imageLink
    return ""

def getItemText(itemPage):
    textDiv =  itemPage.find(class_="single-lot__body")
    if textDiv is None:
        return ""
    textElem =  textDiv.find('p')
    if textElem is None:
        return ""
    text = textElem.get_text()
    return text

def extractFromItemTextTheValues(text):
    # Assumes text appears as "Title, type, 00×00 units . signed/unsigned" for it to work properly
    pointSepArr = text.split('.')
    # TODO
