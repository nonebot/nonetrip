import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

from nonebot import Config, get_driver

from nonetrip import default_config
from nonetrip.compat import CQHttp, DefaultConfig, Event, Message

from .log import logger
from .sched import Scheduler

if Scheduler:
    scheduler = Scheduler()
else:
    scheduler = None


class NoneBot(CQHttp):

    def __init__(self, config_object: Optional[Any] = None):
        super().__init__()

        nonebot_config: Config = get_driver().config
        config_object = config_object or default_config
        config_keys: List[str] = [
            key for key in {
                *dir(config_object),
                *map(lambda x: x.upper(),
                     nonebot_config.dict().keys()),
                *dir(default_config),
            } if key.isupper() and not key.startswith('_')
        ]
        config_dict: Dict[str, Any] = {}

        for key in config_keys:
            if hasattr(config_object, key):
                value = getattr(config_object, key)
            else:
                value = nonebot_config.dict().get(key)
            config_dict[key] = value

        self.config = DefaultConfig.parse_obj(config_dict)

        self.logger.setLevel(
            logging.DEBUG if self.config.DEBUG else logging.INFO)

        logger.debug(f"Loaded configurations: {config_dict}")

        self.config = config_object

        from .message import handle_message
        from .notice_request import handle_notice_or_request

        @self.on_message
        async def _(event: Event):  # type:ignore
            asyncio.create_task(handle_message(self, event))

        @self.on_notice
        async def _(event: Event):  # type: ignore
            asyncio.create_task(handle_notice_or_request(self, event))

        @self.on_request
        async def _(event: Event):  # type: ignore
            asyncio.create_task(handle_notice_or_request(self, event))


_bot: Optional[NoneBot] = None


def init(config_object: Optional[Any] = None,
         start_scheduler: bool = True) -> None:
    """
    Initialize NoneBot instance.

    This function must be called at the very beginning of code,
    otherwise the get_bot() function will return None and nothing
    will work properly.

    :param config_object: configuration object
    """
    global _bot
    _bot = NoneBot(config_object)

    if _bot.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if start_scheduler:
        on_startup(_start_scheduler)


async def _start_scheduler():
    if scheduler and not scheduler.running:
        scheduler.configure(_bot.config.APSCHEDULER_CONFIG)
        scheduler.start()
        logger.info('Scheduler started')


def get_bot() -> NoneBot:
    """
    Get the NoneBot instance.

    The result is ensured to be not None, otherwise an exception will
    be raised.

    :raise ValueError: instance not initialized
    """
    if _bot is None:
        raise ValueError('NoneBot instance has not been initialized')
    return _bot


def on_startup(func: Callable[[], Awaitable[None]]) \
        -> Callable[[], Awaitable[None]]:
    """
    Decorator to register a function as startup callback.
    """
    return get_driver().on_startup(func)


def on_websocket_connect(func: Callable[[Event], Awaitable[None]]) \
        -> Callable[[], Awaitable[None]]:
    """
    Decorator to register a function as websocket connect callback.

    Only work with CQHTTP v4.14+.
    """
    return get_bot().on_meta_event('lifecycle.connect')(func)  # type: ignore


from .command import CommandGroup, CommandSession
from .exceptions import CQHttpError
from .helpers import context_id
from .message import Message, MessageSegment, message_preprocessor  # noqa:F811
from .natural_language import IntentCommand, NLPResult, NLPSession
from .notice_request import NoticeSession, RequestSession
from .plugin import (get_loaded_plugins, load_builtin_plugins, load_plugin,
                     load_plugins, on_command, on_natural_language, on_notice,
                     on_request)

__all__ = [
    'NoneBot',
    'scheduler',
    'init',
    'get_bot',
    'on_startup',
    'on_websocket_connect',
    'CQHttpError',
    'load_plugin',
    'load_plugins',
    'load_builtin_plugins',
    'get_loaded_plugins',
    'message_preprocessor',
    'Message',
    'MessageSegment',
    'on_command',
    'CommandSession',
    'CommandGroup',
    'on_natural_language',
    'NLPSession',
    'NLPResult',
    'IntentCommand',
    'on_notice',
    'NoticeSession',
    'on_request',
    'RequestSession',
    'context_id',
]
