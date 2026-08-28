import json
import os
import random
import urllib.request

LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
FREE_AI_API_KEY = os.environ.get('FREE_AI_API_KEY')


def lambda_handler(event, context):
  print('收到原始 Event:', json.dumps(event))

  try:
    body_raw = event.get('body', '{}')
    if isinstance(body_raw, str):
      body = json.loads(body_raw)
    else:
      body = body_raw

    for event_item in body.get('events', []):
      if event_item['type'] == 'message' and event_item['message'][
          'type'
      ] == 'text':
        user_message = event_item['message']['text']
        reply_token = event_item['replyToken']
        print(f'收到使用者訊息: {user_message}')

        # 檢查訊息裡面有沒有包含「小騷貨」
        if '小騷貨' not in user_message:
          print('沒有包含觸發詞「小騷貨」，不予回應')
          continue

        # 把「小騷貨」三個字從訊息裡拿掉，取得後面的實際指令
        clean_message = user_message.replace('小騷貨', '').strip()

        # 根據清掉前綴後的訊息進行判斷
        if '抽' in clean_message:
          # 隨機取得不同張美女圖片網址
          img_url = get_random_girl_image()
          send_line_image_reply(reply_token, img_url)
          continue
        elif '欸屁馬是什麼' in clean_message:
          ai_reply = '欸屁馬 是胖胖 愛放屁'
        elif '欸屁馬' in clean_message:
          ai_reply = '我是欸屁馬 快樂的一天'
        elif '菲比豬' in clean_message:
          ai_reply = '我是欸屁馬 愛放屁 噗噗噗'
        elif clean_message == '':
          ai_reply = '叫我幹嘛？'
        else:
          ai_reply = call_free_ai(clean_message)

        send_line_reply(reply_token, ai_reply)

    return {'statusCode': 200, 'body': json.dumps('Success')}
  except Exception as e:
    print(f'發生錯誤: {str(e)}')
    return {'statusCode': 500, 'body': json.dumps(str(e))}


def get_random_girl_image():
  # 準備一組不同的優質人像照片 ID 清單，讓它每次隨機挑選不同張
  photo_ids = [
      'photo-1534528741775-53994a69daeb',
      'photo-1517841905240-472988babdf9',
      'photo-1524504388940-b1c1722653e1',
      'photo-1494790108377-be9c29b29330',
      'photo-1529626455594-4ff0802cfb7e',
      'photo-1488426862026-3ee34a7d66df',
      'photo-1517841905240-472988babdf9',
      'photo-1506794778202-cad84cf45f1d',
  ]
  chosen_id = random.choice(photo_ids)
  random_v = random.randint(1, 10000)

  # 組合出正確大小且每次都不一樣的圖片網址
  image_url = f'https://images.unsplash.com/{chosen_id}?w=600&auto=format&fit=crop&q=60&v={random_v}'
  return image_url


def send_line_image_reply(reply_token, original_content_url):
  url = 'https://api.line.me/v2/bot/message/reply'
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {LINE_ACCESS_TOKEN}',
  }
  data = {
      'replyToken': reply_token,
      'messages': [
          {
              'type': 'image',
              'originalContentUrl': original_content_url,
              'previewImageUrl': original_content_url,
          }
      ],
  }

  req = urllib.request.Request(
      url,
      data=json.dumps(data).encode('utf-8'),
      headers=headers,
      method='POST',
  )
  try:
    with urllib.request.urlopen(req) as response:
      return response.read()
  except urllib.error.HTTPError as e:
    print(f'LINE 圖片 API 報錯: {e.code} - {e.read().decode("utf-8")}')
    raise e


def call_free_ai(prompt):
  url = 'https://api.groq.com/openai/v1/chat/completions'
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {FREE_AI_API_KEY}',
      'User-Agent': 'Mozilla/5.0',
  }
  payload = {
      'model': 'openai/gpt-oss-20b',
      'messages': [
          {
              'role': 'system',
              'content': (
                  '你是一個繁體中文助理，無論使用者問什麼，請務必全部使用台灣慣用的繁體中文（Traditional'
                  ' Chinese）來回答。'
              ),
          },
          {'role': 'user', 'content': prompt},
      ],
      'max_tokens': 1000,
  }

  req = urllib.request.Request(
      url,
      data=json.dumps(payload).encode('utf-8'),
      headers=headers,
      method='POST',
  )

  try:
    with urllib.request.urlopen(req) as response:
      result = json.loads(response.read().decode('utf-8'))
      return result['choices'][0]['message']['content']
  except urllib.error.HTTPError as e:
    err_msg = e.read().decode('utf-8')
    print(f'免費 AI API 報錯: {e.code} - {err_msg}')
    return '抱歉，AI 暫時連線失敗，請稍後再試！'


def send_line_reply(reply_token, text):
  url = 'https://api.line.me/v2/bot/message/reply'
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {LINE_ACCESS_TOKEN}',
  }
  data = {
      'replyToken': reply_token,
      'messages': [{'type': 'text', 'text': text}],
  }

  req = urllib.request.Request(
      url,
      data=json.dumps(data).encode('utf-8'),
      headers=headers,
      method='POST',
  )
  try:
    with urllib.request.urlopen(req) as response:
      return response.read()
  except urllib.error.HTTPError as e:
    print(f'LINE API 報錯: {e.code} - {e.read().decode("utf-8")}')
    raise e