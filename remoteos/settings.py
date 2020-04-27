"""
Django settings for remoteOs project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this explorer, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '50-1x52$)7uad8l&8vtx^w8tjz=qs2w^u)l(5mkul3lme(i99k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'media',
    'explorer',
    'user'
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

ROOT_URLCONF = 'remoteos.urls'

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

WSGI_APPLICATION = 'remoteos.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'remoteos',
        'USER': 'root',
        'PASSWORD': 'admin',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 指定django认证系统使用的模型类
AUTH_USER_MODEL = 'user.User'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# smtp service address and port
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# sender's address
EMAIL_HOST_USER = 'zhangjie89722@163.com'
# email's author code
EMAIL_HOST_PASSWORD = 'python89722'
# 收件人看到的发件人信息
EMAIL_FROM = '张洁<zhangjie89722@163.com>'

VLC_CACHE_PATH = "/home/zjay/.vlc-cache/"
VLC_SOCK_FILE = "vlc.sock"
VLC_SOCK_PATH = VLC_CACHE_PATH + VLC_SOCK_FILE

VLC_PLAYING_FILE = "playing_index"
VLC_PLAYING_PATH = VLC_CACHE_PATH + VLC_PLAYING_FILE

DISK_PATH = "/media/zjay/Datas"

DEVICE_UUID = "toshiba"

PUBLIC_DOMAIN = "huiwanit.cn"

# Django cache settings
CACHES = {
    'default': {
        'BACKEND': "django_redis.cache.RedisCache",
        'LOCATION': "redis://127.0.0.1:6379/2",
        'OPTIONS': {
            'CLIENT_CLASS': "django_redis.client.DefaultClient",
        }
    }
}

# config sessions store
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = 'default'

LOGIN_URL = "/user/login"

# ############################################################
# 网络视频搜索相关配置
ONLINE_VIDEO_REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",
}

# 速影
# ONLINE_VIDEO_BASE_URL = "https://xn--94qq85au3qyvbe13c.xyz"
# ONLINE_VIDEO_SEARCH_URL = "/index.php?m=vod-search"

# 牛牛TV
ONLINE_VIDEO_BASE_URL = "http://ziliao6.com"
ONLINE_VIDEO_SEARCH_URL = "/tv/api.php?do={}&v={}"
# ###########################################################

