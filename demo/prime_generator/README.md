# prime number generation using several clients

### How to run

In a terminal, run the prime generator server

```
python prime_server.py
```

Run the prime generator client several times in different terminals, each time opening a client

```
python prime_client.py
```

###End result

The server will display all the primes between 1 and 1000, and show the total server running time. Each client instance will generate a portion of the primes and display them before sending the portion back to the server.

### How to change parameters
To change starting integer, ending integer or size of work block for each client, edit

```
meta.py
```

### How to run in multiple computers
To change HOST or PORT, edit

```
meta.py
```

