# ./Modules/fetch.py

# pip3 install requests
import requests
import aiohttp
import time
from selenium import webdriver
from chromedriver_py import binary_path

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

class RequestFailedError(Exception):
    """Exception raised when the HTTP request fails with a non-success status code."""
    pass

def getPageOfUrl(url):
    response = requests.get(url)
    # TODO: like getPageOfUrl_useHeaders, check exceptions
    return response

def getPageOfUrl_useHeaders(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            else:
                print(f"Page couldn't be retrieved: {response.status_code}")
                raise RequestFailedError
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            raise RequestFailedError

async def getPageOfUrl_async(session, url):
    try:
        async with session.get(url) as response:
            return await response.read()
    except Exception as e:
        # Handle the exception, you can print it for debugging purposes
        print(f"An error occurred when getting url {url}: {e}")
        return None

def getSoup(response):
    if response.status_code == 200:
        content = response.content
    return BeautifulSoup(content, 'html.parser')

def getSoup_forAsync(response):
    if response.status == 200:
        content = response.content
        return BeautifulSoup(content, 'html.parser')
    else:
        # TODO: Handle Exception
        return None

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
        

# Scroll through page 
def scrollThroughPageAndGetSoup(url, wait_time_scroll):
    # Function to scroll down the page
    def scroll_down(driver):
        # Get current page height
        current_position = driver.execute_script("return window.pageYOffset;")
        # Execute JavaScript to scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for some time to allow content to load
        time.sleep(wait_time_scroll)
        # Get new page height
        new_position = driver.execute_script("return window.pageYOffset;")
        # Return if should continue scrolling
        return current_position != new_position

    # Setup Chrome WebDriver service using chromedriver-py binary_path
    print("Setup Chrome WebDriver service...")
    try: 
        service = webdriver.chrome.service.Service(binary_path)

        # Start headless Chrome browser
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)

    except Exception as e:
        print(f"Error in setting up chrome web driver {e}")
        print("Note: You need 'Chrome' web browser to run this program")
        print("Make sure you have updated Chrome version: ")
        print("$ sudo apt-get update")
        print("$ sudo apt-get --only-upgrade install google-chrome-stable")

    # Load the page in the browser
    driver.get(url)

    # Scroll down multiple times to load additional content
    continue_scrolling = True
    while continue_scrolling:  # You can adjust the number of times to scroll down
        print("Scrolling down...")
        continue_scrolling = scroll_down(driver)
    print("Gathered all paintings that could be accessed within a reasonable time and don't require sign in")

    # Get the final HTML content after scrolling
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Create a Beautiful Soup object
    soup = BeautifulSoup(html_content, "html.parser")
    return soup

