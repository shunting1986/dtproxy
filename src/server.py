from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

class HandlerClass(SimpleHTTPRequestHandler):
	pass

class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
	
	def start(self):
		httpd = HTTPServer((self.host, self.port), HandlerClass)
		print("Serving on port {0}".format(self.port))

		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			print("\nKeyboard interrupt received, exiting.")
			httpd.server_close()
			sys.exit(0)

### WSGI implementation
# from wsgiref.simple_server import make_server
# 
# def req_handler(environ, start_response):
# 	cl = environ.get("CONTENT_LENGTH", None)
# 	for x in environ:
# 		print(x)
# 		print("\t{0}".format(environ[x]))
# 	
# 	if cl:
# 		body = environ["wsgi.input"].read(int(cl))
# 	else:
# 		body = environ["wsgi.input"].read()
# 	print("body:")
# 	print(body)
# 	print()
# 
# 	print("Enter req_handler") # TODO
# 
# class Server:
# 	def __init__(self, host, port):
# 		self.httpd = make_server(host, port, req_handler)
# 		print("Serving on port {0}".format(port))
# 	
# 	def start(self):
# 		self.httpd.serve_forever()
