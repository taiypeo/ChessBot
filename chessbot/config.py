import os
import datetime

TOKEN = os.environ.get("TOKEN")
DB_PATH = os.environ.get("DB_PATH")

EXPIRATION_TIMEDELTA = datetime.timedelta(days=7)
