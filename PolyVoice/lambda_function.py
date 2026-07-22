import json
import boto3
import uuid

translate = boto3.client('translate')
polly = boto3.client('polly')
s3 = boto3.client('s3')

# TODO: 換成你剛剛建立的 S3 儲存桶名稱
BUCKET_NAME = 'polyvoice-audio-bucket-apma'

def lambda_handler(event, context):
    print("Event: " + json.dumps(event))

    slots = event['sessionState']['intent']['slots']

    # 1. 抓目標語言與對應聲音
    target_lang_slot = slots.get('targetLanguage')
    target_language = "zh"
    polly_voice = "Zhiyu"

    if target_lang_slot and target_lang_slot.get('value'):
        lang_name = target_lang_slot['value']['interpretedValue'].lower()
        if 'french' in lang_name:
            target_language = 'fr'
            polly_voice = "Celine"
        elif 'spanish' in lang_name:
            target_language = 'es'
            polly_voice = "Lucia"
        elif 'chinese' in lang_name:
            target_language = 'zh'
            polly_voice = "Zhiyu"

    # 2. 抓要翻譯的文字
    text_slot = slots.get('textToTranslate')
    text_to_translate = "Hello, default text."
    if text_slot and text_slot.get('value'):
        text_to_translate = text_slot['value']['interpretedValue']

    # 3. 呼叫 Translate 翻譯
    trans_response = translate.translate_text(
        Text=text_to_translate,
        SourceLanguageCode='auto',
        TargetLanguageCode=target_language
    )
    translated_text = trans_response['TranslatedText']

    # 4. 呼叫 Polly 轉語音
    polly_response = polly.synthesize_speech(
        Text=translated_text,
        OutputFormat='mp3',
        VoiceId=polly_voice
    )

    audio_stream = polly_response['AudioStream'].read()

    # 5. 把 MP3 檔案上傳到 S3 儲存桶
    file_name = f"translated_{uuid.uuid4()}.mp3"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=audio_stream,
        ContentType='audio/mpeg'
    )

    # 6. 產生一個有效時間 180 秒的 S3 臨時下載連結 (Presigned URL)
    audio_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file_name},
        ExpiresIn=180
    )

    # 7. 回傳結果給 Lex (包含文字與語音連結)
    return {
        'sessionState': {
            'dialogAction': {'type': 'Close'},
            'intent': {'name': event['sessionState']['intent']['name'], 'state': 'Fulfilled'}
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': f"翻譯結果: {translated_text}\n語音連結: {audio_url}"
            }
        ]
    }