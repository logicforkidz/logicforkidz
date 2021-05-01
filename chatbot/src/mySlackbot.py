"""
The chatbotServer mnodule below provides 3 helper functions to build the chatbot server
1. chatbot_server_init(): this function initializes the chatbot
2. chatbot_server_run(): this function starts running the main loop to poll for messages. 
3. chtnot_server_send_msg(user, msg): this function sends the given message to the specified user.
                                      It will return True if successful, False otherwise
"""
import chatbotServer


def handle_new_user_connected (user):
    """
    This function is called when a new user connects to Slackbot
    
    user is the string name of the user that connects
    """



def handle_user_disconnected (user):
    """
    This function is called when a new user connects to Slackbot
    user is the string name of the user that disconnected
    """
    

def handle_msg_from_user(user, msg):
    """
    This function is called when a new user connects to Slackbot

    user is the string name of the user that sent the message
    msg is the string message that the user sent. If the message is directed to 
        a particular user then client should send is as:  ruch@ how are you?
        If the message is directred to the chatbot  then the client should send
        it as  /<command>. For example, in order to find out who all are connected
        the client can send a command  /directory. You will need to parse these messages 
        and implement the functionality yourself. By default, the chatbot_server
        sends any message it receives to everyone else who is connected to it. 
        If you have handled the message and you don't want server to do anything with it
        then this function should return 0. But if you cannot handle this message
        and let the server forward it to everyone else, then return -1
    """
    return -1
    
# Intialize the chatbot server
chatbotServer.chatbot_server_init(handle_new_user_connected, handle_user_disconnected, handle_msg_from_user)

# run the main loop of the server
chatbotServer.chatbot_server_run()
