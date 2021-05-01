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

import os
import sys
import select
import pickle
import socket
if os.name == "nt": import msvcrt

marshall = pickle.dumps
unmarshall = pickle.loads

class ChatClient(object):
    """ A simple command line chat client using select """

    def buildMessage(self, msg):
        m = {}
        m['user'] = self.name
        m['msg'] = msg
        return marshall(m)

    def decodeMessage (self, msg):
        msg = unmarshall(msg)
        return(msg['user'], msg['msg'])

    def __init__(self, name, host='127.0.0.1', port=8007):
        self.name = name
        # Quit flag
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
        self.prompt = '[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(False)
            self.sock.settimeout(.1)
            self.sock.connect((host, self.port))
            print('Connected to chat server@%d\n' % self.port)
            # Send my name...
            self.sock.send(self.buildMessage('Hello'))
            addr = ""
            self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
        except socket.error as e:
            print('Could not connect to chat server @%d\n' % self.port)
            sys.exit(1)

    def cmdloop(self):
        print_prompt = True
        while not self.flag:
            try:
                if print_prompt:
                    sys.stdout.write(self.prompt)
                    sys.stdout.flush()
                    print_prompt = False

                # Wait for input from stdin & socket
                inputready, outputready, exceptrdy = select.select([self.sock], [], [], .1)
                for i in inputready:
                    if i == self.sock:
                        data = self.sock.recv(1024)
                        user, msg = self.decodeMessage(data)
                        if not data:
                            print('Shutting down.\n')
                            self.flag = True
                            break
                        else:
                            sys.stdout.write( '\n[' + user + ']>')
                            sys.stdout.write(' ' + msg + '\n')
                            sys.stdout.flush()
                            print_prompt = True
                data = None
                if os.name == "nt":
                    if msvcrt.kbhit():
                        data = sys.stdin.readline().strip()
                        print_prompt = True
                elif os.name == "posix":
                    inputready, outputready, exceptrdy = select.select([0], [], [], .1)
                    for i in inputready:
                        if i == 0:
                            data = sys.stdin.readline().strip()
                            print_prompt = True
                if data:
                    data = self.buildMessage(data)
                    self.sock.send(data)
            except KeyboardInterrupt:
                print ('Interrupted.\n')
                self.sock.close()
                break


if __name__ == "__main__":

    if len(sys.argv) < 3:
        sys.exit('Usage: %s <your first name> <chat server ip address>'  % sys.argv[0])

    client = ChatClient(sys.argv[1], sys.argv[2], 8007)
    client.cmdloop()

