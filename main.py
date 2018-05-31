# -*- coding: utf-8 -*-
"""
Created on Fri May 25 09:23:58 2018

@author: Aakash
"""

import http.server
import json
import asyncio

from botbuilder.schema import (Activity, ActivityTypes)
from botframework.connector import ConnectorClient
from botframework.connector.auth import (MicrosoftAppCredentials,
                                         JwtTokenValidation, SimpleCredentialProvider)
#from luis_sdk import LUISClient
import luis
APP_ID = '50df83be-289f-4b6d-bcba-29eb74d78ac1'
APP_PASSWORD = 'ulwPSJ46^[vobvRBLH025+#'

#APP_ID = ''
#APP_PASSWORD = ''

####################################################################################################
class BotRequestHandler(http.server.BaseHTTPRequestHandler):

    @staticmethod
    def __create_reply_activity(request_activity, text):
        return Activity(
            type=ActivityTypes.message,
            channel_id=request_activity.channel_id,
            conversation=request_activity.conversation,
            recipient=request_activity.from_property,
            from_property=request_activity.recipient,
            text=text,
            service_url=request_activity.service_url)

    def __handle_conversation_update_activity(self, activity):
        self.send_response(202)
        self.end_headers()
        if activity.members_added[0].id != activity.recipient.id:
            credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
            reply = BotRequestHandler.__create_reply_activity(activity, 'Hello welcome to the cafeteria chatbot!')
            connector = ConnectorClient(credentials, base_url=reply.service_url)
            connector.conversations.send_to_conversation(reply.conversation.id, reply)

    def __handle_message_activity(self, activity):
        self.send_response(200)
        self.end_headers()
        credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
        connector = ConnectorClient(credentials, base_url=activity.service_url)
        userIntent = Analyze_User_Intent_LUIS(activity.text)
        response = Cafeteria_Response_Query(userIntent)
#        reply = BotRequestHandler.__create_reply_activity(activity, 'You said: %s' % activity.text)
        reply = BotRequestHandler.__create_reply_activity(activity, 'CafeteiaBot: %s' % response)
        connector.conversations.send_to_conversation(reply.conversation.id, reply)

    def __handle_authentication(self, activity):
        credential_provider = SimpleCredentialProvider(APP_ID, APP_PASSWORD)
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(JwtTokenValidation.assert_valid_activity(
                activity, self.headers.get("Authorization"), credential_provider))
            return True
        except Exception as ex:
            self.send_response(401, ex)
            self.end_headers()
            return False
        finally:
            loop.close()

    def __unhandled_activity(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(str(body, 'utf-8'))
        activity = Activity.deserialize(data)

        if not self.__handle_authentication(activity):
            return

        if activity.type == ActivityTypes.conversation_update.value:
            self.__handle_conversation_update_activity(activity)
        elif activity.type == ActivityTypes.message.value:
            self.__handle_message_activity(activity)
        else:
            self.__unhandled_activity()
            



def Cafeteria_Response_Query(userIntent):
    
    if(userIntent == "Greeting"):
        return "Hello there how can I help you today"
    
    elif(userIntent == 'GetMenu'):
        return "On today's menu we have steak & potatoes as entree and pineapple chicken as rice bowl. We also have pizza and soup"
    
    elif(userIntent =="OrderPizza"):
        return "You are all set. Your order for pizza is placed. You can pick it up from cafeteia in 10 minutes. Is there anything I can help you with?"
    
    elif(userIntent == "EndConversation"):
        return "Thank you. We hope you have a nice day!"
    
    else:
        return "I am not sure how to help you with that"
    
    


####################################################################################################

def Analyze_User_Intent_LUIS(userText):
    l = luis.Luis(url='	https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/d570cd5b-363f-4d0d-a1f0-9beddf2a8f5a?subscription-key=1a306c39a0af4a2d8692835e3b487dc5&verbose=true&timezoneOffset=0&q=')
#    r = l.analyze('Can I get the menu for today')
    r = l.analyze(userText)
    print (r.intents)
    best = r.best_intent() 
    print (best.intent)
    return best.intent
    

####################################################################################################

def main():
    try:
        SERVER = http.server.HTTPServer(('localhost', 9000), BotRequestHandler)
        print('Started http server on localhost:9000')
        SERVER.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        SERVER.socket.close()
        


    
####################################################################################################

if __name__ == "__main__":
    print("Chatbot Server Launched!")
    main()
#    l = luis.Luis(url='	https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/d570cd5b-363f-4d0d-a1f0-9beddf2a8f5a?subscription-key=1a306c39a0af4a2d8692835e3b487dc5&verbose=true&timezoneOffset=0&q=')
#    r = l.analyze('Can I get the menu for today')
#    print (r.intents)
#    best = r.best_intent() 
#    print (best.intent)
