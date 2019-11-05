"""
Django settings for new project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import requests
from traceback import format_exc

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(BASE_DIR, 'archive_files')
HANDOFF_DIR = os.path.join(BASE_DIR, 'handoff_files')

if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)
if not os.path.exists(HANDOFF_DIR):
    os.makedirs(HANDOFF_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e65b$ogdiung0b+e@&upfr8%f@e_k1f^k0#synw&kmkhmzcavc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storage'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloud.urls'

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

WSGI_APPLICATION = 'cloud.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

from .conf import *

def sendAlive():
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'alive/')
        try:
            requests.post(addr, data={'node': NODE_NAME})
        except Exception:
            print(format_exc())

sendAlive()

import json
import datetime
from threading import Timer
from cloud.settings import NODE_NAME,NODE_ADDRESS

GOSSIP_LIST = []
t_gossip = 0.5

for i in AVAILABLE_NODES:
    GOSSIP_LIST.append({'name':i['name'],'address':i['address'],'HB':0,'last_modified':datetime.datetime.now().timestamp()})
GOSSIP_LIST.append({'name':NODE_NAME,'address':NODE_ADDRESS,'HB':0,'last_modified':datetime.datetime.now().timestamp()})


def gossip():
    Timer(t_gossip,gossip).start()
    GOSSIP_LIST[-1]['HB'] += 1
    GOSSIP_LIST[-1]['last_modified'] = datetime.datetime.now().timestamp()
    addr1 = os.path.join(GOSSIP_LIST[0]['address'], 'gossip/')
    addr2 = os.path.join(GOSSIP_LIST[1]['address'], 'gossip/')
    data = json.dumps(GOSSIP_LIST)
    try:
        r = requests.post(addr1, data=data)
    except:
        print('Gossip failed for ' + addr1)
    try:
        r = requests.post(addr2, data=data)
    except:
        print('Gossip failed for ' + addr2)
    
gossip()
    
    





