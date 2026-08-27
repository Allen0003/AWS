import json
import os
import urllib.request
import boto3

# 初始化 Bedrock 客戶端
bedrock = boto3.client(
    service_name='bedrock-runtime', region_name='us-east-1'
)

# 讀取環境變數
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')


def lambda_handler(event, context):
  print('收到原始 Event:', json.dumps(event))  # 👈 把收到的東西印出來看

  try:
    # 兼容處理：有些 API Gateway 會把 body 變成字串，有些會直接是 dict
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
        print(f'收到使用者訊息: {user_message}')  # 👈 印出收到的訊息

        if '欸屁馬' in user_message:
          ai_reply = '我是欸屁馬 快樂的一天'
        elif '菲比豬' in user_message:
          ai_reply = '我是欸屁馬 愛放屁 噗噗噗'
        else:
          ai_reply = call_bedrock(user_message)

        # 透過 LINE Reply API 將訊息回覆給使用者
        send_line_reply(reply_token, ai_reply)

    return {'statusCode': 200, 'body': json.dumps('Success')}
  except Exception as e:
    print(f'發生錯誤: {str(e)}')  # 👈 把錯誤印出來
    return {'statusCode': 500, 'body': json.dumps(str(e))}


def call_bedrock(prompt):
  payload = {
      'anthropic_version': 'bedrock-2023-05-31',
      'max_tokens': 1000,
      'messages': [{'role': 'user', 'content': prompt}],
  }

  response = bedrock.invoke_model(
      modelId='anthropic.claude-3-haiku-20240307-v1:0',
      body=json.dumps(payload),
  )

  result = json.loads(response['body'].read())
  return result['content'][0]['text']


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