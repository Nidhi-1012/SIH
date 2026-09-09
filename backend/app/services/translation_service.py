from typing import Dict, Any

TRANSLATION_DICTIONARY = {
    "ROAD_BLOCKED": {
        "en": "Road Blocked due to Landslide. Rerouting active shipments.",
        "hi": "भूस्खलन के कारण मार्ग अवरुद्ध है। आपातकालीन वाहनों का मार्ग बदला जा रहा है।",
        "as": "ভূমিস্খলনৰ বাবে পথ অৱৰুদ্ধ হৈছে। জৰুৰী কালীন বাহন পুনঃপথ নিৰ্দেশ কৰা হৈছে।"
    },
    "HIGH_RISK": {
        "en": "Caution: High Landslide & Flash Flood Risk detected in district.",
        "hi": "सावधान: जिले में भारी भूस्खलन और बाढ़ का जोखिम पाया गया है।",
        "as": "সাতৰ্কতা: জিলাখনত প্ৰবল ভূমিস্খলন আৰু বানপানীৰ আশংকা ধৰা পৰিছে।"
    },
    "EMERGENCY_MODE": {
        "en": "EMERGENCY MODE ACTIVE: Priority P0 medical & relief corridors prioritized.",
        "hi": "आपातकालीन मोड सक्रिय: P0 चिकित्सा एवं राहत गलियारों को प्राथमिकता।",
        "as": "জৰুৰীকালীন অৱস্থা সক্ৰিয়: P0 চিকিৎসা আৰু সাহায্য পথক অগ্ৰাধিকাৰ দিয়া হৈছে।"
    }
}

def translate_alert(intent_key: str, lang: str = "en") -> str:
    """
    Translates safety alert intent into target language (en, hi, as).
    """
    lang_dict = TRANSLATION_DICTIONARY.get(intent_key, TRANSLATION_DICTIONARY["ROAD_BLOCKED"])
    return lang_dict.get(lang.lower(), lang_dict["en"])

def get_multilingual_alert_payload(intent_key: str) -> Dict[str, str]:
    """
    Returns dictionary with all 3 translations for an alert intent.
    """
    return TRANSLATION_DICTIONARY.get(intent_key, TRANSLATION_DICTIONARY["ROAD_BLOCKED"])
