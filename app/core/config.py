import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    MAX_QUERY_TIMEOUT = int(os.getenv("MAX_QUERY_TIMEOUT", "30"))
    MAX_RESULT_ROWS = int(os.getenv("MAX_RESULT_ROWS", "1000"))
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

config = Config() 