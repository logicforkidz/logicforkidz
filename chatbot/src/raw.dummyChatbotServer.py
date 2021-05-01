"""
    Copyright 2021 LogicForKidz

    This file is part of logicForkidz repository on https://www.github.com.

    All software in logicforkidz repository is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Software in logicforkidz repository is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
A basic, multiclient 'chat server' using Python's select module
with interrupt handling.

Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys
import signal

def readline_from_socket(sock):
    with BytesIO() as buffer:
        while True:
            try:
                resp = sock.recv(100)       # Read in some number of bytes -- balance this
            except BlockingIOError:
                print("sleeping")           # Do whatever you want here, this just
                time.sleep(2)               #   illustrates that it's nonblocking
            else:
                buffer.write(resp)          # Write to the BytesIO object
                buffer.seek(0)              # Set the file pointer to the SoF
                start_index = 0             # Count the number of characters processed
                for line in buffer:
                    start_index += len(line)
                    handle_line(line)       # Do something with your line
    
                """ If we received any newline-terminated lines, this will be nonzero.
                    In that case, we read the remaining bytes into memory, truncate
                    the BytesIO object, reset the file pointer and re-write the
                    remaining bytes back into it.  This will advance the file pointer
                    appropriately.  If start_index is zero, the buffer doesn't contain
                    any newline-terminated lines, so we set the file pointer to the
                    end of the file to not overwrite bytes.
                """
                if start_index:
                    buffer.seek(start_index)
                    remaining = buffer.read()
                    buffer.truncate(0)
                    buffer.seek(0)
                    buffer.write(remaining)
                else:
                    buffer.seek(0, 2)
    
    
class ChatServer(object):
    """ Simple chat server using select """
    
    def __init__(self, port=8007, backlog=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        print ('Listening to port',port,'...')
        self.server.listen(backlog)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        # Close the server
        print ('Shutting down server...')
        # Close existing client sockets
        for o in self.outputs:
            o.close()
            
        self.server.close()

    def getname(self, client):

        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))
        
    def serve(self):
        
        inputs = [self.server,sys.stdin]
        self.outputs = []

        running = 1

        while running:

            try:
                inputready,outputready,exceptready = select.select(inputs, self.outputs, [])
            except select.error as e:
                break
            except socket.error as e:
                break

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print ('chatserver: got connection %d from %s' % (client.fileno(), address))
                    client.setblocking(0)
                    f = client.makefile('rb',0) 
                    self.clientmap[client] = (address, "", f)
                    self.clients += 1
                    for line in f.readlines():
                        print ("Read ", line)

                    
                    # just send Hello
                    client.sendall(b'Hello')
                    inputs.append(client)

                    address, cname, fhandle = self.clientmap[client] 
                    self.clientmap[client] = (address, line, fhandle)

                    # Send joining information to other clients
                    msg = '\n(Connected: New client (%d) from %s)' % (self.clients, self.getname(client))
                    for o in self.outputs:
                        # o.send(msg)
                        o.sendall(msg)
                    
                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0
                else:
                    # handle all other sockets
                    try:
                        # data = s.recv(BUFSIZ)
                        data = s.recv(1024)
                        if data:
                            # Send as new client's message...
                            msg = '\n#[' + self.getname(s) + ']>> ' + data
                            # Send data to all except ourselves
                            for o in self.outputs:
                                if o != s:
                                    # o.send(msg)
                                    o.sendall(msg)
                        else:
                            print ('chatserver: %d hung up' % s.fileno())
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)

                            # Send client leaving information to others
                            msg = '\n(Hung up: Client from %s)' % self.getname(s)
                            for o in self.outputs:
                                # o.send(msg)
                                o.sendall(msg)
                                
                    except socket.error as e:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)
                        


        self.server.close()

if __name__ == "__main__":
    ChatServer().serve()
