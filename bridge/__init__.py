# Backend bridge: the web server that serves the web app (webapp/ folder) and its API.
#   http_server.py  reads requests and writes replies (knows nothing about the doorbell)
#   web_files.py    which web app file belongs to which address
#   web_bridge.py   login, the /api/... routes, and starting the server
