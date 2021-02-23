import asyncio
from functools import partial
from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar

from nonebot import get_app, get_asgi, get_bots, get_driver
from nonebot.adapters.cqhttp import Bot as CQBot
from nonebot.adapters.cqhttp.event import Event as NoneBotEvent
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.adapters.cqhttp.message import Message as NoneBotMessage
from nonebot.exception import ApiNotAvailable
from nonebot.matcher import Matcher
from singledispatchmethod import singledispatchmethod

from nonetrip.typing import Message_T

from .message import Message, MessageSegment

_AsyncCallable_T = TypeVar("_AsyncCallable_T", bound=Callable[..., Coroutine])
_HandlerDecorator = Callable[[_AsyncCallable_T], _AsyncCallable_T]
_NoneBotHandler = Callable[[CQBot, NoneBotEvent], Coroutine]


class Event(dict):
    """
    封装从 CQHTTP 收到的事件数据对象（字典），提供属性以获取其中的字段。
    除 `type` 和 `detail_type` 属性对于任何事件都有效外，其它属性存在与否（不存在则返回
    `None`）依事件不同而不同。
    """

    @classmethod
    def from_payload(cls, payload: NoneBotEvent) -> "Event":
        """
        从 CQHTTP 事件数据构造 `Event` 对象。
        """
        payload_dict = payload.dict()
        if isinstance(payload, MessageEvent):
            payload_dict["message"] = Message([
                MessageSegment(type_=segment.type, data=segment.data)
                for segment in payload.message
            ])
        return cls(payload_dict)

    @property
    def type(self) -> str:
        """
        事件类型，有 ``message``、``notice``、``request``、``meta_event`` 等。
        """
        return self["post_type"]

    @property
    def detail_type(self) -> str:
        """
        事件具体类型，依 `type` 的不同而不同，以 ``message`` 类型为例，有
        ``private``、``group``、``discuss`` 等。
        """
        return self[f"{self.type}_type"]

    @property
    def sub_type(self) -> Optional[str]:
        """
        事件子类型，依 `detail_type` 不同而不同，以 ``message.private`` 为例，有
        ``friend``、``group``、``discuss``、``other`` 等。
        """
        return self.get("sub_type")

    @property
    def name(self):
        """
        事件名，对于有 `sub_type` 的事件，为 ``{type}.{detail_type}.{sub_type}``，否则为
        ``{type}.{detail_type}``。
        """
        n = self.type + "." + self.detail_type
        if self.sub_type:
            n += "." + self.sub_type
        return n

    self_id: int  # 机器人自身 ID
    user_id: Optional[int]  # 用户 ID
    operator_id: Optional[int]  # 操作者 ID
    group_id: Optional[int]  # 群 ID
    discuss_id: Optional[int]  # 讨论组 ID
    message_id: Optional[int]  # 消息 ID
    message: Optional[Message]  # 消息
    raw_message: Optional[str]  # 未经 CQHTTP 处理的原始消息
    sender: Optional[Dict[str, Any]]  # 消息发送者信息
    anonymous: Optional[Dict[str, Any]]  # 匿名信息
    file: Optional[Dict[str, Any]]  # 文件信息
    comment: Optional[str]  # 请求验证消息
    flag: Optional[str]  # 请求标识

    def copy(self):
        return Event(**self)

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setattr__(self, key, value) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return f"<Event, {super().__repr__()}>"


class CQHttp:
    message_matcher = Matcher.new("message")
    message_handlers = []

    notice_matcher = Matcher.new("notice")
    notice_handlers = []

    request_matcher = Matcher.new("request")
    request_handlers = []

    metaevent_matcher = Matcher.new("meta_event")
    metaevent_handlers = []

    _loop: asyncio.AbstractEventLoop

    @staticmethod
    async def _run_handlers(handlers: List[_NoneBotHandler], bot: CQBot,
                            event: NoneBotEvent):
        asyncio.ensure_future(
            asyncio.gather(
                *map(lambda f: f(bot, event), handlers),  # type: ignore
                return_exceptions=True))

    def __init__(self):
        get_driver().on_startup(
            lambda: setattr(self, "_loop", asyncio.get_running_loop()))

        @self.message_matcher.handle()
        async def handle_message(bot: CQBot, event: NoneBotEvent):
            return await self._run_handlers(self.message_handlers, bot, event)

        @self.notice_matcher.handle()
        async def handle_notice(bot: CQBot, event: NoneBotEvent):
            return await self._run_handlers(self.notice_handlers, bot, event)

        @self.request_matcher.handle()
        async def handle_request(bot: CQBot, event: NoneBotEvent):
            return await self._run_handlers(self.request_handlers, bot, event)

        @self.metaevent_matcher.handle()
        async def handle_metaevent(bot: CQBot, event: NoneBotEvent):
            return await self._run_handlers(self.metaevent_handlers, bot, event)

    @property
    def asgi(self):
        return get_asgi()

    @property
    def server_app(self):
        return get_app()

    @property
    def logger(self):
        from nonetrip.log import logger

        return logger

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        assert isinstance(self._loop, asyncio.AbstractEventLoop)
        return self._loop

    @property
    def bot(self) -> CQBot:
        for bot in get_bots().values():
            if not isinstance(bot, CQBot):
                continue
            return bot
        raise ApiNotAvailable("nonetrip")

    def _handler_factory(
        self,
        function: Callable[[Event], Coroutine],
        post_type: Optional[str] = None,
    ) -> _NoneBotHandler:

        async def handler(bot: CQBot, event: NoneBotEvent):
            if post_type is not None and event.post_type != post_type:
                return
            nonebot_event = Event.from_payload(event)
            if nonebot_event is None:
                return
            return await function(nonebot_event)

        return handler

    @singledispatchmethod
    def on_message(self, arg: _AsyncCallable_T) -> _AsyncCallable_T:
        self.message_matcher.append_handler(self._handler_factory(arg))
        return arg

    @on_message.register  # type:ignore
    def _on_specified_message(self, arg: str) -> _HandlerDecorator:

        def wrapper(function: _AsyncCallable_T) -> _AsyncCallable_T:
            self.message_matcher.append_handler(
                self._handler_factory(function, arg))
            return function

        return wrapper

    @singledispatchmethod
    def on_notice(self, arg):
        self.notice_matcher.append_handler(self._handler_factory(arg))
        return arg

    @on_notice.register  # type: ignore
    def _on_specified_notice(self, arg: str) -> _HandlerDecorator:

        def wrapper(function: _AsyncCallable_T) -> _AsyncCallable_T:
            self.notice_matcher.append_handler(
                self._handler_factory(function, arg))
            return function

        return wrapper

    @singledispatchmethod
    def on_request(self, arg: _AsyncCallable_T) -> _AsyncCallable_T:
        self.request_matcher.append_handler(self._handler_factory(arg))
        return arg

    @on_request.register  # type: ignore
    def _on_specified_request(self, arg: str) -> _HandlerDecorator:

        def wrapper(function: _AsyncCallable_T) -> _AsyncCallable_T:
            self.request_matcher.append_handler(
                self._handler_factory(function, arg))
            return function

        return wrapper

    @singledispatchmethod
    def on_metaevent(self, arg: _AsyncCallable_T) -> _AsyncCallable_T:
        self.metaevent_matcher.append_handler(self._handler_factory(arg))
        return arg

    @on_metaevent.register  # type:ignore
    def _on_specified_metaevent(self, arg: str) -> _HandlerDecorator:

        def wrapper(function: _AsyncCallable_T) -> _AsyncCallable_T:
            self.metaevent_matcher.append_handler(
                self._handler_factory(function, arg))
            return function

        return wrapper

    on_meta_event = on_metaevent

    async def send(self, event: Event, message: "Message_T", **kwargs):
        bot = get_bots().get(str(event.self_id))
        assert (bot is not None) and isinstance(bot, CQBot)
        message = message if isinstance(message, Message) else Message(message)
        return await bot.send(NoneBotEvent(**event), NoneBotMessage(message),
                              **kwargs)

    async def call_action(self, action: str, **kwargs):
        return await self.bot.call_api(action, **kwargs)

    def __getattr__(self, key: str) -> Callable[..., Coroutine]:
        return partial(self.call_action, key)
