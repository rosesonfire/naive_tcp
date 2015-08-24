# prime number generation using several clients

### How to run

From the directory

```
py_tcp_client_server_library/../
```

In a terminal, run the prime generator server

```
python -m py_tcp_client_server_library.demo.prime_generator.prime_server
```

Run the prime generator client several times in different terminals, each time opening a client

```
python -m py_tcp_client_server_library.demo.prime_generator.prime_client
```

###End result

The server will display all the primes between 1 and 1000. Each client instance will generate a portion of the primes and display them before sending the portion back to the server.

### How to change parameters
To change starting integer, ending integer or size of work block for each client, edit

```
py_tcp_client_server_library/demo/prime_generator/meta.py
```

### How to run in multiple computers
To change HOST or PORT, edit

```
py_tcp_client_server_library/demo/prime_generator/meta.py
```

