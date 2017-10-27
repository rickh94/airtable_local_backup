import better_exceptions


class DataCorruptionError(Exception):
    pass


class ConfigurationError(Exception):
    pass