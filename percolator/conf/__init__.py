"""
Module-based settings configuration, adopted and adapted from Django.
The settings module must be supplied in the `PERCOLATOR_SETTINGS_MODULE` environment variable.
Manual configuration of settings (like Django's `settings.configure()` is NOT supported.
"""
import importlib
import os

from . import default_settings
from .utils import LazyObject, empty
from percolator.core.exceptions import ConfigurationError


ENV_VAR = 'PERCOLATOR_SETTINGS_MODULE'


class LazySettings(LazyObject):

    def _setup(self, name=None):
        settings_module = os.environ.get(ENV_VAR)
        if not settings_module:
            desc = f'setting {name}' if name else 'settings'
            raise ConfigurationError(
                f'Requested {desc}, but settings are not configured. '
                f'You must define the environment variable {ENV_VAR}'
            )

        self._wrapped = Settings(settings_module)

    def __repr__(self):
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is empty:
            return '<LazySettings [Unevaluated]>'
        return f'<LazySettings "{self._wrapped.SETTINGS_MODULE}">'

    def __getattr__(self, name):
        """Return the value of a setting and cache it in self.__dict__."""
        if self._wrapped is empty:
            self._setup(name)
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        """
        Set the value of setting. Clear all cached values if _wrapped changes
        (@override_settings does this) or clear single values when set.
        """
        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """Delete a setting and clear it from cache if needed."""
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    @property
    def configured(self):
        """Return True if the settings have already been configured."""
        return self._wrapped is not object()


class Settings:
    def __init__(self, settings_module):
        for setting in dir(default_settings):
            if setting.isupper():
                setattr(self, setting, getattr(default_settings, setting))

        self.SETTINGS_MODULE = settings_module
        mod = importlib.import_module(self.SETTINGS_MODULE)

        tuple_settings = ()  # TODO : Populate this

        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if (setting in tuple_settings and
                        not isinstance(setting_value, (list, tuple))):
                    raise ConfigurationError(f'The {setting} setting must be a list or a tuple. ')
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def __getattr__(self, name):
        raise AttributeError(f'"{self.__class__.__name__}" object has no attribute "{name}"')

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.SETTINGS_MODULE}">'


settings = LazySettings()
