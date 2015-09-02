from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
import sys

class InvalidRequest(Exception):
	pass

class HandlerClass(SimpleHTTPRequestHandler):
	# Override since the implementation in base class will send extra headers
	def send_response(self, code):
		if code in self.responses:
			message = self.responses[code][0]
		else:
			message = ""
		self.wfile.write(("%s %d %s\r\n" % (self.protocol_version, code, message))
			.encode("ASCII", "strict"))

	def forward_response(self, resp):
		self.send_response(resp.status)
		for h in resp.headers:
			self.send_header(h, resp.headers[h])
		self.end_headers()
		self.wfile.write(resp.read())

	# TODO: just call baidu.com right now
	def forward_request(self):
		conn = HTTPConnection("www.baidu.com", 80)
		conn.request("GET", "/")
		resp = conn.getresponse()

		self.forward_response(resp)

	def handle_one_request(self):
		self.raw_requestline = self.rfile.readline()
		if not self.raw_requestline:
			return
		if not self.parse_request():
			raise InvalidRequest("Fail to parse the http request")

		print("Handle req: {0}".format(self.raw_requestline))

		self.forward_request()
		self.close_connection = 1 # mandate to close connection right now

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
