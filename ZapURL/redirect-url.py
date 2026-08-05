import json
import boto3

# 初始化 DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlMappings')

def lambda_handler(event, context):
    try:
        # 1. 從 API Gateway 的路徑參數中取得短代碼
        # （我們等等在 API Gateway 會設定一個變數叫 proxy 或 shortCode）
        path_parameters = event.get('pathParameters', {}) or {}

        # 兼容不同的 API Gateway 路由設定方式 (proxy 或自訂變數)
        short_code = path_parameters.get('proxy') or path_parameters.get('shortCode')

        if not short_code:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing short code in URL path.'})
            }

        # 2. 去 DynamoDB 查詢對應的長網址
        response = table.get_item(
            Key={
                'shortCode': short_code
            }
        )

        # 3. 如果找到了就 302 轉址，找不到就回傳 404
        if 'Item' in response:
            long_url = response['Item']['longUrl']
            return {
                'statusCode': 302,
                'headers': {
                    'Location': long_url
                },
                'body': '' # 重新導向不需要 Body 內容
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Short URL not found.'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }