from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
from socketserver import ThreadingMixIn
from tunnel import Tunnel
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
			# the chunk encoding has already been processed by the library, 
			# don't send it to client
			if h[0].lower() == "transfer-encoding" and h[1].lower() == "chunked":
				continue
			self.send_header(h[0], h[1])
		self.end_headers()
		respbody = resp.read()
		self.wfile.write(respbody)

	# XXX just remove the header and wait for client to timeout right now	
	def handleExpect100(self, headers):
		if headers.get("Expect") and headers["Expect"].lower() == "100-continue":
			del headers["Expect"]

	def forward_request(self):
		uri = self.path
		cmd = self.command

		if cmd == "CONNECT":
			self.send_response(200)
			# in Python 3.4, end_headers need access _headers_buffer. Invoke send_header
			# will make sure the field is created
			self.send_header("Date", self.date_time_string()) 
			self.end_headers()
			return Tunnel(self.connection, uri).handle()

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

		if cmd not in ["GET", "POST"]:
			raise NotSupportedError("http method {0} not supported".format(cmd))

		headers = {name: self.headers[name] for name in self.headers }
		if headers.get("Content-Length"):
			cl = int(headers["Content-Length"])
		else:
			cl = None
		body = None

		# get body for post
		if cmd in ["POST"]:
			self.handleExpect100(headers)
			if cl:
				body = self.rfile.read(cl)
			else:
				body = self.rfile.read()
			print("body is [{0}]".format(body))

		if "Proxy-Connection" in headers:
			del headers["Proxy-Connection"]
		conn.request(cmd, resource, body, headers)

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

class ThreadServer(ThreadingMixIn, HTTPServer):
	pass

class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
	
	def start(self):
		httpd = ThreadServer((self.host, self.port), HandlerClass)
		print("Serving on port {0}".format(self.port))

		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			print("\nKeyboard interrupt received, exiting.")
			httpd.server_close()
			sys.exit(0)
