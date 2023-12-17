def printTextToFile(text, file_path):
    with open(file_path, 'w') as file:
        file.write(text)
    print(f"Content has been written to {file_path}")

def appendTextToFile(text, file_path):
    with open(file_path, 'a') as file:
        file.write(text + "\n")

def clearFile(file_path):
    with open(file_path, 'w') as file:
        file.write("")