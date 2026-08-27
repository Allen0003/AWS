import json
import os
import urllib.request

# 讀取環境變數
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
# 💡 等等要在 Lambda 環境變數填入你的免費 API Key (例如 Groq Key)
FREE_AI_API_KEY = os.environ.get('FREE_AI_API_KEY')


def lambda_handler(event, context):
  print('收到原始 Event:', json.dumps(event))

  try:
    body_raw = event.get('body', '{}')
    if isinstance(body_raw, str):
      body = json.loads(body_raw)
    else:
      body = body_raw

    # 解析 LINE 傳過來的事件
    for event_item in body.get('events', []):
      if event_item['type'] == 'message' and event_item['message'][
          'type'
      ] == 'text':
        user_message = event_item['message']['text']
        reply_token = event_item['replyToken']
        print(f'收到使用者訊息: {user_message}')

        if '欸屁馬' in user_message:
          ai_reply = '我是欸屁馬 快樂的一天'
        elif '菲比豬' in user_message:
          ai_reply = '我是欸屁馬 愛放屁 噗噗噗'
        else:
          # 改呼叫不用錢的第三方免費 AI API
          ai_reply = call_free_ai(user_message)

        # 透過 LINE Reply API 將訊息回覆給使用者
        send_line_reply(reply_token, ai_reply)

    return {'statusCode': 200, 'body': json.dumps('Success')}
  except Exception as e:
    print(f'發生錯誤: {str(e)}')
    return {'statusCode': 500, 'body': json.dumps(str(e))}


def call_free_ai(prompt):
  # 這裡以 Groq 免費 API 為例 (相容 OpenAI 格式，速度極快)
  url = 'https://api.groq.com/openai/v1/chat/completions'
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {FREE_AI_API_KEY}',
  }
  payload = {
      'model': 'llama-3.1-8b-instant',  # Groq 的免費高速開源模型
      'messages': [{'role': 'user', 'content': prompt}],
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
    return '抱歉，免費 AI 腦袋暫時短路了！'


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
      res_body = response.read()
      print('LINE 回應結果:', res_body.decode('utf-8'))
      return res_body
  except urllib.error.HTTPError as e:
    print(f'LINE API 報錯: {e.code} - {e.read().decode("utf-8")}')
    raise e