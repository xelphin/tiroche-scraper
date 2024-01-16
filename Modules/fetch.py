# ./Modules/fetch.py

# pip3 install requests
import requests
import asyncio
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
def getUID4():
    url = "https://www.uuidgenerator.net/api/version4"

    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        # content = response.content
        return content
    return -1