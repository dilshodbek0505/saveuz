"""
Сервис перевода текста для админки (ручной ввод товара).
Использует deep-translator: MyMemory (бесплатно, без ключа) с fallback на Google.
Языки: uz, ru, en (соответствуют modeltranslation).
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Соответствие наших кодов языков кодам deep-translator / ISO
LANG_MAP = {
    "uz": "uz",   # MyMemory/Google
    "ru": "ru",
    "en": "en",
}


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[str]:
    """
    Переводит текст из source_lang в target_lang.
    Возвращает переведённую строку или None при ошибке.
    """
    if not (text or text.strip()):
        return ""
    text = text.strip()
    if source_lang == target_lang:
        return text

    src = LANG_MAP.get(source_lang, source_lang)
    tgt = LANG_MAP.get(target_lang, target_lang)
    if src == tgt:
        return text

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source=src, target=tgt)
        return translator.translate(text)
    except Exception as e1:
        logger.warning("GoogleTranslator failed: %s", e1)
        try:
            from deep_translator import MyMemoryTranslator
            translator = MyMemoryTranslator(source=src, target=tgt)
            return translator.translate(text)
        except Exception as e2:
            logger.warning("MyMemoryTranslator failed: %s", e2)
            return None
    return None


def translate_to_all_languages(
    text: str,
    source_lang: str,
) -> dict[str, str]:
    """
    Возвращает словарь { "uz": "...", "ru": "...", "en": "..." }.
    В source_lang подставляется исходный text, остальные — перевод.
    """
    result = {lang: "" for lang in LANG_MAP}
    if not (text or text.strip()):
        return result
    result[source_lang] = text.strip()
    for target in LANG_MAP:
        if target == source_lang:
            continue
        translated = translate_text(text, source_lang, target)
        result[target] = translated if translated is not None else ""
    return result
