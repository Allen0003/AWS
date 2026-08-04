import os
import json
import urllib.request
import urllib.error

def send_line_message(message: str, token: str, user_id: str):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': message}]
    }

    # 將字典轉成 JSON 字串並轉成 bytes
    req_data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("LINE 訊息發送成功！")
            else:
                print(f"發送 LINE 訊息失敗，狀態碼: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTP 錯誤: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"LINE 訊息連線異常: {e}")

def lambda_handler(event, context):
    TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    USER_ID = os.getenv('LINE_USER_ID')

    if not TOKEN or not USER_ID:
        print("[警告] LINE Token 或 User ID 未設定，無法發送通知！")
        return {
            'statusCode': 500,
            'body': 'Missing LINE credentials'
        }

    message = "看股票喔摟"

    send_line_message(message, TOKEN, USER_ID)

    return {
        'statusCode': 200,
        'body': 'Success'
    }