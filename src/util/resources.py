import os
# Get the dir of this file
this_file = os.path.dirname(os.path.realpath(__file__))

def resource(name):
    path = os.path.join(this_file, "..", "..", "resources", name)
    text = open(path).read()
    return text

