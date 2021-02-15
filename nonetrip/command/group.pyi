from datetime import timedelta
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Type, Union

from nonetrip.command import CommandSession
from nonetrip.typing import CommandHandler_T, CommandName_T, Patterns_T


class CommandGroup:
    basename: Tuple[str]
    base_kwargs: Dict[str, Any]

    def __init__(self,
                 name: Union[str, CommandName_T],
                 *,
                 permission: int = ...,
                 only_to_me: bool = ...,
                 privileged: bool = ...,
                 shell_like: bool = ...,
                 expire_timeout: Optional[timedelta] = ...,
                 run_timeout: Optional[timedelta] = ...,
                 session_class: Optional[Type[CommandSession]] = ...):
        ...

    def command(
        self,
        name: Union[str, CommandName_T],
        *,
        aliases: Union[Iterable[str], str] = ...,
        patterns: Patterns_T = ...,
        permission: int = ...,
        only_to_me: bool = ...,
        privileged: bool = ...,
        shell_like: bool = ...,
        expire_timeout: Optional[timedelta] = ...,
        run_timeout: Optional[timedelta] = ...,
        session_class: Optional[Type[CommandSession]] = ...
    ) -> Callable[[CommandHandler_T], CommandHandler_T]:
        ...
