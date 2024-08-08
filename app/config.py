import os

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
base_url = os.getenv("BASE_URL", "http://localhost:8000")
max_text_length = int(os.getenv("MAX_TEXT_LENGTH", 50000))