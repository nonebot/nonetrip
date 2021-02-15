from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, Iterable,
                    List, Optional, Pattern, Sequence, Tuple, Union)

if TYPE_CHECKING:
    from nonetrip import NoneBot
    from nonetrip.command import CommandSession
    from nonetrip.compat import Event as CQEvent
    from nonetrip.natural_language import IntentCommand, NLPSession
    from nonetrip.notice_request import NoticeSession, RequestSession
    from nonetrip.plugin import PluginManager

Context_T = Dict[str, Any]
Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]]]
Expression_T = Union[str, Sequence[str], Callable[..., str]]
CommandName_T = Tuple[str, ...]
CommandArgs_T = Dict[str, Any]
CommandHandler_T = Callable[["CommandSession"], Awaitable[Any]]
Patterns_T = Union[Iterable[str], str, Iterable[Pattern[str]], Pattern[str]]
State_T = Dict[str, Any]
Filter_T = Callable[[Any], Union[Any, Awaitable[Any]]]
PermChecker_T = Callable[["NoneBot", "CQEvent"], Awaitable[bool]]
NLPHandler_T = Callable[["NLPSession"], Awaitable[Optional["IntentCommand"]]]
NoticeHandler_T = Callable[["NoticeSession"], Awaitable[Any]]
RequestHandler_T = Callable[["RequestSession"], Awaitable[Any]]
MessagePreprocessor_T = Callable[["NoneBot", "CQEvent", "PluginManager"],
                                 Awaitable[Any]]

__all__ = [
    'Context_T',
    'Message_T',
    'Expression_T',
    'CommandName_T',
    'CommandArgs_T',
    'CommandHandler_T',
    'Patterns_T',
    'State_T',
    'Filter_T',
    'PermChecker_T',
]
