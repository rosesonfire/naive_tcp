from abc import ABCMeta, abstractmethod
from threading import Thread
from Queue import Queue
import socket


class ServerProcessorThread(Thread):

    def __init__(self, client=None, assigned_work=None):
        super(ServerProcessorThread, self).__init__()
        self.client = client
        self.assigned_work = assigned_work

    # server is not responsible for re-establishing connection if connection fails. Client is suppose to do that.

    @abstractmethod
    def run(self):
        pass


class ServiceThread(Thread):
    __metaclass__ = ABCMeta

    def __init__(self, thread_id=None, client=None, msg_queue=None, assigned_work=None, processor_thread_class=None):
        super(ServiceThread, self).__init__()
        self.thread_id = thread_id
        self.msg_queue = msg_queue
        processor_thread_args = self.get_processor_thread_args()
        processor_thread_kwargs = self.get_processor_thread_kwargs()
        processor_thread_kwargs.update({
            "client": client,
            "assigned_work": assigned_work})
        self.processor_thread = processor_thread_class(*processor_thread_args, **processor_thread_kwargs)
        self.processor_thread.start()

    @abstractmethod
    def get_processor_thread_args(self):
        pass

    @abstractmethod
    def get_processor_thread_kwargs(self):
        pass

    @abstractmethod
    def handle_msg(self, msg):
        pass

    def check_for_msg(self):
        if not self.msg_queue.empty():
            self.handle_msg(self.msg_queue.get())

    def run(self):
        while True:
            if not self.processor_thread.is_alive():
                break
            self.check_for_msg()


class ServiceController:
    __metaclass__ = ABCMeta

    def __init__(self, service_thread_class=None):
        self.service_thread_class = service_thread_class
        self.active_threads = {}

    @abstractmethod
    def get_new_service_id(self):
        pass

    @abstractmethod
    def get_new_work(self):
        pass

    @abstractmethod
    def get_service_thread_args(self):
        pass

    @abstractmethod
    def get_service_thread_kwargs(self):
        pass

    def create_new_service_thread(self, client=None, processor_thread_class=None):
        thread_id = self.get_new_service_id()
        msg_queue = Queue()
        assigned_work = self.get_new_work()
        if (self.active_threads.get(thread_id, None) is not None) and (self.active_threads[thread_id].is_alive()):
            raise Exception("Service by this id is already running ! " + str(thread_id))
        service_thread_args = self.get_service_thread_args()
        service_thread_kwargs = self.get_service_thread_kwargs()
        service_thread_kwargs.update({
            "thread_id": thread_id,
            "client": client,
            "msg_queue": msg_queue,
            "assigned_work": assigned_work,
            "processor_thread_class": processor_thread_class})
        self.active_threads[thread_id] = self.service_thread_class(*service_thread_args, **service_thread_kwargs)
        self.active_threads[thread_id].start()


class Server:
    __metaclass__ = ABCMeta

    def __init__(
            self,
            host=None,
            port=None,
            max_queued_connections=None,
            service_controller_class=None,
            service_thread_class=None,
            processor_thread_class=None):

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.setblocking(0)
        self.max_queued_connections = max_queued_connections
        service_controller_args = self.get_service_controller_args()
        service_controller_kwargs = self.get_service_controller_kwargs()
        service_controller_kwargs.update({"service_thread_class": service_thread_class})
        self.service_controller = service_controller_class(*service_controller_args, **service_controller_kwargs)
        self.processor_thread_class = processor_thread_class

    @abstractmethod
    def server_work(self):
        pass

    @abstractmethod
    def get_service_controller_args(self):
        pass

    @abstractmethod
    def get_service_controller_kwargs(self):
        pass

    def start(self):
        self.server.listen(self.max_queued_connections)
        while True:
            try:
                client, addr = self.server.accept()
                client.setblocking(0)
                self.service_controller.create_new_service_thread(
                    client=client,
                    processor_thread_class=self.processor_thread_class)
            except socket.error:
                pass
            self.server_work()

