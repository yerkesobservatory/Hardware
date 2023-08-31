# ...
import sys
import socket
import selectors # .select() to handle multiple connections simultaneously
from libserver import Message # contains our message class
import traceback

sel = selectors.DefaultSelector() # selector object

# ...

def accept_wrapper(sock):
    conn, addr = sock.accept() # Should be ready to read
    print(f'Accepted connection from addr: {addr}')
    conn.setblocking(False) # put socket into non-blocking mode
    message = Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print(f'Listening on host: {host}, port: {port}')
lsock.setblocking(False) # calls made to this socket will no longer block
# can wait for events on >=1 socket and then read + write data when its ready
sel.register(lsock, selectors.EVENT_READ, data=None) # registering the object with lsock, want read events for listening socket

try:
    while True: #infinite loop
        events = sel.select(timeout=None) # returns list of tuples which contain key and mask
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f'Main: Error: Exception for {message.addr}:\n'
                        f'{traceback.format_exc()}'
                    )
                    message.close()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close() 