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

from twisted.protocols import basic
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
import pickle

marshall = pickle.dumps
unmarshall = pickle.loads

debug = False
server_port = 8007
handle_new_user_connected = None
handle_user_disconnected = None
handle_msg_from_user = None
factory = None

# print debug messages only if debug is set
def print_trace(*args):
   if debug: print(args)

# fill up the missing fields and marshall the message
def encodeMessage(msg):
    if not 'to' in msg.keys(): return None
    if not 'text' in msg.keys(): msg['text']=""
    if not 'from' in msg.keys(): msg['from']='Server'
    return marshall(msg)

# unmarshall the incoming message
def decodeMessage(msg):
    msg = unmarshall(msg)
    return msg

class MyChat(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def addUserToClientMap(self, user):
        if user in self.factory.clientmap.keys(): return False
        self.factory.clientmap[user] = self
        self.factory.clientmap[self] = user
        if handle_new_user_connected: handle_new_user_connected(user)
        return True

    def delUserFromClientMap(self, user):
        if user not in self.factory.clientmap.keys(): 
            print_trace ("ERROR: ", user, " not found in clientmap\n")
            return
        # tell everyone we lost a user
        for key in self.factory.clientmap.keys():
            #print_trace("Ankur CA: looping keys user=", repr(user), '\n')
            if key == user: continue
            if key == self: continue
            #print_trace("Ankur CA: found another user")
            if isinstance(key, MyChat):
                #print_trace("Ankur CA: sending message")
                to_user = self.factory.clientmap[key]
                msg = encodeMessage({'to': to_user, 'text': 'User ' + user + ' disconnected'})
                self.factory.clientmap[to_user].sendLine(msg)
        # directory maintenance
        self.factory.clientmap.pop(user, None)
        self.factory.clientmap.pop(self, None)

    def connectionMade(self):
        print_trace("Got new client!")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print_trace("Lost a client!")
        if handle_user_disconnected: handle_user_disconnected(self.factory.clientmap[self])
        self.delUserFromClientMap(self.factory.clientmap[self]) 
        self.factory.clients.remove(self)

    def dataReceived(self, line):
        print_trace("data received", repr(line))
        msg = decodeMessage(line)
        user = msg['from']
        ret = -1

        # try to add user to client map regardless
        u = self.addUserToClientMap(user)
        if u: # send hello back to user and an announcement to everyone else.
            msg = encodeMessage({'to': user, 'text': 'Hello ' + user})
            if msg: self.sendLine(msg)
            for key in self.factory.clientmap.keys():
                #print_trace ("Ankur CA: looping keys user=", repr(key))
                if key == user: continue
                if key == self: continue
                #print_trace("Ankur CA: found another user", repr(key))
                if isinstance(key, MyChat):
                    to_user = self.factory.clientmap[key]
                    #print_trace("Ankur CA: sending message to ", to_user)
                    msg = encodeMessage({'to':to_user, 'text': 'User ' + user + ' joined'})
                    self.factory.clientmap[to_user].sendLine(msg)
        else: # client was already in the map
            if handle_msg_from_user: ret = handle_msg_from_user(msg)
            if ret != 0: # implement default behavior of sending the message to everyone else.
                for key in self.factory.clientmap.keys():
                    if  key == user: continue
                    if  key == self: continue
                    if  isinstance(key, MyChat):
                        self.factory.clientmap[self.factory.clientmap[key]].sendLine(line)

    def lineReceived(self, line):
        print_trace("received", repr(line))
        self.sendLine(self.buildMessage("Hello!", "ascii"))

    def message(self, message):
       self.transport.write(message + b"\n")

class BotFactory(protocol.Factory):
    def __init__ (self):
        self.clientmap = {}

    def buildProtocol(self, addr):
        return MyChat(self)


"""This  initializes the chatbot client"""
def chatbot_server_init(args, handlers):
    global factory, server_port, handle_new_user_connected, handle_user_disconnected, handle_msg_from_user

    #debug
    global debug
    debug = args.debug

    # server port
    server_port = args.port

    # set the handlers if given
    k = ['connected', 'disconnected', 'from_user']
    for i in k:
        if i in handlers.keys():
            if callable(handlers[i]):
                if i == 'connected': handle_new_user_connected = handlers[i]
                if i == 'disconnected': handle_user_disconnected = handlers[i]
                if i == 'from_user': handle_msg_from_user = handlers[i]

    # create and init the factory
    factory = BotFactory()
    factory.protocol = MyChat
    factory.clients = []

"""This runs the protocol on port in server_port"""
def chatbot_server_run():
    global server_port
    endpoint = TCP4ServerEndpoint(reactor, server_port)
    endpoint.listen(factory)
    reactor.run()

"""This sends the given message to the specifed user - Will return True if successful, False otherwise"""
def chatbot_server_send_msg(msg):
    if not 'to' in msg.keys(): return False
    else: user = msg['to']
    if not user in factory.clientmap.keys(): return False
    factory.clientmap[user].sendLine(msg)
    return True




