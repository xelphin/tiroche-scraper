# HELPER FUNCTIONS

# "Marc Chagall" -> "marc+chagall"
def strToQueryStr(str):
  queryStr = ""
  words = str.split()
  for i in range(len(words)):
    cleanWord = words[i].strip().lower()
    queryStr += cleanWord
    if (i != len(words)-1):
      queryStr += "-"
  
  return  queryStr

def printSeparatingLines():
  print("---------------------------------------")
  print("---------------------------------------")