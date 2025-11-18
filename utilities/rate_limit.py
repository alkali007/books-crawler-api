from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
RATE_LIMIT = os.getenv("RATE_LIMIT", "100")

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT}/hour"])

