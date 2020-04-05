import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import RichMenu

def create_richmenuid(line_bot_api, rich_menu_name):
    ''' Create rich menu & Upload rich menu image  
        rich_menu_name: 填入要新增的 圖文選單  

        新增一個執行一次就好，不然 ID 會有很多個      
    '''
    # Create rich menu and get ID
    lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(json.load(open('material/'+ rich_menu_name +'/rich_menu.json', 'r', encoding='utf8'))))
    print('Rich Menu ID:', lineRichMenuId)
                                        
    # record rich menu ID
    with open('material/'+ rich_menu_name +'/rich_menu_id', 'w', encoding='utf8') as f:
        f.write(lineRichMenuId)

    # Upload rich menu image
    setImageResponse = ''
    with open('material/'+ rich_menu_name +'/rich_menu.png', 'rb') as f:
        setImageResponse = line_bot_api.set_rich_menu_image(lineRichMenuId, 'image/png', f)
    print('Upload Result: ', setImageResponse)

    return lineRichMenuId


def userlinktest_richmenuid(line_bot_api, self_user_id, lineRichMenuId):
    ''' Link rich menu to user  
        lineRichMenuId: 填入要測試的 圖文選單ID  

        此為綁定個人用戶進行測試                 
    '''
    linkResult = line_bot_api.link_rich_menu_to_user(self_user_id, lineRichMenuId)
    print('Link Result: ', linkResult)


def userunlink_richmenuid(line_bot_api, self_user_id):
    ''' Unlink rich menu from user  

        進階功能: VIP會員管理
    '''
    unlinkResult = line_bot_api.unlink_rich_menu_from_user(self_user_id)
    print('Unlink Result: ', unlinkResult)


def getuser_richmenuid(line_bot_api, self_user_id):
    ''' Get rich menu ID of user

        進階功能: 用 linebot 做遊戲時，可以得知用戶現在玩到哪 XD
    '''
    rich_menu_id = line_bot_api.get_rich_menu_id_of_user(self_user_id)
    print(rich_menu_id)


def list_richmenuid(line_bot_api):
    ''' Get rich menu list   

        列出此帳號內所有的圖文選單ID
    '''
    rich_menu_list = line_bot_api.get_rich_menu_list()
    for rich_menu in rich_menu_list:
        print(rich_menu.rich_menu_id)


def delete_richmenuid(line_bot_api, rich_menu_name):
    ''' Delete rich menu  
        rich_menu_name: 填入要移除的 圖文選單  

        讀取 rich_menu_id 檔案，並告知 Line 進行刪除，  
        並在刪除後，把 rich_menu_id 檔案內容清空 
    '''  
    with open('material/'+ rich_menu_name +'/rich_menu_id', 'r', encoding='utf8') as f:
        rich_menu_id = f.read()
        deleteResult = line_bot_api.delete_rich_menu(rich_menu_id)
        print('Delete Result:', deleteResult)

    with open('material/'+ rich_menu_name +'/rich_menu_id', 'w', encoding='utf8') as f:
        f.write('')


if __name__ == "__main__":

    if os.path.isfile("line_secret_key"):
        secretFileContentJson = json.load(open("line_secret_key", 'r', encoding="utf-8"))
        line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
        self_user_id = secretFileContentJson.get("self_user_id")
    else:
        line_bot_api = LineBotApi(os.getenv("channel_access_token"))
        self_user_id = os.getenv("self_user_id")


    '''建立或刪除多個圖文選單時，可用 list + loop'''
    # rich_menu_array = ['rich_menu_default', 'rich_menu_default2']
    # for name in rich_menu_array:
    #     create_richmenuid(line_bot_api, name)
    
    # richmenuid = create_richmenuid(line_bot_api, 'rich_menu_default')      
    # userlinktest_richmenuid(line_bot_api, self_user_id, richmenuid)

    # delete_richmenuid(line_bot_api, 'rich_menu_default')
    # create_richmenuid(line_bot_api, 'rich_menu_default')
    list_richmenuid(line_bot_api)


