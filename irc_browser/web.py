import os

from urllib import quote as url_encode
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs


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
    elif path == "/search":
        route = search

    return route(environ, start_response)


def root(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])
    yield "<ul>"
    for channel in os.listdir(ROOT_PATH):
        uri = "/%s" % url_encode(channel)
        yield '<li><a href="%s">%s</a></li>' % (uri, channel)
    yield "</ul>"


def search(environ, start_response):
    params = environ.get('QUERY_STRING', '')

    start_response("200 OK", [("Content-Type", "text/html; charset=UTF-8")])

    if not params:
        yield '<form method="GET">'
        yield '<input type="search" name="query">'
        yield '<input type="submit">'
        yield "</form>"
    else:
        query = parse_qs(params)["query"][0]

        # XXX: hard-codes directory hierarchy logic that doesn't belong here
        matches_by_channel = {}
        for channel in os.listdir(ROOT_PATH):
            for conversation in os.listdir(os.path.join(ROOT_PATH, channel)):
                filepath = os.path.join(ROOT_PATH, channel, conversation)
                matches = search_in_file(query, filepath)
                if matches:
                    matches_by_channel[channel] = matches_by_channel.get(channel, {}) # TODO: use defaultdict!?
                    matches_by_channel[channel][conversation] = matches

        if matches_by_channel:
            yield "<dl>"
            for channel in matches_by_channel:
                yield "<dt>%s</dt>" % channel
                for conversation in matches_by_channel[channel]:
                    for no, line in matches_by_channel[channel][conversation]:
                        uri = "/%s/%s#%s" % (url_encode(channel),
                                url_encode(conversation), no)
                        yield '<dd><a href="%s">#%s</a>: %s</dd>' % (uri, no, line)
            yield "</dl>"


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


def search_in_file(query, filepath):
    matches = []
    with open(filepath) as fh:
        for i, line in enumerate(fh):
            line = line.rstrip()
            if query in line:
                matches.append((i + 1, line))

    return matches
