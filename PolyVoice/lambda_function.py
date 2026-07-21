import json
import boto3

translate = boto3.client('translate')

def lambda_handler(event, context):
    print("Event: " + json.dumps(event))

    # 抓取使用者的目標語言
    slots = event['sessionState']['intent']['slots']
    target_lang_slot = slots.get('targetLanguage')

    target_language = "zh" # 預設中文
    if target_lang_slot and target_lang_slot.get('value'):
        lang_name = target_lang_slot['value']['interpretedValue'].lower()
        if 'french' in lang_name:
            target_language = 'fr'
        elif 'spanish' in lang_name:
            target_language = 'es'
        elif 'chinese' in lang_name:
            target_language = 'zh'

    # 模擬要翻譯的文字（之後可以從 Lex 取得使用者說的話）
    text_to_translate = "Hello, welcome to our cloud system!"
    
    # 呼叫 AWS Translate 翻譯
    response = translate.translate_text(
        Text=text_to_translate,
        SourceLanguageCode='en',
        TargetLanguageCode=target_language
    )
    
    translated_text = response['TranslatedText']

    return {
        'sessionState': {
            'dialogAction': {'type': 'Close'},
            'intent': {'name': event['sessionState']['intent']['name'], 'state': 'Fulfilled'}
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': f"翻譯結果 ({target_language}): {translated_text}"
            }
        ]
    }