from wsgiref.simple_server import make_server

def req_handler(environ, start_response):
	print("Enter req_handler") # TODO

class Server:
	def __init__(self, host, port):
		self.httpd = make_server(host, port, req_handler)
		print("Serving on port {0}".format(port))
	
	def start(self):
		self.httpd.serve_forever()
