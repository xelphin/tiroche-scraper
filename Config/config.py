import json
import os
import requests

# NOTE: Called from ../tiroche-scraper.py , so that's why the paths are written as they are

configPath = "./Config/config.json"

def removeJpgImages(folderPath):
    # (Asked chatGPT lol)
    if os.path.exists(folderPath):
        # Iterate over all files in the folder
        for item in os.listdir(folderPath):
            itemPath = os.path.join(folderPath, item)

            # Check if it's a file and has a ".jpg" or ".jpeg" extension
            if os.path.isfile(itemPath) and item.lower().endswith(('.jpg', '.jpeg')):
                os.remove(itemPath)
                print(f"Removed: {itemPath}")

        print(f"All JPG images removed from '{folderPath}'.")
    else:
        print(f"Folder '{folderPath}' does not exist.")

def downloadImage(url, folderPath, fileName):
    # (Asked chatGPT lol)
    os.makedirs(folderPath, exist_ok=True) # Create folder if needed
    filePath = os.path.join(folderPath, fileName) # Combine the folder path and file name to get the full file path
    response = requests.get(url) # Send an HTTP request to the URL

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the file in binary write mode and write the content
        with open(filePath, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {filePath}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

def getConfig():
    with open(configPath, 'r') as file:
        return json.load(file)

def downloadImages(allItemData, downloadPath, deleteOldImages):
    if (deleteOldImages):
        removeJpgImages(downloadPath) # clear what was in the images folder before
    count = 0
    for item in allItemData:
        downloadImage(item["imgLink"], downloadPath, item['id']+".jpg")
        count+=1

def applyConfigFromAllItems(allItemData):
    config = getConfig()
    if (config["downloadImages"]):
        downloadImages(allItemData, config["pathToImagesPrinted"], config["deleteOldImages"])