import re

# Custom filter method
def regex_replace(s, find, replace):
    return re.sub(find, replace, s)
