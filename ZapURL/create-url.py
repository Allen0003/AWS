import json
import boto3
import random
import string

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlMappings')

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def lambda_handler(event, context):
    print("收到 Event 內容:", json.dumps(event))

    try:
        # 相容直接測試或 API Gateway 呼叫
        body = {}
        if 'longUrl' in event:
            body = event
        elif 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            elif isinstance(event['body'], dict):
                body = event['body']

        long_url = body.get('longUrl')
        print("解析出的 longUrl:", long_url)  # <-- 印出解析結果

        if not long_url:
            print("錯誤：找不到 longUrl")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "longUrl" in request body.'})
            }

        short_code = generate_short_code()
        print(f"準備寫入 DynamoDB: shortCode={short_code}, longUrl={long_url}")

        # 寫入 DynamoDB
        table.put_item(
            Item={
                'shortCode': short_code,
                'longUrl': long_url
            }
        )
        print("DynamoDB 寫入成功！")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Short URL created successfully!',
                'shortCode': short_code,
                'longUrl': long_url
            })
        }

    except Exception as e:
        print(f"發生例外錯誤 (Exception): {str(e)}") # <-- 印出錯誤
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }