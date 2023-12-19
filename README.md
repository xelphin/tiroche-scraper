# Tiroche Scraper
Web scrapes "Tiroche" website given a valid (logged) artist's name

## Requirements

```
$ pip install .
```
Installs requirements ('requests', 'beautifulsoup4', 'pandas')

## Run

Example if you want to search for artist "Izhak Frenkel Frenel"
```
$ python3 tiroche-scraper.py Izhak Frenkel Frenel
```

### Notice
Because "Tircohe" doesn't have a consistent frame for how it writes out: title, year, painting type, dimensions and signed status, 
the program only guesses these values. However, the full text given can be found in "info"