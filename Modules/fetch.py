# ./Modules/fetch.py

# pip3 install requests
import requests
import aiohttp

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

def getPageOfUrl(url):
    response = requests.get(url)
    return response

async def getPageOfUrl_async(session, url):
    async with session.get(url) as response:
        return await response.read()

def getSoup(response):
    if response.status_code == 200:
        content = response.content
    return BeautifulSoup(content, 'html.parser')

def getSoupFromContent(content):
    # if response.status_code == 200:
    #     content = response.content
    return BeautifulSoup(content, 'html.parser')

# Get UID-4
async def getUID4_async():
    url = "https://www.uuidgenerator.net/api/version4"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                return content
            return -1