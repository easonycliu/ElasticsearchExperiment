def read_response(file, method):
    f = open(file, "r")
    data = []
    for line in f:
        data.append(method(line))
        
    return data
