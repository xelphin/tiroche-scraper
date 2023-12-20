# pip3 install requests
import requests

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

def getCatalogAtPageResponse(pageNum, queryStr):
    url = f"https://www.tiroche.co.il/paintings-authors/{queryStr}/page/{pageNum}/" # the 'f' at the starts makes the 'pageNum' a variable
    response = requests.get(url)
    return response

def getPageOfUrl(url):
    response = requests.get(url)
    return response

def getSoup(response):
    if response.status_code == 200:
        content = response.content
    return BeautifulSoup(content, 'html.parser')

# Get UID-4
def getUID4():
    url = "https://www.uuidgenerator.net/api/version4"

    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        return content
    return -1