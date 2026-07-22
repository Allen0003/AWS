import json
import boto3
import uuid

translate = boto3.client('translate')
polly = boto3.client('polly')
s3 = boto3.client('s3')

# 你的 S3 儲存桶名稱
BUCKET_NAME = 'polyvoice-audio-bucket-apma'

def lambda_handler(event, context):
    print("Event: " + json.dumps(event))

    try:
        # 1. 解析前端透過 API Gateway 傳過來的 JSON 資料
        body = event
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']

        # 取得前端傳來的文字與目標語言
        text_to_translate = body.get('text', 'MynameisApmaHappy')
        target_lang_input = body.get('targetLanguage', 'chinese').lower()

        # 2. 對應語言與 Polly 聲音
        target_language = "zh"
        polly_voice = "Zhiyu"

        if 'french' in target_lang_input or 'fr' in target_lang_input:
            target_language = 'fr'
            polly_voice = "Celine"
        elif 'spanish' in target_lang_input or 'es' in target_lang_input:
            target_language = 'es'
            polly_voice = "Lucia"
        elif 'chinese' in target_lang_input or 'zh' in target_lang_input:
            target_language = 'zh'
            polly_voice = "Zhiyu"

        # 3. 呼叫 Translate 進行翻譯
        trans_response = translate.translate_text(
            Text=text_to_translate,
            SourceLanguageCode='auto',
            TargetLanguageCode=target_language
        )
        translated_text = trans_response['TranslatedText']

        # 4. 呼叫 Polly 轉成語音
        polly_response = polly.synthesize_speech(
            Text=translated_text,
            OutputFormat='mp3',
            VoiceId=polly_voice
        )

        audio_stream = polly_response['AudioStream'].read()

        # 5. 上傳 MP3 到 S3
        file_name = f"translated_{uuid.uuid4()}.mp3"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=audio_stream,
            ContentType='audio/mpeg'
        )

        # 6. 產生 180 秒的 S3 臨時下載連結
        audio_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=180
        )

        # 7. 回傳符合 API Gateway 格式的 JSON（必須包含 headers 確保 CORS 正常運作）
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'translatedText': translated_text,
                'audioUrl': audio_url
            }, ensure_ascii=False)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }