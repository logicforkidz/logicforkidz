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

handle_new_user_connected = None
handle_user_disconnected = None
handle_msg_from_user = None

class MyChat(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def buildMessage(self, from_who, msg):
        m = {}
        m['user'] = from_who
        m['msg'] = msg
        return marshall(m)

    def decodeMessage(self,  msg):
        msg = unmarshall (msg)
        return (msg['user'],msg['msg'])

    def addUserToClientMap(self, user):
        if user in self.factory.clientmap.keys(): return False
        self.factory.clientmap[user] = self
        self.factory.clientmap[self] = user
        if handle_new_user_connected: handle_new_user_connected(user)
        return True

    def delUserFromClientMap(self, user):
        if user not in self.factory.clientmap.keys(): 
            print ("ERROR: ", user, " not found in clientmap\n")
            return
        self.factory.clientmap.pop(user, None)
        self.factory.clientmap.pop(self, None)

    def connectionMade(self):
        print("Got new client!")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print("Lost a client!")
        if handle_user_disconnected: handle_user_disconnected(self.factory.clientmap[self])
        self.delUserFromClientMap(self.factory.clientmap[self]) 
        self.factory.clients.remove(self)

    def dataReceived(self, line):
        print("data received", repr(line))
        user, msg = self.decodeMessage(line)
        print("data unpacked ", user, " msg=", msg)
        ret = -1
        u = self.addUserToClientMap(user)
        if u: 
            self.sendLine(self.buildMessage('Server','Hello ' + user))
            line = self.buildMessage('Server', 'User ' + user + ' joined')
        else:
            ret = handle_msg_from_user(user, msg)
        if ret == -1: # implement default behavior of sending the mssage to everyone else. 
            for key in self.factory.clientmap.keys(): 
                if  key == user: continue
                if  key == self: continue
                if  isinstance(key, MyChat):
                    self.factory.clientmap[self.factory.clientmap[key]].sendLine(line)

    def lineReceived(self, line):
        print("received", repr(line))
        self.sendLine(self.buildMessage("Hello!", "ascii"))

    def message(self, message):
       self.transport.write(message + b"\n")

class BotFactory(protocol.Factory):
    def __init__ (self):
        self.clientmap = {}

    def buildProtocol(self, addr):
        return MyChat(self)


"""This  initializes the chatbot client"""
factory = None
def chatbot_server_init(connected=None, disconnected=None, msg=None):
    global factory, handle_new_user_connected, handle_user_disconnected, handle_msg_from_user 
    handle_new_user_connected = connected
    handle_user_disconnected = disconnected
    handle_msg_from_user = msg
    factory = BotFactory()
    factory.protocol = MyChat
    factory.clients = []

"""This runs the protocol on port 8007"""
def chatbot_server_run():
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(factory)
    reactor.run()

"""This sends the given message to the specifed user - Will return True if successful, False otherwise"""
def chatbot_server_send_msg(user, msg):
    if not user in factory.clientmap.keys(): return False
    factory.clientmap[user].sendLine(msg)
    return True




