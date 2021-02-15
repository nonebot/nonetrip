"""
此模块提供事件总线相关类。
"""

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, DefaultDict, Iterable, List, Set

AsyncCallable = Callable[..., Coroutine]


async def parallel_run(functions: Iterable[AsyncCallable], *args, **kwargs):
    return await asyncio.gather(*map(lambda f: f(*args, **kwargs), functions))


class EventBus:

    def __init__(self):
        self._subscribers: DefaultDict[str,
                                       Set[AsyncCallable]] = defaultdict(set)
        self._hooks_before: DefaultDict[str,
                                        Set[AsyncCallable]] = defaultdict(set)

    def subscribe(self, event: str, func: Callable) -> None:
        self._subscribers[event].add(func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        if func in self._subscribers[event]:
            self._subscribers[event].remove(func)

    def hook_before(self, event: str, func: Callable) -> None:
        self._hooks_before[event].add(func)

    def unhook_before(self, event: str, func: Callable) -> None:
        if func in self._hooks_before[event]:
            self._hooks_before[event].remove(func)

    def on(self, event: str) -> Callable:

        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func)
            return func

        return decorator

    def before(self, event: str) -> Callable:

        def decorator(func: Callable) -> Callable:
            self.hook_before(event, func)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        event_copy = event

        while True:
            await parallel_run(self._hooks_before[event], *args, **kwargs)
            event, *sub_event = event.rsplit(".", maxsplit=1)
            if not sub_event:
                # the current event is the root event
                break
        event = event_copy

        results = []
        while True:
            results += await parallel_run(self._subscribers[event], *args,
                                          **kwargs)
            event, *sub_event = event.rsplit(".", maxsplit=1)
            if not sub_event:
                # the current event is the root event
                break
        return results
