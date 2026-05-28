from typing import Dict, List

SUPPORTED_LANGUAGES = [
    {"code": "kn", "name": "Kannada", "script": "ಕನ್ನಡ", "whisper_code": "kn", "locale": "kn-IN"},
    {"code": "hi", "name": "Hindi", "script": "हिन्दी", "whisper_code": "hi", "locale": "hi-IN"},
    {"code": "ta", "name": "Tamil", "script": "தமிழ்", "whisper_code": "ta", "locale": "ta-IN"},
    {"code": "te", "name": "Telugu", "script": "తెలుగు", "whisper_code": "te", "locale": "te-IN"},
    {"code": "ml", "name": "Malayalam", "script": "മലയാളം", "whisper_code": "ml", "locale": "ml-IN"},
    {"code": "bn", "name": "Bengali", "script": "বাংলা", "whisper_code": "bn", "locale": "bn-IN"},
    {"code": "mr", "name": "Marathi", "script": "मराठी", "whisper_code": "mr", "locale": "mr-IN"},
    {"code": "en", "name": "English", "script": "English", "whisper_code": "en", "locale": "en-IN"},
]

LANGUAGE_MAP: Dict[str, dict] = {lang["code"]: lang for lang in SUPPORTED_LANGUAGES}

GREETINGS: Dict[str, str] = {
    "kn": "ನಮಸ್ಕಾರ! ನಾನು ವಾಣಿ, ನಿಮ್ಮ AI ಸಂವಹನ ತರಬೇತುದಾರ. ಇಂದು ನಾವು ಏನು ಅಭ್ಯಾಸ ಮಾಡೋಣ?",
    "hi": "नमस्ते! मैं वाणी हूं, आपका AI संचार कोच। आज हम क्या अभ्यास करें?",
    "ta": "வணக்கம்! நான் வாணி, உங்கள் AI தகவல்தொடர்பு பயிற்சியாளர். இன்று என்ன பயிற்சி செய்வோம்?",
    "te": "నమస్కారం! నేను వాణి, మీ AI కమ్యూనికేషన్ కోచ్. ఈరోజు మనం ఏమి అభ్యాసం చేద్దాం?",
    "ml": "നമസ്കാരം! ഞാൻ വാണി, നിങ്ങളുടെ AI കമ്മ്യൂണിക്കേഷൻ കോച്ച്. ഇന്ന് നമ്മൾ എന്ത് പരിശീലിക്കണം?",
    "bn": "নমস্কার! আমি বাণী, আপনার AI যোগাযোগ কোচ। আজ আমরা কী অনুশীলন করব?",
    "mr": "नमस्कार! मी वाणी, तुमचा AI संवाद प्रशिक्षक. आज आपण काय सराव करूया?",
    "en": "Hello! I'm Vani, your AI communication coach. What shall we practice today?",
}


def get_language_name(code: str) -> str:
    return LANGUAGE_MAP.get(code, {}).get("name", "Unknown")


def get_greeting(language_code: str) -> str:
    return GREETINGS.get(language_code, GREETINGS["en"])


def is_supported_language(code: str) -> bool:
    return code in LANGUAGE_MAP


def get_whisper_code(language_code: str) -> str:
    return LANGUAGE_MAP.get(language_code, {}).get("whisper_code", "en")