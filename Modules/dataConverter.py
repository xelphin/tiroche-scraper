# pip3 install pandas
import pandas as pd

# List of dictionaries
# [
#   {'websiteLink': '...', 'imgLink': '...', ...},
#   {'websiteLink': '...', 'imgLink': '...', ...} 
# ]

def getDictKeys(listDict):
    if listDict[0]:
        return list(listDict[0].keys())
    return []

# json -> csv
def listOfDictToCsv(listDict, path):
    keys = getDictKeys(listDict)
    csv = []
    for item in listDict:
        itemArr = []
        for key in keys:
            itemArr.append(item[key])
        csv.append(itemArr)
    df = pd.DataFrame(csv, columns=keys)
    df.to_csv(path, index=False)
    return df