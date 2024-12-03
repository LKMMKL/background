"""
Django settings for peanutai project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

import dashscope
from django.conf import settings
from langchain_openai import AzureChatOpenAI
import mongoengine

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '))a#z2+h9avji%*t)09o@_8&-ya5cgtk+s$zq!c%%0%28@7&3s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["192.168.110.10", "0.0.0.0", '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rag',
    'chat',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'peanutai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'peanutai.wsgi.application'

ASGI_APPLICATION = 'peanutai.asgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'data',  # 要使用的数据库名
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
                'host': '219.135.168.178',
                'port': 56980,
                'username': 'chuangdata',
                'password': 'Hjklzxc0505',
                'authSource': 'admin'
            }
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'


#azure
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = "dfd5d971667d4790aad0785d5d0b2765"
os.environ["AZURE_OPENAI_ENDPOINT"] = "http://api.wlai.vip"
os.environ['DUBO_USE_SELECTOR_EVENTLOOP'] = '1'
#通义千问
dashscope.api_key = 'sk-f21bb011a0fa475c96daec36fe597046'

#mongodb
mongoengine.connect(host="mongodb://chuangdata:Hjklzxc0505@219.135.168.178:56980/data?authSource=admin")

#gpt
DEPLOYE_NAME = 'gpt-4o-p'
OPENAI_API_VERSION = '2024-02-15-preview'
AZURE_ENDPOINT = 'https://peanut-gpt4o.openai.azure.com/'

#milvus
MILVUS_URL = 'http://219.135.168.178:56985/data'
MILVUS_COLLECTION_NAME = 'doc_slice256_qwen_v31024'
