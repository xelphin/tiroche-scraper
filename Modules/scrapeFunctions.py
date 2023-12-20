import re

def getFirstNonNumericChar(str):
    for char in str:
        if char not in ['-', '.', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return char

    return ""

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

# Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
# returns the text of the information on the item
def getItemText(itemPage):
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
def getItemEstimatedPrice(itemPage):
    textElem =  itemPage.find(class_="single-lot__estimate")
    if textElem is None:
        return ""
    textElem =  textElem.find('strong')
    if textElem is None:
        return ""
    text = textElem.get_text()
    textArr = text.split('-')
    estimateData = {
        "low-estimate": "",
        "high-estimate": "",
        "currency": ""
    }

    estimateData["currency"] = getFirstNonNumericChar(text)
    if (len(textArr) == 2):
        estimateData["low-estimate"] = re.sub(r'[^0-9.]', '', textArr[0])
        estimateData["high-estimate"] = re.sub(r'[^0-9.]', '', textArr[1])
    elif (len(textArr) == 1):
        estimateData["high-estimate"] = re.sub(r'[^0-9.]', '', textArr[0])
    
    return estimateData


# Given itemPage (soup of website like: https://www.tiroche.co.il/auction/158-en/lot-289-marc-chagall-2/)
# extracts from the paragraph (text) found the values: innacurate extraction!
# EXTRACT FROM ITEM TEXT THE VALUES

def dimensionsSplitter(dim):
    if ('×' in dim):
        return dim.split('×')
    if ('X' in dim):
        return dim.split('X')
    if ('/' in dim):
        return dim.split('/')
    return ""

def extractFromItemTextTheValues_dimensiones(dim):
    dimensions = {
        "height": "",
        "width": "",
        "units": ""
    }
    dimSepArr = dimensionsSplitter(dim)
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

def extractFromItemTextTheValues_year(text):
    match = re.search(r'\b\d{4}\b', text) # first 4-digit number that appears
    if match:
        return match.group()
    return ""

def cleanupText(text):
    text = text.replace('\n', ',') # Replace '\n' with comma
    text = re.sub(r',\s*,', ',', text) # Replace consecutive commas with a single comma
    if text.endswith('.'):
        text = text[:-1]
    return text

def extractFromItemTextTheValues(text):
    # Assumes text appears as "Title, type, 00×00 units . signed/unsigned" for it to work properly
    text = cleanupText(text)
    pointSepArr = text.rsplit('.', 1) # Splits with the last '.' that appears
    if (len(pointSepArr) == 0):
        return ""
    commaSepArr = pointSepArr[0].split(',')
    textValues = {
        "guessed-year": "",
        "guessed-signed": "",
        "guessed-title": "",
        "guessed-paintingType": "",
        "guessed-height": "",
        "guessed-width": "",
        "guessed-units": "",
    }

    textValues["guessed-year"] = extractFromItemTextTheValues_year(text)
    if (len(pointSepArr) > 1):
        textValues["guessed-signed"] = pointSepArr[1]
    if (len(commaSepArr) > 0):
        textValues["guessed-title"] = ''.join(commaSepArr[:-2])
    if (len(commaSepArr) > 1):
        textValues["guessed-paintingType"] = commaSepArr[-2]
    if (len(commaSepArr) > 2):
        dimensions = extractFromItemTextTheValues_dimensiones(commaSepArr[-1])
        textValues["guessed-height"] = dimensions["height"]
        textValues["guessed-width"] = dimensions["width"]
        textValues["guessed-units"] = dimensions["units"]

    return textValues









