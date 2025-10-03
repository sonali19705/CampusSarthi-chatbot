from langdetect import detect
from googletrans import Translator

translator = Translator()

texts = [
    "नमस्ते, आप कैसे हैं?",                     # Hindi
    "तुम्ही कसे आहात?",                         # Marathi
    "હેલો, કેમ છો?",                             # Gujarati
    "আপনি কেমন আছেন?",                          # Bengali
    "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",      # Tamil
    "మీరు ఎలా ఉన్నారు?",                         # Telugu
    "ನೀವು ಹೇಗಿದ್ದೀರಾ?",                           # Kannada
    "നമസ്കാരം, നിങ്ങൾ എങ്ങനെയിരിക്കുന്നു?",        # Malayalam
    "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?",                           # Punjabi
    "थारो हाल चाल के है?"                         # Rajasthani / Marwari
]

for text in texts:
    try:
        # Detect language
        lang = detect(text)
        # Map unsupported langdetect codes to Hindi if needed
        if lang not in ['hi','mr','gu','bn','ta','te','kn','ml','pa']:
            lang = 'hi'
        
        print(f"Original Text: {text}")
        print(f"Detected language: {lang}")

        # Translate to English
        translated_en = text if lang == 'en' else translator.translate(text, src=lang, dest='en').text
        print(f"Translated to English: {translated_en}")

        # Translate back to original language
        translated_back = translated_en if lang == 'en' else translator.translate(translated_en, src='en', dest=lang).text
        print(f"Translated back to original: {translated_back}\n")

    except Exception as e:
        print(f"Error for text '{text}': {e}\n")
