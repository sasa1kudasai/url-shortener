import hashids
from user_agents import parse as parse_user_agent

from app.config import settings

hashids_instance = hashids.Hashids(salt=settings.hashids_salt, min_length=6)


def encode_id(number: int) -> str:
    return hashids_instance.encode(number)


def decode_id(code: str) -> int | None:
    decoded = hashids_instance.decode(code)
    return decoded[0] if decoded else None


def classify_device(user_agent_string: str | None) -> str:
    if not user_agent_string:
        return "unknown"

    ua = parse_user_agent(user_agent_string)

    if ua.is_bot:
        return "bot"
    elif ua.is_mobile:
        return "mobile"
    elif ua.is_tablet:
        return "tablet"
    elif ua.is_pc:
        return "desktop"
    else:
        return "other"