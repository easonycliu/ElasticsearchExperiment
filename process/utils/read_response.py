import sys
sys.path.append('')

from utils.file_operation import open_file

def read_response(file, method):
    f = open_file(file)
    data = []
    for line in f:
        data.append(method(line))
    f.close()
    return data
