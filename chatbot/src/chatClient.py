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
eventHandlers = {}
chatClient = None
dbg = False

# print debug messages only if debug is set
def print_trace(*args):
   if dbg: print(args)

class ChatClient(object):
    """ A simple command line chat client using select """

    def buildMessage(self, text, to=""):
        m = {}
        m['from'] = self.name
        m['to'] = to
        m['text'] = text
        return marshall(m)

    def decodeMessage(self, msg):
        msg = unmarshall(msg)
        return msg

    # public function needs to validate the keys
    def sendMessage(self, msg):
        if 'text' in msg.keys(): text = msg['text']
        else: text = ""
        if 'to' in msg.keys(): to = msg['to']
        else: to=""
        m = self.buildMessage(text, to)
        try:
            self.sock.send(m)
            return True
        except:
            return False

    def __init__(self, name, host='127.0.0.1', port=8007):
        self.name = name
        self.port = int(port)
        self.host = host
        # Quit flag
        self.flag = False
        # Initial prompt
        #self.prompt = '[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        self.prompt = '>'
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(False)
            self.sock.settimeout(.1)
            self.sock.connect((host, self.port))
            print('Connected to chat server@%d\n' % self.port)
            # if event handler for connected is set call it.
            if 'connected' in eventHandlers.keys(): eventHandlers['connected']()
            # Send my name...
            msg = {'text':'hello', 'to':'/'}
            self.sendMessage(msg)
            #addr = ""
            #self.prompt = '[' + '@'.join((self.name, addr)) + ']> '
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

                # Wait for input from socket
                inputready, outputready, exceptrdy = select.select([self.sock], [], [], .1)
                for i in inputready:
                    if i == self.sock:
                        data = self.sock.recv(1024)
                        if not data:
                            if 'disconnected' in eventHandlers.keys(): eventHandlers['disconnected']()
                            print('Shutting down.\n')
                            self.flag = True
                            break
                        else:
                            ret = -1
                            msg = self.decodeMessage(data)
                            # call server message event handler if it is set.
                            if 'from_server' in eventHandlers.keys(): ret = eventHandlers['from_server'](msg)
                            if ret != 0:
                                print_trace(repr(msg))
                            print_prompt = True

                # check for input from stdin (terminal)
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
                    msg = {}
                    msg['from'] = self.name
                    msg['to'] = ''
                    msg ['text'] = data
                    ret = -1
                    if 'from_terminal' in eventHandlers.keys():  ret = eventHandlers['from_terminal'](msg)
                    if ret != 0: # we need to handle the message
                        self.sendMessage(msg)

            except KeyboardInterrupt:
                if 'disconnected' in eventHandlers.keys(): eventHandlers['disconnected']()
                print('Interrupted.\n')
                self.sock.close()
                break


"""
    chat_client_init(): Intialize the chatClient
    
    name = the username (required parameter)
    server = ipaddress of the server (defaults to local host
    port = port on which the server is listening
    handlers = a dictionary of event handlers.
"""
def chat_client_init(name, server="127.0.0.1", port=8007, handlers={}, debug=False):
    global chatClient, eventHandlers

    #debug
    global dbg
    dbg = debug

    # clean and store the handlers
    k = ['connected', 'disconnected', 'from_server', 'from_terminal']
    for i in k:
        if i in handlers.keys():
            if not callable(handlers[i]):
                handlers.pop(i, None)
    eventHandlers = handlers

    #intialize the chatClient
    chatClient = ChatClient(name, server, port)


#will run the main command tool of the program.
def chat_client_run():
    global chatClient
    if chatClient: chatClient.cmdloop()

#send the specified message to the given user
def chat_client_send_msg(msg):
    global chatClient
    if chatClient.sendMessage(msg): return True
    return False

#change the prompt to the specified prompt
def chat_client_change_prompt(prompt='>'):
    global chatClient
    chatClient.prompt = prompt
    sys.stdout.write('\n' + prompt)
    sys.stdout.flush()

"""
    The code that will be executed if this module is run from command line 
"""
if __name__ == "__main__":
    chatClient = ChatClient("foo")
    chatClient.cmdloop()
