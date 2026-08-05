import json
import boto3
import random
import string

# 初始化 DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlMappings')

def generate_short_code(length=6):
    """產生隨機的短代碼，例如 ab3X9z"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def lambda_handler(event, context):
    try:
        # 1. 解析前端傳來的 Body 資料
        body = json.loads(event.get('body', '{}'))
        long_url = body.get('longUrl')

        if not long_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "longUrl" in request body.'})
            }

        # 2. 產生短代碼（你可以檢查是否重複，這裡先簡化直接產生）
        short_code = generate_short_code()

        # 3. 寫入 DynamoDB
        table.put_item(
            Item={
                'shortCode': short_code,
                'longUrl': long_url
            }
        )

        # 4. 回傳成功訊息與短代碼
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Short URL created successfully!',
                'shortCode': short_code,
                'longUrl': long_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }