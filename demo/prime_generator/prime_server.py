import json
import sys
from datetime import datetime

from naivetcp.server import Server, ServiceController, ServiceThread, ServerProcessorThread
import meta


class MyServerProcessThread(ServerProcessorThread):

    def __init__(self, prime_segment=None, thread_id=None, client=None, assigned_work=None):
        self.prime_segment = prime_segment
        self.myWork = assigned_work
        super(MyServerProcessThread, self).__init__(thread_id=thread_id, client=client, assigned_work=assigned_work)

    def run(self):
        self.client.setblocking(1)
        while True:
            request = json.loads(self.client.recv(1024))
            if request['request'] == 'give_me_work':
                self.client.send(json.dumps(self.assigned_work))
                if 'error' in self.assigned_work:
                    break
            elif request['request'] == 'take_my_primes':
                self.prime_segment['primes'] = request['primes']
                break
        self.client.close()


class MyServiceThread(ServiceThread):

    def __init__(
            self,
            prime_segment=None,
            thread_id=None,
            client=None,
            msg_queue=None,
            assigned_work=None,
            processor_thread_class=None):
        self.prime_segment = prime_segment
        super(MyServiceThread, self).__init__(
            thread_id=thread_id,
            client=client,
            msg_queue=msg_queue,
            assigned_work=assigned_work,
            processor_thread_class=processor_thread_class)

    def get_processor_thread_args(self):
        return []

    def get_processor_thread_kwargs(self):
        return {"prime_segment": self.prime_segment}

    def handle_msg(self, msg):
        print msg


class MyServiceController(ServiceController):
    def __init__(self, prime_segments=None, service_thread_class=None):
        self.prime_segments = prime_segments
        self.current_id = 1
        self.latest_prime_segment_given = None
        super(MyServiceController, self).__init__(service_thread_class=service_thread_class)

    def get_new_service_id(self):
        self.current_id += 1
        return self.current_id - 1

    def get_new_work(self):
        for prime_segment in self.prime_segments:
            # if prime_segment['primes'] is None:
            if not prime_segment['assigned']:
                prime_segment['assigned'] = True
                self.latest_prime_segment_given = prime_segment
                return {"start": prime_segment['start'], "end": prime_segment['end']}
        return {"error": "No undone work to give !"}

    def get_service_thread_args(self):
        return []

    def get_service_thread_kwargs(self):
        return {"prime_segment": self.latest_prime_segment_given}


class MyServer(Server):
    def __init__(
            self,
            all_primes=None,
            starting_integer=None,
            ending_integer=None,
            increment=None,
            host=None,
            port=None,
            max_queued_connections=None,
            service_controller_class=None,
            service_thread_class=None,
            processor_thread_class=None):

        self.starting_time = None
        self.all_primes = all_primes
        self.prime_segments = []
        i = starting_integer
        while True:
            if i > ending_integer:
                break
            if i+increment > ending_integer:
                self.prime_segments.append({"start": i, "end": ending_integer, "primes": None, "assigned": False})
            else:
                self.prime_segments.append({"start": i, "end": i+increment, "primes": None, "assigned": False})
            i += increment

        super(MyServer, self).__init__(
            host=host,
            port=port,
            max_queued_connections=max_queued_connections,
            service_controller_class=service_controller_class,
            service_thread_class=service_thread_class,
            processor_thread_class=processor_thread_class)

    def start(self):
        self.starting_time = datetime.now()
        super(MyServer, self).start()

    def server_work(self):
        for prime_segment in self.prime_segments:
            if prime_segment['primes'] is None:
                return
        all_primes = []
        for prime_segment in self.prime_segments:
            all_primes.extend(prime_segment['primes'])
        print json.dumps(all_primes)
        time_taken = datetime.now() - self.starting_time
        print "\n\ntime taken", time_taken
        sys.exit()

    def get_service_controller_args(self):
        return []

    def get_service_controller_kwargs(self):
        return {"prime_segments": self.prime_segments}


if __name__ == '__main__':
    main_primes = []
    server = MyServer(
        all_primes=main_primes,
        starting_integer=meta.starting_integer,
        ending_integer=meta.ending_integer,
        increment=meta.increment,
        host=meta.host,
        port=meta.port,
        max_queued_connections=5,
        service_controller_class=MyServiceController,
        service_thread_class=MyServiceThread,
        processor_thread_class=MyServerProcessThread)
    server.start()
