# Tiroche Scraper
Web scrapes "Tiroche" website given a valid (logged) artist's name

## Requirements

```
$ pip install .
```
Installs requirements ('requests', 'beautifulsoup4', 'pandas', 'aiohttp')

## Run

Example if you want to search for artist "Marc Chagall"
```
$ python3 main.py Marc Chagall
```

In `./Outputs/data.csv` you'll have the data as a csv file

## Config

In `./Config/config.json` you can change whether or not you want to have images downloaded and whether or not you want to ignore certain links

### Ignoring certain links

Add to `./Config/ignoreCertainPaintingPageLinks.txt` the painting page links you want to ignore

The `./Config/ignoreCertainImageLinks.txt`gets updated with the painting's link from these pages

If you already calculated (ran the program with the links you put in `./Config/ignoreCertainPaintingPageLinks.txt`) then
you can write `true` in `ignoreCertainImageLinksAlreadyUpdated` in the `./Config/config.json` file.

## Notice
Because "Tircohe" doesn't have a consistent frame for how it writes out: title, year, painting type, dimensions and signed status, 
the program only guesses these values. However, the full text given can be found in "info"