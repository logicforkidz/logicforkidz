"""
The chatClient module below provides the following helper functions to build your own chat client
1. chat_client_init(): this function initializes the chatbot. It accepts a dictionary that maps the following events to
                        their function handlers. If you want default behavior to an event then don't set the corresponding
                        key.

                        "connected"     - key for connected_to_server event handler.
                        "disconnected"  - key for disconnected_from_server event handler
                        "from_server"   - key for received message_from_server event handler.
                        "from_terminal" - key for received message_from_terminal event handler.

2. chat_client_run(): this function starts running the main loop to poll for messages.
3. chat_client_send_msg(msg): this function sends the given message to the specified user.
                                      It will return True if successful, False otherwise
4. chat_client_change_prompt(prompt): this function will change the prompt to the given string.

Also the following data types are relevant:

1. msg: it is a dictionary that has 3 keys:
        (a) "from" : username of the user that sent the messsage
        (b) "to": username of the user to who the message was sent.
        (c) "text" the actual text of the message.
        Note:
             In order to send a message to server set the value of "to" key to "/"
             In order to sent a message to everyone don't include the "to" key
             Likewise if a server sends you a message the value of "from" will be "/". Otherwise
             the value of "from" key will be set to the user who sent the message.
"""

import chatClient

def handle_server_connected():
    """
    This function is called when the connection to server is successful.
    """
    print("\n[System] Server connected\n")

def handle_server_disconnected():
    """
    This function is called when the connection to server gets dropped.
    """
    print("\n[System] Server disconnected\n")

def handle_msg_from_server(msg):
    """
    This function is called when a new message is received from the server.
    See notes at the top for the definition of msg.
    If you have handled the message and you don't want chatClient to do anything further with it
    then this function should return 0. Otherwise return -1
    """
    print("\n[System] got msg from server\n")
    return -1

def handle_msg_from_terminal(msg):
    """
    This function is called when the user enters some text at the terminal and presses ENTER

    msg is a dictionary as described in the notes at the top of the file.
    msg["from"] will be set to the user name you supplied when you initialized the function.
    msg["text"] will be set to the string typed by user.

    It is upto you to appropriately set the "to" key. If you don't set it then the msg will be
    sent to server without it and the server will apply the default behavior.

    If you have handled this message and don't want chatClient to do anything further then return 0.
    If you return anything else the chatClient will send msg to the chatbotServer
    """
    print("\n[System] got msg from terminal\n")
    return -1


#parse command line arguments
import argparse
import sys
parser = argparse.ArgumentParser(description="A chat client")
parser.add_argument('--debug', help='enable debug trace messages', default=False, action='store_true')
parser.add_argument('--name', dest='name', help='your user name', required=True)
parser.add_argument('--server', dest = 'server', help='server address', default="127.0.0.1")
parser.add_argument('--port', dest='port', help='server port number', default=8007)
args = parser.parse_args(sys.argv[1:])
print ("Trying to connect to ",args.server, " at port ", args.port, " as ", args.name, "\n")

# Intialize the chatbot server
myEventHandlers = {}
myEventHandlers ["connected"] = handle_server_connected
myEventHandlers["disconnected"] = handle_server_disconnected
myEventHandlers["from_server"] = handle_msg_from_server
myEventHandlers["from_terminal"] = handle_msg_from_terminal

#Intialize the chatClient
chatClient.chat_client_init(args.name, server=args.server, port=args.port, handlers=myEventHandlers, debug = args.debug)

# run the main loop of the server
chatClient.chat_client_run()
