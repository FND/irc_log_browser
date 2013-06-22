import os

from urllib import quote as url_encode


ROOT_PATH = "./sample_data" # TODO: configurable


def app(environ, start_response):
    """
    routing dispatch
    """
    path = environ.get("PATH_INFO", "")

    route = not_found
    if path == "/":
        route = root
    elif path.startswith("/#"):
        # either /#<channel> or /#<channel>/<conversation>
        route = conversation if "/" in path[1:] else channel

    return route(environ, start_response)


def root(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])
    yield "<ul>"
    for channel in os.listdir(ROOT_PATH):
        uri = "/%s" % url_encode(channel)
        yield '<li><a href="%s">%s</a></li>' % (uri, channel)
    yield "</ul>"


def channel(environ, start_response):
    channel = environ.get("PATH_INFO", "").lstrip("/")
    dirpath = os.path.join(ROOT_PATH, channel) # TODO: encode special chars (e.g. slashes)

    try:
        entries = os.listdir(dirpath)
    except (OSError, IOError):
        start_response("404 Not Found", [])
        yield "Not Found"
    else:
        start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])
        yield "<ul>"
        for entry in entries:
            uri = "/%s/%s" % (url_encode(channel), url_encode(entry))
            yield '<li><a href="%s">%s</a></li>' % (uri, entry)
        yield "</ul>"


def conversation(environ, start_response):
    channel, conversation = environ.get("PATH_INFO", "").lstrip("/").split("/")
    filepath = os.path.join(ROOT_PATH, channel, conversation) # TODO: encode special chars (e.g. slashes)

    try:
        fh = open(filepath)
    except (OSError, IOError):
        start_response("404 Not Found", [])
        yield "Not Found"
    else:
        start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])
        yield "<ol>"
        for i, line in enumerate(fh):
            i += 1
            yield '<li><a href="#l%s" name="l%s">%s</a></li>' % (i, i, line)
        yield "</ol>"


def not_found(environ, start_response):
        start_response("404 Not Found", [])
        return ["Not Found"]
