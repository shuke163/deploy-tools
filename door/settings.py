"""
Django settings for door backend project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import datetime
from config import config
from datetime import timedelta
from celery.schedules import crontab, crontab_parser

# from apps.core.loggers import JsonFormatter

# import pymysql

# pymysql.version_info = (1, 3, 13, "final", 0)
# pymysql.install_as_MySQLdb()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qz$l8ai0z101@rfjofwc6i9hijrr76+-6p-no)6-3=)e2tt#f)'

# SECURITY WARNING: don't run with debug turned on in production!
env = os.getenv("env", "dev")
ENV = env
APP = config[env]().APP

# project info
PROJECT_DICT = config[env]().PROJECT

OS_VERSION = "CentOS 7.2"

DEBUG = config[env]().DEBUG if config[env]().DEBUG else False

ALLOWED_HOSTS = ["*"]

LOCAL_HOSTS = "127.0.0.1"

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    # 'rest_framework_swagger',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'apps.account',
    'apps.dashboard',
    'apps.deploy',
    'apps.host',
]

MIDDLEWARE = [
    'apps.middleware.SessionMiddleware.ClearSessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'door.urls'

# Application definition
AUTH_USER_MODEL = 'account.Account'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'door.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    # 'account': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': config[env]().mysql["db"],
    #     'USER': config[env]().mysql["user"],
    #     'PASWORD': config[env]().mysql["password"],
    #     'HOST': config[env]().mysql["host"],
    #     'PORT': config[env]().mysql["port"],
    #     'OPTIONS': {
    #         'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    #     },
    # }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # cache保存

SESSION_COOKIE_NAME = "DoorId"  # Session的cookie保存在浏览器上时的key，即：sessionid＝随机字符串（默认）
SESSION_COOKIE_PATH = "/"  # Session的cookie保存的路径（默认）
SESSION_COOKIE_DOMAIN = None  # Session的cookie保存的域名（默认）
SESSION_COOKIE_SECURE = False  # 是否Https传输cookie（默认）
SESSION_COOKIE_HTTPONLY = True  # 是否Session的cookie只支持http传输（默认）
SESSION_COOKIE_AGE = 1209600  # Session的cookie失效日期（2周）（默认）
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 是否关闭浏览器使得Session过期（默认）
SESSION_SAVE_EVERY_REQUEST = True  # 是否每次请求都保存Session，默认修改之后才保存（默认）
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None

CELERY = {
    'CELERY_RESULT_BACKEND_URL': 'redis://:{password}@{host}:{port}/{db}'.format(
        password=config[env]().redis["password"],
        host=config[env]().redis["host"],
        port=config[env]().redis["port"],
        db=config[env]().redis["db"]
    ),
    'CELERY_BROKER_URL': 'redis://:{password}@{host}:{port}/{db}'.format(
        password=config[env]().redis["password"],
        host=config[env]().redis["host"],
        port=config[env]().redis["port"],
        db=config[env]().redis["db"]
    ),
    'CELERYD_HIJACK_ROOT_LOGGER': False,
    'CELERY_TIMEZONE': 'Asia/Shanghai',
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

REST_FRAMEWORK = {
    #'DEFAULT_AUTHENTICATION_CLASSES': (
    #    'rest_framework.authentication.BasicAuthentication',
    #    'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    #),
    #'DEFAULT_PERMISSION_CLASSES': [
    #    'rest_framework.permissions.IsAuthenticated',
    #],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'EXCEPTION_HANDLER': 'apps.core.exceptions.core_exception_handler',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'VERSION_PARAM': "version",
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    'PAGE_SIZE': 10,
}

# swagger
SWAGGER_SETTINGS = {
    "LOGOUT_URL": 'rest_framework:logout',
    "LOGIN_URL": 'rest_framework:login',
    'DEFAULT_INFO': 'door.urls.swagger_info',
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'SHOW_REQUEST_HEADERS': True,
    'JSON_EDITOR': True,
    'APIS_SORTER': 'alpha',
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
    'OPERATIONS_SORTER': 'alpha'
}

# jwt setting
JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=12000),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}

# 跨域设置
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)

SUPERVISOR = {
    "port": 8900,
    "username": "rcloud",
    "password": "rongcloud@2020"
}

PUSH_ADDRESS = {
    "APPLE": ["gateway.sandbox.push.apple.com:2195", "gateway.push.apple.com:2195",
              "feedback.sandbox.push.apple.com:2196", "feedback.push.apple.com:2196",
              "api.development.push.apple.com:443", "api.push.apple.com:443"],
    "XIAOMI": ["api.xmpush.xiaomi.com:443", ],
    "HUAWEI": ["api.push.hicloud.com:443", "api.vmall.com:443", "login.vmall.com:443", "push-api.cloud.huawei.com:443"],
    "OPPO": ["api.push.oppomobile.com:443"],
    "VIVO": ["api-push.vivo.com.cn:443"],
    "MEIZU": ["server-api-push.meizu.com:80","server-api-push.meizu.com:443"]
}

DEFAULT_ACCOUNT = {
    "username": "admin",
    "password": "beRcnLADAJdsycZKrdKseR8d"
}

DEFAULT_BUSINESS = "RCX"

RCDB_DICT = {
    "START_PORT": 8888,
    "RCDB_NUM_KEY": "RCDB_NUM",
    "RCDB_GROUP_NAME": "rcx_rcdb"
}

ANSIBLE = {
    "ANSIBLE_USER": "root",
    "INVENTORY_PATH": os.path.join(BASE_DIR, "apps/playbook/inventory"),
    "ANSIBLE_ROLE_PATH": os.path.join(BASE_DIR, "apps/playbook/roles"),
    "MYSQL_GROUP_NAME": "mysql",
    "MYSQL_SLAVE_SERVER_NAME": "rcx_mysql_slave",
    "ANSIBLE_LOF_FILE": os.path.join(BASE_DIR, "logs/ansible-playbook.log")
}

# LOG
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 'json': {
        #     '()': JsonFormatter,
        # },
        'standard': {
            'format': '[%(asctime)s] [%(threadName)s:%(thread)d] [task_id:%(name)s] [%(filename)s: %(lineno)d] [%(levelname)s]: %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - [%(pathname)s] - [%(filename)s: %(lineno)d] - %(message)s'
        },
    },
    # filter
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        # 'kafka': {
        #     'level': 'INFO',
        #     'class': 'apps.core.loggers.KafkaLoggingHandler',
        #     'brokers': config[env]().kafka['brokers'][0],
        #     'topic': config[env]().kafka['topic'],
        #     'formatter': 'json',
        #     'encoding': 'utf-8',
        #     'when': 'midnight',
        # },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "door.info.log"),
            # 'maxBytes': 1024 * 1024 * 50,
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
            'when': 'midnight',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "door.error.log"),
            # 'maxBytes': 1024 * 1024 * 50,
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'door': {
            'handlers': ['info', 'error', 'console', ],
            'level': 'INFO',
            'propagate': False,
        },
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG' if DEBUG else 'INFO',
        # },  # 显示SQL
        'celery': {
            'handlers': ['info', ],
            'level': 'INFO',
            'propagate': True,  # 向更高级别的logger传递
        },
        'django.server': {
            'handlers': ['django.server', 'console', ],
            'level': 'INFO',
            'propagate': True,
        }
    }
}
