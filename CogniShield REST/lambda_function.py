import json
import boto3
import uuid

# 初始化 DynamoDB 客連結，並指定對應的資料表
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Posts')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    # 取得 HTTP 方法與路徑參數 (適用於 API Gateway 代理整合)
    http_method = event.get('httpMethod')
    path_parameters = event.get('pathParameters') or {}
    item_id = path_parameters.get('id')

    try:
        # 1. 讀取 (GET)
        if http_method == 'GET':
            if item_id:
                # 取得單筆資料
                response = table.get_item(Key={'id': item_id})
                if 'Item' not in response:
                    return create_response(404, {'message': '找不到該筆資料'})
                return create_response(200, response['Item'])
            else:
                # 取得全部資料
                response = table.scan()
                return create_response(200, response.get('Items', []))

        # 2. 建立 (POST)
        elif http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            item_id = str(uuid.uuid4())[:8] # 自動產生 8 碼的唯一 ID

            item = {
                'id': item_id,
                'title': body.get('title', '無標題'),
                'content': body.get('content', '')
            }
            table.put_item(Item=item)
            return create_response(201, {'message': '建立成功', 'item': item})

        # 3. 更新 (PUT)
        elif http_method == 'PUT':
            if not item_id:
                return create_response(400, {'message': '缺少要更新的 ID'})
            body = json.loads(event.get('body', '{}'))

            response = table.update_item(
                Key={'id': item_id},
                UpdateExpression='SET title = :t, content = :c',
                ExpressionAttributeValues={
                    ':t': body.get('title', ''),
                    ':c': body.get('content', '')
                },
                ReturnValues='ALL_NEW'
            )
            return create_response(200, {'message': '更新成功', 'item': response.get('Attributes')})

        # 4. 刪除 (DELETE)
        elif http_method == 'DELETE':
            if not item_id:
                return create_response(400, {'message': '缺少要刪除的 ID'})
            table.delete_item(Key={'id': item_id})
            return create_response(200, {'message': f'已成功刪除 ID: {item_id}'})

        else:
            return create_response(405, {'message': f'不支援的請求方法: {http_method}'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'error': str(e)})

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }