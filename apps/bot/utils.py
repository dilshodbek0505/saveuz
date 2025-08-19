import uuid
from django.core.cache import cache

def generate_deep_link(base_url: str) -> str:
    unique_id = str(uuid.uuid4())
    return f"{base_url}?start={unique_id}", unique_id

def set_verification_code(phone: str, code: str, ttl: int = 300):
    cache.set(f"verify:{phone}", code, ttl)

def get_verification_code(phone: str) -> str | None:
    return cache.get(f"verify:{phone}")

def clear_verification_code(phone: str):
    cache.delete(f"verify:{phone}")

