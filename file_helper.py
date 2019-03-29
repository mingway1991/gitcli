import os

def loadfile(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None

def writefile(path, content):
    with open(path, 'w') as f:
        f.write(content)