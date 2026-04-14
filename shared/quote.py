import urllib.parse

def quote(unqoted) -> str:
    return urllib.parse.quote(unqoted, safe='/=?&:')
