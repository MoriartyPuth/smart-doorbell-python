# A very small HTTP/1.0 server toolkit: read one request, send one reply.
# It knows nothing about the doorbell; web_bridge.py decides what to answer.

MAX_BODY_BYTES = 512      # bigger request bodies are refused
_CHUNK = 512              # files are sent in pieces this big to save memory


class Request:
    def __init__(self, method, path, headers, body, too_big):
        self.method = method
        self.path = path
        self.headers = headers     # names in lower case, e.g. "authorization"
        self.body = body           # bytes
        self.too_big = too_big     # True if the body was over MAX_BODY_BYTES (and was not read)


async def read_request(reader):
    """Reads one request from a browser. Returns a Request, or None if it made no sense."""
    first = await reader.readline()
    parts = first.decode().split()
    if len(parts) < 2:
        return None
    method, path = parts[0], parts[1].split("?")[0]

    headers = {}
    while True:
        line = await reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        name, _, value = line.decode().partition(":")
        headers[name.strip().lower()] = value.strip()

    length = int(headers.get("content-length") or 0)
    body = b""
    too_big = length > MAX_BODY_BYTES
    while not too_big and len(body) < length:
        piece = await reader.read(length - len(body))
        if not piece:
            break
        body += piece
    return Request(method, path, headers, body, too_big)


async def send(writer, status, content_type, text, extra_headers=""):
    """Sends a whole reply. status is like "200 OK"; extra_headers end in \\r\\n."""
    data = text.encode() if isinstance(text, str) else text
    head = ("HTTP/1.0 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\n%s"
            "Connection: close\r\n\r\n") % (status, content_type, len(data), extra_headers)
    writer.write(head.encode())
    writer.write(data)
    await writer.drain()


async def send_file(writer, filename, content_type):
    """Sends a file from the board's storage, a piece at a time."""
    writer.write(("HTTP/1.0 200 OK\r\nContent-Type: %s\r\nCache-Control: no-cache\r\n"
                  "Connection: close\r\n\r\n" % content_type).encode())
    with open(filename, "rb") as f:
        while True:
            piece = f.read(_CHUNK)
            if not piece:
                break
            writer.write(piece)
            await writer.drain()
