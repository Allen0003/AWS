import os
import requests
from dotenv import load_dotenv

load_dotenv('config.env')

TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_line_message(message: str):
    if not TOKEN or not USER_ID:
        print("[警告] LINE Token 或 User ID 未設定，無法發送通知！")
        return

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }
    data = {
        'to': USER_ID,
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(發送 LINE 訊息失敗: {response.text})
    except Exception as e:
        print(f"LINE 訊息連線異常: {e}")

if __name__ == '__main__':
    send_line_message("🚀 DockerTrader 階段三：LINE Bot 風控通知測試成功！")