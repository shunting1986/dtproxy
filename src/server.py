from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
import sys

class InvalidRequest(Exception):
	pass

class NotSupportedError(Exception):
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

		for h in resp.getheaders():
			self.send_header(h[0], h[1])
		self.end_headers()
		self.wfile.write(resp.read())

	def forward_request(self):
		uri = self.path
		if uri.startswith("https://"):
			raise NotSupportedError("https not supported yet")	
		elif uri.startswith("http://"):
			uri = uri[len("http://") :]
		else:
			raise InvalidRequest("Invalid uri for proxy: {0}".format(uri))

		start_ind = uri.find("/")
		if start_ind == -1:
			start_ind = uri.find("?")

		if start_ind == -1:
			addr = uri
			resource = "/"
		else:
			addr = uri[:start_ind]
			resource = uri[start_ind:]

		if not resource.startswith("/"):
			resource = "/" + resource

		conn = HTTPConnection(addr)
		cmd = self.command

		if cmd not in ["GET"]:
			raise NotSupportedError("http method {0} not supported".format(cmd))
		headers = {name: self.headers[name] for name in self.headers }

		del headers["Proxy-Connection"]
		# del headers["User-Agent"] # TODO fix the problem caused by user agent
		conn.request(cmd, resource, None, headers)

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
