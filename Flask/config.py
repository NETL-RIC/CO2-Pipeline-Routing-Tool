import os
from dotenv import load_dotenv

if os.getenv("FLASK_ENV") == 'development':
  load_dotenv

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY')
  if not SECRET_KEY:
    raise ValueError('No SECRET_KEY set, check environment variables if in prod, or .env if in dev')
  SESSION_PERMANENT = False
  SCHEDULER_API_ENABLED = True