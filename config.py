# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv()
mode = os.getenv('FLASK_ENV')


class CConfig(object):
    PROJECT_NAME = os.getenv('PROJECT_NAME')
    SERVER_NAME = os.getenv('SERVER_NAME')
    SECRET_KEY = os.getenv('SECRET_KEY')
    CACHE_TYPE = os.getenv('CACHE_TYPE')
    #CAPTCHA_CONFIG = os.getenv('CAPTCHA_CONFIG')
    HOST = f"""{os.getenv('PROTOCOL')}://{SERVER_NAME}"""
    CSRF_SECRET_KEY = os.getenv('SECRET_KEY')
    CACHE_DEFAULT_TIMEOUT= 300
