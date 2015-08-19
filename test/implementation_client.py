from lib.client import Client, ClientProcessorThread
import json
import socket


class MyClientProcessThread(ClientProcessorThread):

    def __init__(self, server_host=None, server_port=None):
        super(MyClientProcessThread, self).__init__(server_host=server_host, server_port=server_port)

    @staticmethod
    def is_prime(n):
        n = abs(n)
        if n == 0 or n == 1:
            return False
        for I in range(2, n-1):
            if n % I == 0:
                return False
        return True

    def process(self):
        primes = []
        self.client.setblocking(1)
        self.client.send(json.dumps({"request": "give_me_work"}))
        work = json.loads(self.client.recv(1025))
        starting_integer = work['start']
        ending_integer = work['end']
        for I in range(starting_integer, ending_integer):
            if self.is_prime(I):
                primes.append(I)
        self.client.send(json.dumps({"request": "take_my_primes", "primes": primes}))
        print "client's work done!", json.dumps(primes)


if __name__ == '__main__':
    client = Client(
        server_host=socket.gethostname(),
        server_port=1270,
        processor_thread_class=MyClientProcessThread)
    client.start()

