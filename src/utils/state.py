from ..services.logger import SingletonLogger


class SingletonMeta(type):
    """A metaclass for creating singleton classes."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class State(metaclass=SingletonMeta):
    """Legacy State kept for compatibility. Prefer `app.state` and DI.

    `logger` is delegated to the SingletonLogger; model/tokenizer
    should be stored on `app.state` instead.
    """

    @property
    def logger(self):
        return SingletonLogger().get_logger()
