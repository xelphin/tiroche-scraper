# Tiroche Scraper
Web scrapes "Tiroche" website given a valid (logged) artist's name

## Requirements

```
$ pip install .
```
Installs requirements ('requests', 'beautifulsoup4', 'pandas')

## Run

Example if you want to search for artist "Arie Aroch"
```
$ python3 tiroche-scraper.py Arie Aroch
```

In `./Outputs/data.csv` you'll have the data as a csv file

## Config

In `./Config/config.json` you can change whether or not you want to have images downloaded and whether or not you want to ignore certain links

Add to `./Config/ignoreLinks.txt` the links you want to ignore

#### Ignore Links (sophisticated ignore)

Occassionaly, the same webpage (painting webpage) has various links, so when you add a link to `ignoreLinks.txt`, the program extracts the image (painting) from the webpage link and adds it to `ignoreLinksImages.txt` so that we make sure to ignore alternate links with the same painting.

## Notice
Because "Tircohe" doesn't have a consistent frame for how it writes out: title, year, painting type, dimensions and signed status, 
the program only guesses these values. However, the full text given can be found in "info"