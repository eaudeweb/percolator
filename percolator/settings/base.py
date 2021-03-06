import os
from pathlib import Path


def get_env_var(var_name, default=None):
    var = os.getenv(var_name, default)
    if var is None and default is None:
        raise RuntimeError(f'Set the {var_name} environment variable')

    return var


def get_bool_env_var(var_name, default=None):
    var = get_env_var(var_name, default)
    return var.lower() == 'yes'


def get_int_env_var(var_name, default=None):
    var = get_env_var(var_name, default)
    try:
        return int(var)

    except ValueError:
        raise RuntimeError(
            f'Environment variable {var_name} '
            f'must be an integer or integer-convertible string'
        )


def get_float_env_var(var_name, default=None):
    var = get_env_var(var_name, default)
    try:
        return float(var)

    except ValueError:
        raise RuntimeError(
            f'Environment variable {var_name} '
            f'must be a float or float-convertible string'
        )


def split_env_var(var_name, sep=','):
    var = get_env_var(var_name)
    return [e.strip() for e in var.split(sep)]


DEBUG = False

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
TEMPLATES_DIR = (BASE_DIR / 'templates').as_posix()  # Jinja can't handle PosixPath objects
STATIC_DIR = ROOT_DIR / 'static'

ELASTICSEARCH_HOSTS = split_env_var('ELASTICSEARCH_HOSTS')

TIKA_HOST = get_env_var('TIKA_HOST')
TIKA_PORT = get_int_env_var('TIKA_PORT', 9998)
TIKA_URL = f'http://{TIKA_HOST}:{TIKA_PORT}'
TIKA_TIMEOUT = get_float_env_var('TIKA_TIMEOUT', 10)
