import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table('ChatConnections')
messages_table = dynamodb.Table('ChatMessages')

# 從環境變數或直接指定你的 API Gateway 網域 (去掉 wss:// 和後面結尾的斜線)
# 你的 WSS: wss://trvnx6ap7f.execute-api.us-east-1.amazonaws.com/production/
API_GATEWAY_DOMAIN = "trvnx6ap7f.execute-api.us-east-1.amazonaws.com"
API_GATEWAY_STAGE = "production"

apigw_management = boto3.client(
    'apigatewaymanagementapi',
    endpoint_url=f"https://{API_GATEWAY_DOMAIN}/{API_GATEWAY_STAGE}"
)

def lambda_handler(event, context):
    route_key = event.get('requestContext', {}).get('routeKey')
    connection_id = event.get('requestContext', {}).get('connectionId')

    print(f"Received route: {route_key}, connectionId: {connection_id}")

    if route_key == '$connect':
        # 1. 使用者連線：儲存 connectionId
        try:
            connections_table.put_item(Item={'connectionId': connection_id})
        except Exception as e:
            print(f"Connect error: {e}")
            return {'statusCode': 500, 'body': 'Failed to connect'}
        return {'statusCode': 200, 'body': 'Connected.'}

    elif route_key == '$disconnect':
        # 2. 使用者斷線：刪除 connectionId
        try:
            connections_table.delete_item(Key={'connectionId': connection_id})
        except Exception as e:
            print(f"Disconnect error: {e}")
            return {'statusCode': 500, 'body': 'Failed to disconnect'}
        return {'statusCode': 200, 'body': 'Disconnected.'}

    elif route_key == '$default':
        # 3. 收到訊息：廣播給所有人
        try:
            body = json.loads(event.get('body', '{}'))
            message_text = body.get('message', 'Hello from server!')
            user_name = body.get('name', 'Anonymous')

            # 格式化廣播資料
            out_data = json.dumps({
                'name': user_name,
                'message': message_text
            })

            # 取得所有在線上的連線
            scan_response = connections_table.scan(ProjectionExpression='connectionId')
            items = scan_response.get('Items', [])

            # 廣播給所有連線中的客戶端
            for item in items:
                active_conn_id = item['connectionId']
                try:
                    apigw_management.post_to_connection(
                        ConnectionId=active_conn_id,
                        Data=out_data.encode('utf-8')
                    )
                except Exception as ex:
                    # 如果該連線已失效（例如客戶端異常斷線），可選擇從 DB 清理
                    print(f"Post to connection {active_conn_id} failed: {ex}")

        except Exception as e:
            print(f"Default route error: {e}")
            return {'statusCode': 500, 'body': 'Failed to process message'}

        return {'statusCode': 200, 'body': 'Message sent.'}

    return {'statusCode': 400, 'body': 'Unrecognized route'}