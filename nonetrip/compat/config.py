from datetime import timedelta
from typing import Any, Dict, Optional, Pattern, Set, Union

from nonebot.config import BaseConfig
from pydantic import Extra

from nonetrip.typing import Expression_T


class DefaultConfig(BaseConfig):

    class Config:
        extra = Extra.allow

    DEBUG: bool = True

    SUPERUSERS: Set[int] = set()
    NICKNAME: Union[str, Set[str]] = ""

    COMMAND_START: Set[Union[str, Pattern]] = {"/", "!", "／", "！"}
    COMMAND_SEP: Set[Union[str, Pattern]] = {"/", "."}

    SESSION_EXPIRE_TIMEOUT: Optional[timedelta] = timedelta(minutes=5)
    SESSION_RUN_TIMEOUT: Optional[timedelta] = None
    SESSION_RUNNING_EXPRESSION: Expression_T = "您有命令正在执行，请稍后再试"

    SHORT_MESSAGE_MAX_LENGTH: int = 50

    DEFAULT_VALIDATION_FAILURE_EXPRESSION: Expression_T = "您的输入不符合要求，请重新输入"
    MAX_VALIDATION_FAILURES: int = 3
    TOO_MANY_VALIDATION_FAILURES_EXPRESSION: Expression_T = "您输入错误太多次啦，如需重试，请重新触发本功能"

    SESSION_CANCEL_EXPRESSION: Expression_T = "好的"

    APSCHEDULER_CONFIG: Dict[str, Any] = {
        "apscheduler.timezone": "Asia/Shanghai"
    }
