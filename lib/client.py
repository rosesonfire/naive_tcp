from abc import ABCMeta, abstractmethod
from threading import Thread
import socket


class ClientProcessorThread(Thread):
    __metaclass__ = ABCMeta

    def __init__(self, server_host=None, server_port=None):
        super(ClientProcessorThread, self).__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setblocking(1)

    # server is not responsible for re-establishing connection if connection fails. Client is suppose to do that.

    @abstractmethod
    def process(self):
        pass

    def ensure_connection(self):
        if not self.client.is_alive():
            print 'client side connection lost'

    def run(self):
        self.client.connect((self.server_host, self.server_port))
        self.process()


class Client:
    __metaclass__ = ABCMeta

    def __init__(
            self,
            server_host=None,
            server_port=None,
            processor_thread_class=None):

        client_processor_thread_args = self.get_client_processor_thread_args()
        client_processor_thread_kwargs = self.get_client_processor_thread_kwargs()
        client_processor_thread_kwargs.update({
            "server_host": server_host,
            "server_port": server_port})
        self.processor_thread = processor_thread_class(*client_processor_thread_args, **client_processor_thread_kwargs)
        # self.processor_thread = processor_thread_class(server_host, server_port)

    def start(self):
        self.processor_thread.start()
        self.processor_thread.join()

    @abstractmethod
    def get_client_processor_thread_args(self):
        pass

    @abstractmethod
    def get_client_processor_thread_kwargs(self):
        pass
