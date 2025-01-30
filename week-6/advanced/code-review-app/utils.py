import logging
import os
from datetime import datetime

# 로그 설정
log_file = os.path.join(os.path.dirname(__file__), "debug.log")
logging.basicConfig(filename=log_file, level=logging.DEBUG, format="[LOG] %(asctime)s | %(filename)s | %(funcName)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def log_message(message):
    """디버깅 로그 남기기"""
    logging.debug(message)
    print(f"[LOG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {message}")