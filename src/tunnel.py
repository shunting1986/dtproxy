import socket
import select

# This is running inside a thread
class Tunnel:
	def __init__(self, client_sock, server_addr):
		self.client_sock = client_sock
		self.server_addr = server_addr

		comps = server_addr.split(":")
		if len(comps) != 2:
			raise ValueError("Invalid server address: {0}".format(server_addr))

		self.host = comps[0]
		self.port = int(comps[1])
	
	def client_to_server(self):
		return self.transfer(self.client_sock, self.server_sock)
	
	def server_to_client(self):
		return self.transfer(self.server_sock, self.client_sock)

	# when remoting end is closed, recv will return 0
	def transfer(self, from_sock, to_sock):
		data = from_sock.recv(4096)
		to_sock.sendall(data)
		return len(data)
	
	def handle(self):
		self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_sock.connect((self.host, self.port))

		while True:
			readable, writable, exceptional = select.select([self.client_sock, self.server_sock], [], [])
			assert readable
			assert not writable
			assert not exceptional

			tot = 0
			if self.client_sock in readable:
				tot += self.client_to_server()
			if self.server_sock in readable:
				tot += self.server_to_client()
			print("get readable for {0}, tot {1}".format(self.server_addr, tot)) # TODO
			
			if not tot:
				break
		print("Close connection to {0}".format(self.server_addr))

def tryout():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(("localhost", 8888))
	s.sendall(b"Hello")
	s.close()

if __name__ == "__main__":
	tryout()
