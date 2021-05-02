"""
The chatbotServer mnodule below provides 3 helper functions to build the chatbot server
1. chatbot_server_init(): this function initializes the chatbot
2. chatbot_server_run(): this function starts running the main loop to poll for messages. 
3. chatbot_server_send_msg(msg): this function sends the given message to the specified user.
                                It will return True if successful, False otherwise

                                msg is a dictionary which can have 3 standard keys.
                                    'to':   which user the message is/was sent
                                    'from': who sent the message
                                    'text': the string message.
"""
import chatbotServer


def handle_new_user_connected (user):
    """
    This function is called when a new user connects to Slackbot
    
    user is the string name of the user that connects
    """
    print (user, " connected \n")



def handle_user_disconnected (user):
    """
    This function is called when a new user connects to Slackbot
    user is the string name of the user that disconnected
    """
    print (user, " disconnected \n")


def handle_msg_from_user(msg):
    """
    This function is called when a new user connects to Slackbot

    user is the string name of the user that sent the message
    msg is a dictionary. See notes above for details.

    By default, the chatbot_server forwards any message it receives to everyone else who is connected to it.
    If you have handled the message and you don't want server to do anything with it
    then this function should return 0. But return anything other than 0 for the server do its default processing
    """
    print ("received: ",  repr(msg), "\n")
    return -1


#parse command line arguments
import argparse
import sys
parser = argparse.ArgumentParser(description="A chat server")
parser.add_argument('--debug', help='enable debug trace messages', default=False, action='store_true')
parser.add_argument('--port', dest='port', help='server port number', default=8007)
args = parser.parse_args(sys.argv[1:])
print ("Starting server at port ", args.port, 'with debug ', args.debug, "\n")

# Intialize the chatbot server
myEventHandlers = {}
myEventHandlers ["connected"] = handle_new_user_connected
myEventHandlers["disconnected"] = handle_user_disconnected
myEventHandlers["from_user"] = handle_msg_from_user

# Intialize the chatbot server
chatbotServer.chatbot_server_init(args, myEventHandlers)

# run the main loop of the server
chatbotServer.chatbot_server_run()
