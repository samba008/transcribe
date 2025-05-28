from deep_translator import GoogleTranslator

def translate_to_telugu(text):
    return GoogleTranslator(source='auto', target='te').translate(text)
