import os

def load_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)