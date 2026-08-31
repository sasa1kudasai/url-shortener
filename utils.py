import random
import string

import hashids

import os
from dotenv import load_dotenv
from user_agents import parse as parse_user_agent

load_dotenv()

def generate_random_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

hashids = hashids.Hashids(salt=os.getenv("HASHIDS_SALT", "change-me-in-production"), min_length=6)

def encode_id(number: int) -> str:
    return hashids.encode(number)

def decode_id(code: str) -> int | None:
    decoded = hashids.decode(code)
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