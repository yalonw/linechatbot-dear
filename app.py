'''==================== Application 主架構 ===================='''
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import json
import os

app = Flask(__name__, static_url_path = "/images", static_folder = "../images/")

if os.path.isfile("line_secret_key"):
    secretFileContentJson = json.load(open("line_secret_key", 'r', encoding="utf-8"))
    server_url = secretFileContentJson.get("server_url")
    line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
    handler = WebhookHandler(secretFileContentJson.get("secret_key"))
    linkRichMenuId = secretFileContentJson.get("rich_menu_id")
else:
    server_url = os.getenv("server_url")
    line_bot_api = LineBotApi(os.getenv("channel_access_token"))
    handler = WebhookHandler(os.getenv("secret_key"))
    linkRichMenuId = os.getenv("rich_menu_id")


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


'''==================== detect_json_array_to_new_message_array ===================='''
from linebot.models import (
        TextSendMessage, ImageSendMessage, VideoSendMessage, AudioSendMessage, LocationSendMessage, StickerSendMessage, 
        ImagemapSendMessage, TemplateSendMessage, FlexSendMessage
    )

def detect_json_array_to_new_message_array(fileName):
    ''' message_type 判斷器

        讀取指定的 json檔，解析成不同格式的 SendMessage
    '''
    with open(fileName, 'r', encoding='utf8') as f:
        jsonArray = json.load(f)
    
    newmessage_Array = []
    for jsonObject in jsonArray:
        message_type = jsonObject.get('type')
        
        if message_type == 'text':
            newmessage_Array.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            newmessage_Array.append(StickerSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            newmessage_Array.append(ImageSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            newmessage_Array.append(VideoSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'audio':
            newmessage_Array.append(AudioSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'location':
            newmessage_Array.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            newmessage_Array.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            newmessage_Array.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            newmessage_Array.append(FlexSendMessage.new_from_json_dict(jsonObject))        

    return newmessage_Array


'''==================== handler process Event ===================='''
from linebot.models import FollowEvent, MessageEvent, TextMessage, PostbackEvent
import requests

'''------------------- process_follow_event -------------------'''
@handler.add(FollowEvent)
def process_follow_event(event):
    # get and save user profile (name, picture, status_message, user_id)
    user_profile = line_bot_api.get_profile(event.source.user_id)
    with open("user_profile", "a", encoding='utf8') as f:
        f.write(json.dumps(vars(user_profile), sort_keys=True))
        f.write(',\n')
        
    # Link rich menu to user
    line_bot_api.unlink_rich_menu_from_user(event.source.user_id)
    line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)
       
    # reply: read reply.josn and change to message_list
    reply_message_array = []
    replyJsonPath = "material/UserFollow/reply.json"
    reply_message_array = detect_json_array_to_new_message_array(replyJsonPath)
    line_bot_api.reply_message(event.reply_token, reply_message_array)


'''------------------- process_text_message -------------------'''
@handler.add(MessageEvent, message=TextMessage)
def process_text_message(event):

    reply_message_array = []

    if event.message.text.find('【::help::】') == 0:   
        pass

    elif os.path.exists("material/"+ event.message.text):
        replyJsonPath = "material/"+ event.message.text +"/reply.json"
        reply_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, reply_message_array)

    elif event.message.text.find('請問') == 0 and len(event.message.text) > 4 :
        replyJsonPath = "material/Magic_card/reply.json"
        reply_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, reply_message_array)

    else:
        reply_message_array = TextSendMessage(text='抱歉 我不太明白你的意思')
        line_bot_api.reply_message(event.reply_token, reply_message_array)


'''------------------- process_postback_event -------------------'''
from urllib.parse import parse_qs
import random
@handler.add(PostbackEvent)
def process_postback_event(event):
    query_string_dict = parse_qs(event.postback.data)    
    print(query_string_dict)

    if 'ans' in query_string_dict:
        reply_message_array = ['magic_answer', 'next_section']

        with open('material/magic_data.json' , 'r', encoding='utf8') as f:
            readjson = json.loads(f.read())
            magic_number = str(random.randint(1,348))
            magic_words = readjson[magic_number]
        reply_message_array[0] = TextMessage(text=magic_words)
        
        replyJsonPath = 'material/'+ query_string_dict.get('folder')[0] +"/reply.json"
        reply_message_array[1] = detect_json_array_to_new_message_array(replyJsonPath)[0]

        line_bot_api.reply_message(event.reply_token, reply_message_array)

    elif 'folder' in query_string_dict:        
        reply_message_array = []
        replyJsonPath = 'material/'+ query_string_dict.get('folder')[0] +"/reply.json"
        reply_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, reply_message_array)

    elif 'menu' in query_string_dict: 
        linkRichMenuId = open('material/'+ query_string_dict.get('menu')[0] +'/rich_menu_id', 'r', encoding='utf8').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id, linkRichMenuId)
        
        replyJsonPath = 'material/'+ query_string_dict.get('menu')[0] +"/reply.json"
        reply_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, reply_message_array)


'''==================== Application 運行（開發版）===================='''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')

'''==================== Application 運行（heroku版）===================='''
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])