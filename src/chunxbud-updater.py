import socketserver
from request import RequestHandler

address = ('', 6684)

server = socketserver.TCPServer(address, RequestHandler)
server.serve_forever()