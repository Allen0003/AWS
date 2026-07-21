import json
import boto3

translate = boto3.client('translate')

def lambda_handler(event, context):
    print("Event: " + json.dumps(event))

    # 抓取 Lex 傳過來的 slots
    slots = event['sessionState']['intent']['slots']

    # 1. 抓取目標語言 (例如 French / chinese)
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

    # 2. 抓取使用者想翻譯的文字 (動態參數！)
    text_slot = slots.get('textToTranslate')
    text_to_translate = "Hello, default text." # 預設值
    if text_slot and text_slot.get('value'):
        # 抓取使用者實際打的字
        text_to_translate = text_slot['value']['interpretedValue']

    # 3. 呼叫 AWS Translate 進行動態翻譯
    response = translate.translate_text(
        Text=text_to_translate,
        SourceLanguageCode='auto', # 自動偵測來源語言，超方便！
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