from configparser import ConfigParser
from pathlib import Path


class ConfigReader:
    _config = None

    @classmethod
    def load_config(cls):
        if cls._config is None:
            config_path = Path(__file__).resolve().parent / "config.ini"
            parser = ConfigParser()
            parser.read(config_path)
            cls._config = parser
        return cls._config

    @classmethod
    def get(cls, section, option, fallback=None):
        config = cls.load_config()
        return config.get(section, option, fallback=fallback)

    @classmethod
    def getboolean(cls, section, option, fallback=False):
        config = cls.load_config()
        return config.getboolean(section, option, fallback=fallback)

    @classmethod
    def getint(cls, section, option, fallback=0):
        config = cls.load_config()
        return config.getint(section, option, fallback=fallback)

