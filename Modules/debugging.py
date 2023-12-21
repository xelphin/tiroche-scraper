def printTextToFile(text, file_path):
    with open(file_path, 'w') as file:
        file.write(text)

def appendTextToFile(text, file_path):
    with open(file_path, 'a') as file:
        file.write(text + "\n")

def clearFile(file_path):
    try:
        with open(file_path, 'w') as file:
            file.write("")
            pass  # Open the file and do nothing
    except FileNotFoundError:
        pass  # File doesn't exist, so nothing to clear