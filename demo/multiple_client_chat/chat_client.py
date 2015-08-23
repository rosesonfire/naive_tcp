from ...lib.client import Client, ClientProcessorThread
import json
import socket
import meta
from threading import Thread
from Queue import Queue


class KeyBoardInputThread(Thread):
    def __init__(self, input_queue=None):
        self.input_queue = input_queue
        super(KeyBoardInputThread, self).__init__()

    def run(self):
        while True:
            msg_in = raw_input()
            self.input_queue.put(msg_in)


class MyClientProcessThread(ClientProcessorThread):

    def __init__(self, server_host=None, server_port=None):
        super(MyClientProcessThread, self).__init__(server_host=server_host, server_port=server_port)
        self.input_queue = Queue()
        self.client_id = None
        keyboard_input = KeyBoardInputThread(input_queue=self.input_queue)
        keyboard_input.start()

    def process(self):
        self.client.setblocking(1)
        self.client_id = json.loads(self.client.recv(1025))["client_id"]
        self.client.send(json.dumps({"received_client_id": self.client_id}))
        print 'CLIENT ID: ', self.client_id
        self.client.setblocking(0)
        while True:
            try:
                if not self.input_queue.empty():
                    out_msg = self.input_queue.get()
                    self.client.send(json.dumps({"msg": out_msg}) + ',')
                in_msgs = json.loads('[' + self.client.recv(1025)[0:-1] + ']')
                for msg_obj in in_msgs:
                    author = msg_obj['author']
                    time = msg_obj['time']
                    msg = msg_obj['msg']
                    print author, ' (' + time + '):', msg
            except socket.error:
                pass
        self.client.close()


class MyClient(Client):
    def __init__(self, server_host=None, server_port=None, processor_thread_class=None):
        super(MyClient, self).__init__(
            server_host=server_host,
            server_port=server_port,
            processor_thread_class=processor_thread_class)

    def get_client_processor_thread_args(self):
        return []

    def get_client_processor_thread_kwargs(self):
        return {}


if __name__ == '__main__':
    client = MyClient(
        server_host=meta.host,
        server_port=meta.port,
        processor_thread_class=MyClientProcessThread)
    client.start()

