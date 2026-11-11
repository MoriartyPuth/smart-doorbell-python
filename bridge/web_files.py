# The web app's files (webapp/ folder on the board) and the address of each.
# To add a file: put it in webapp/, upload it, and add a line here.

WEBAPP_FOLDER = "webapp/"

# address -> (file name, content type the browser needs)
FILES = {
    "/": ("index.html", "text/html"),
    "/style.css": ("style.css", "text/css"),
    "/app.js": ("app.js", "application/javascript"),
}


def find(path):
    """Returns (file path on the board, content type) for an address, or None."""
    entry = FILES.get(path)
    if entry is None:
        return None
    return WEBAPP_FOLDER + entry[0], entry[1]
