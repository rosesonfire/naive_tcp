from naivetcp.server import Server, ServiceController, ServiceThread, ServerProcessorThread
import json
import meta
import socket
from datetime import datetime


class MyServerProcessThread(ServerProcessorThread):

    def __init__(self, chat_msg_queue=None, thread_id=None, client=None, assigned_work=None):
        self.chat_msg_queue = chat_msg_queue
        self.myWork = assigned_work
        super(MyServerProcessThread, self).__init__(thread_id=thread_id, client=client, assigned_work=assigned_work)

    def run(self):
        self.client.setblocking(1)
        self.client.send(json.dumps({"client_id": self.thread_id}))
        acknowledged_thread_id = json.loads(self.client.recv(1025))["received_client_id"]
        if str(acknowledged_thread_id) is not str(self.thread_id):
            raise Exception('Client ID error!')
        self.client.setblocking(0)
        while True:
            try:
                msgs_in = json.loads('[' + self.client.recv(1024)[0:-1] + ']')
                for msg_in in msgs_in:
                    self.chat_msg_queue.append(
                        {
                            "msg": msg_in['msg'],
                            "author": "client "+str(self.thread_id),
                            "time": datetime.now(),
                            "seen_by": []
                        })
            except socket.error:
                pass

            try:
                for msg_obj in self.chat_msg_queue:
                    if self.thread_id not in msg_obj["seen_by"]:
                        msg = msg_obj['msg']
                        author = msg_obj['author']
                        time = msg_obj['time']
                        self.client.send(json.dumps({"msg": msg, "author": author, "time": str(time)}) + ',')
                        msg_obj["seen_by"].append(self.thread_id)
            except socket.error:
                pass
        self.client.close()


class MyServiceThread(ServiceThread):

    def __init__(
            self,
            chat_msg_queue=None,
            thread_id=None,
            client=None,
            msg_queue=None,
            assigned_work=None,
            processor_thread_class=None):
        self.chat_msg_queue = chat_msg_queue
        super(MyServiceThread, self).__init__(
            thread_id=thread_id,
            client=client,
            msg_queue=msg_queue,
            assigned_work=assigned_work,
            processor_thread_class=processor_thread_class)

    def get_processor_thread_args(self):
        return []

    def get_processor_thread_kwargs(self):
        return {"chat_msg_queue": self.chat_msg_queue}

    def handle_msg(self, msg):
        print msg


class MyServiceController(ServiceController):
    def __init__(self, chat_msg_queue=None, service_thread_class=None):
        self.chat_msg_queue = chat_msg_queue
        self.current_id = 1
        super(MyServiceController, self).__init__(service_thread_class=service_thread_class)

    def get_new_service_id(self):
        self.current_id += 1
        return self.current_id - 1

    def get_new_work(self):
        pass

    def get_service_thread_args(self):
        return []

    def get_service_thread_kwargs(self):
        return {"chat_msg_queue": self.chat_msg_queue}


class MyServer(Server):
    def __init__(
            self,
            chat_msg_queue=None,
            host=None,
            port=None,
            max_queued_connections=None,
            service_controller_class=None,
            service_thread_class=None,
            processor_thread_class=None):

        self.chat_msg_queue = chat_msg_queue

        super(MyServer, self).__init__(
            host=host,
            port=port,
            max_queued_connections=max_queued_connections,
            service_controller_class=service_controller_class,
            service_thread_class=service_thread_class,
            processor_thread_class=processor_thread_class)

    def server_work(self):
        pass

    def get_service_controller_args(self):
        return []

    def get_service_controller_kwargs(self):
        return {"chat_msg_queue": self.chat_msg_queue}


if __name__ == '__main__':
    main_chat_msg_queue = []
    server = MyServer(
        chat_msg_queue=main_chat_msg_queue,
        host=meta.host,
        port=meta.port,
        max_queued_connections=5,
        service_controller_class=MyServiceController,
        service_thread_class=MyServiceThread,
        processor_thread_class=MyServerProcessThread)
    server.start()
